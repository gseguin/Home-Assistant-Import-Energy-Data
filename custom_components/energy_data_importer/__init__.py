"""The Energy Data Importer integration."""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import (
    BACKUP_DIR,
    CONF_AUTO_BACKUP,
    CONF_DATA_SOURCE,
    CONF_DB_TYPE,
    CONF_INPUT_FILE,
    CONF_MARIADB_DATABASE,
    CONF_MARIADB_HOST,
    CONF_MARIADB_PASSWORD,
    CONF_MARIADB_USER,
    CONF_OUTPUT_PREFIX,
    CONF_SQLITE_DB,
    DB_TYPE_MARIADB,
    DB_TYPE_SQLITE,
    DEFAULT_AUTO_BACKUP,
    DEFAULT_ENERGY_CSV_PATH,
    DEFAULT_FAILED_PATH,
    DEFAULT_PROCESSED_PATH,
    DEFAULT_RAW_PATH,
    DOMAIN,
    SERVICE_IMPORT_DATA,
    SERVICE_PREPARE_DATA,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = []

# Service schemas
PREPARE_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DATA_SOURCE): cv.string,
        vol.Required(CONF_INPUT_FILE): cv.string,
        vol.Optional(CONF_OUTPUT_PREFIX, default=""): cv.string,
    }
)

IMPORT_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DB_TYPE): vol.In([DB_TYPE_SQLITE, DB_TYPE_MARIADB]),
        vol.Optional(CONF_SQLITE_DB): cv.string,
        vol.Optional(CONF_MARIADB_HOST, default="localhost"): cv.string,
        vol.Optional(CONF_MARIADB_USER): cv.string,
        vol.Optional(CONF_MARIADB_PASSWORD): cv.string,
        vol.Optional(CONF_MARIADB_DATABASE): cv.string,
        vol.Required(CONF_INPUT_FILE): cv.string,
        vol.Optional(CONF_AUTO_BACKUP, default=DEFAULT_AUTO_BACKUP): cv.boolean,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Energy Data Importer from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    # Create recommended directory structure (including backup directory)
    await _ensure_directories(hass)

    async def handle_prepare_data(call: ServiceCall) -> None:
        """Handle the prepare_data service call."""
        data_source = call.data[CONF_DATA_SOURCE]
        input_file = call.data[CONF_INPUT_FILE]
        output_prefix = call.data.get(CONF_OUTPUT_PREFIX, "")

        try:
            await _prepare_data(hass, data_source, input_file, output_prefix)
        except Exception as err:
            _LOGGER.exception("Error preparing data: %s", err)
            raise HomeAssistantError(f"Error preparing data: {err}") from err

    async def handle_import_data(call: ServiceCall) -> None:
        """Handle the import_data service call."""
        db_type = call.data[CONF_DB_TYPE]
        input_file = call.data[CONF_INPUT_FILE]
        auto_backup = call.data.get(CONF_AUTO_BACKUP, DEFAULT_AUTO_BACKUP)

        db_params: dict[str, Any] = {"db_type": db_type}

        if db_type == DB_TYPE_SQLITE:
            db_params[CONF_SQLITE_DB] = call.data.get(
                CONF_SQLITE_DB, hass.config.path("home-assistant_v2.db")
            )
        elif db_type == DB_TYPE_MARIADB:
            db_params[CONF_MARIADB_HOST] = call.data.get(CONF_MARIADB_HOST, "localhost")
            db_params[CONF_MARIADB_USER] = call.data[CONF_MARIADB_USER]
            db_params[CONF_MARIADB_PASSWORD] = call.data.get(CONF_MARIADB_PASSWORD, "")
            db_params[CONF_MARIADB_DATABASE] = call.data[CONF_MARIADB_DATABASE]

        try:
            # Create backup if enabled
            if auto_backup:
                await _backup_database(hass, db_params)
            
            await _import_data(hass, input_file, db_params)
        except Exception as err:
            _LOGGER.exception("Error importing data: %s", err)
            raise HomeAssistantError(f"Error importing data: {err}") from err

    hass.services.async_register(
        DOMAIN, SERVICE_PREPARE_DATA, handle_prepare_data, schema=PREPARE_DATA_SCHEMA
    )

    hass.services.async_register(
        DOMAIN, SERVICE_IMPORT_DATA, handle_import_data, schema=IMPORT_DATA_SCHEMA
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id)

    if not hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, SERVICE_PREPARE_DATA)
        hass.services.async_remove(DOMAIN, SERVICE_IMPORT_DATA)

    return True


async def _prepare_data(
    hass: HomeAssistant, data_source: str, input_file: str, output_prefix: str
) -> None:
    """Prepare data from a specific data source."""
    _LOGGER.info("Preparing data from %s: %s", data_source, input_file)

    # Get the integration path
    integration_path = Path(__file__).parent.parent.parent
    datasources_path = integration_path / "Datasources"

    # Map data source to the appropriate script
    data_source_map = {
        "Ameren Electric": "Ameren Electric/AmerenElectricDataPrepare.py",
        "Domoticz": "Domoticz/DomoticzDataPrepare.py",
        "DSMR-reader": "DSMR-reader/DSMR-readerDataPrepare.py",
        "E-REDES": "E-REDES/ERedesDataPrepare.py",
        "Eneco": "Eneco/EnecoDataPrepare.py",
        "Enel Distribuzione": "Enel Distribuzione/EnelDistribuzioneDataPrepare.py",
        "EnergyControl": "EnergyControl/EnergyControlDataPrepare.py",
        "Engie": "Engie/EngieDataPrepare.py",
        "Enphase": "Enphase/EnphaseDataPrepare.py",
        "Fluvius": "Fluvius/FluviusDataPrepare.py",
        "GreenChoice": "GreenChoice/GreenChoiceDataPrepare.py",
        "Home Assistant": "Home Assistant/HomeAssistantDataPrepare.py",
        "HomeWizard": "HomeWizard/HomeWizardDataPrepare.py",
        "iSolarCloud": "iSolarCloud/iSolarCloudDataPrepare.py",
        "Liander": "Liander/LianderDataPrepare.py",
        "MeterN": "MeterN/MeterNDataPrepare.py",
        "Myenergi Zappi": "Myenergi Zappi/MyenergiZappiDataPrepare.py",
        "NEM12": "NEM12/NEM12DataPrepare.py",
        "NextEnergy": "NextEnergy/NextEnergyDataPrepare.py",
        "Oxxio": "Oxxio/OxxioDataPrepare.py",
        "P1mon": "P1mon/P1MonDataPrepare.py",
        "Shelly EM3": "Shelly EM3/ShellyEM3DataPrepare.py",
        "SlimmeMeterPortal": "SlimmeMeterPortal/SlimmeMeterPortalDataPrepare.py",
        "SMA": "SMA/SMADataPrepare.py",
        "SolarEdge": "SolarEdge/SolarEdgeDataPrepare.py",
        "Solarman": "Solarman/SolarmanDataPrepare.py",
        "Solax": "Solax/SolaxDataPrepare.py",
        "United Power": "United Power/UnitedPowerDataPrepare.py",
        "VanOns": "VanOns/VanOnsDataPrepare.py",
        "Xcel Energy": "Xcel Energy/XcelEnergyDataPrepare.py",
        "Zonneplan": "Zonneplan/ZonneplanDataPrepare.py",
    }

    script_path = datasources_path / data_source_map.get(
        data_source, "TemplateDataPrepare.py"
    )

    if not script_path.exists():
        raise HomeAssistantError(
            f"Data preparation script not found for {data_source}: {script_path}"
        )

    # Add the Datasources directory to sys.path
    sys.path.insert(0, str(datasources_path))

    try:
        # Build command arguments
        cmd_args = ["-y", input_file]
        if output_prefix:
            cmd_args.insert(0, output_prefix)
            cmd_args.insert(0, "-p")

        # Run the preparation script in an executor
        await hass.async_add_executor_job(
            _run_prepare_script, str(script_path), cmd_args
        )

        _LOGGER.info("Data preparation completed successfully")
    finally:
        # Remove from sys.path
        if str(datasources_path) in sys.path:
            sys.path.remove(str(datasources_path))


def _run_prepare_script(script_path: str, args: list[str]) -> None:
    """Run a data preparation script synchronously."""
    import subprocess

    result = subprocess.run(
        [sys.executable, script_path] + args,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise HomeAssistantError(
            f"Data preparation script failed: {result.stderr or result.stdout}"
        )


async def _import_data(
    hass: HomeAssistant, input_file: str, db_params: dict[str, Any]
) -> None:
    """Import prepared data into Home Assistant database."""
    _LOGGER.info("Importing data from %s", input_file)

    # Get the integration path
    integration_path = Path(__file__).parent.parent.parent
    import_script = integration_path / "Datasources" / "ImportData.py"

    if not import_script.exists():
        raise HomeAssistantError(f"Import script not found: {import_script}")

    # Build command arguments
    cmd_args = [
        "--db-type",
        db_params["db_type"],
        "--csv-file",
        input_file,
        "--verbose",
    ]

    if db_params["db_type"] == DB_TYPE_SQLITE:
        cmd_args.extend(["--sqlite-db", db_params[CONF_SQLITE_DB]])
    elif db_params["db_type"] == DB_TYPE_MARIADB:
        cmd_args.extend(
            [
                "--host",
                db_params[CONF_MARIADB_HOST],
                "--user",
                db_params[CONF_MARIADB_USER],
                "--database",
                db_params[CONF_MARIADB_DATABASE],
            ]
        )
        if db_params.get(CONF_MARIADB_PASSWORD):
            cmd_args.extend(["--password", db_params[CONF_MARIADB_PASSWORD]])

    # Run the import script in an executor
    await hass.async_add_executor_job(_run_import_script, str(import_script), cmd_args)

    _LOGGER.info("Data import completed successfully")


def _run_import_script(script_path: str, args: list[str]) -> None:
    """Run the import script synchronously."""
    import subprocess

    result = subprocess.run(
        [sys.executable, script_path] + args,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise HomeAssistantError(
            f"Data import script failed: {result.stderr or result.stdout}"
        )


async def _ensure_directories(hass: HomeAssistant) -> None:
    """Ensure the recommended directory structure exists."""
    directories = [
        DEFAULT_ENERGY_CSV_PATH,
        DEFAULT_RAW_PATH,
        DEFAULT_PROCESSED_PATH,
        DEFAULT_FAILED_PATH,
        BACKUP_DIR,
    ]

    def create_dirs():
        for directory in directories:
            path = Path(directory)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                _LOGGER.info("Created directory: %s", directory)

    await hass.async_add_executor_job(create_dirs)


async def _backup_database(hass: HomeAssistant, db_params: dict[str, Any]) -> None:
    """Create a timestamped backup of the database before import."""
    import shutil
    from datetime import datetime

    db_type = db_params["db_type"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if db_type == DB_TYPE_SQLITE:
        db_path = Path(db_params[CONF_SQLITE_DB])
        if not db_path.exists():
            _LOGGER.warning("Database file not found, skipping backup: %s", db_path)
            return

        backup_filename = f"home-assistant_v2_{timestamp}.db"
        backup_path = Path(BACKUP_DIR) / backup_filename

        def do_backup():
            shutil.copy2(db_path, backup_path)
            _LOGGER.info("Database backed up to: %s", backup_path)
            
            # Clean up old backups (keep last 10)
            backup_dir = Path(BACKUP_DIR)
            backups = sorted(backup_dir.glob("home-assistant_v2_*.db"), key=lambda p: p.stat().st_mtime)
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    old_backup.unlink()
                    _LOGGER.info("Removed old backup: %s", old_backup.name)

        await hass.async_add_executor_job(do_backup)

    elif db_type == DB_TYPE_MARIADB:
        # For MariaDB, log a warning that manual backup is recommended
        _LOGGER.warning(
            "Automatic backup is not supported for MariaDB. "
            "Please ensure you have a recent backup of database '%s' before proceeding.",
            db_params[CONF_MARIADB_DATABASE]
        )

