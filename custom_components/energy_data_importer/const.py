"""Constants for the Energy Data Importer integration."""

DOMAIN = "energy_data_importer"

# Service names
SERVICE_PREPARE_DATA = "prepare_data"
SERVICE_IMPORT_DATA = "import_data"

# Default directory structure
DEFAULT_BASE_PATH = "/config/data"
DEFAULT_ENERGY_CSV_PATH = "/config/data/energy/csv"
DEFAULT_RAW_PATH = "/config/data/imports/raw"
DEFAULT_PROCESSED_PATH = "/config/data/imports/processed"
DEFAULT_FAILED_PATH = "/config/data/imports/failed"

# Configuration keys
CONF_INSTANCE_NAME = "instance_name"
CONF_AUTO_BACKUP = "auto_backup"
CONF_DATA_SOURCE = "data_source"
CONF_INPUT_FILE = "input_file"
CONF_OUTPUT_PREFIX = "output_prefix"
CONF_DB_TYPE = "db_type"
CONF_SQLITE_DB = "sqlite_db"
CONF_MARIADB_HOST = "mariadb_host"
CONF_MARIADB_USER = "mariadb_user"
CONF_MARIADB_PASSWORD = "mariadb_password"
CONF_MARIADB_DATABASE = "mariadb_database"

# Default settings
DEFAULT_AUTO_BACKUP = True
BACKUP_DIR = "/config/data/imports/backups"

# Data sources (actual energy providers only - Template is for developers)
DATA_SOURCES = [
    "Ameren Electric",
    "Domoticz",
    "DSMR-reader",
    "E-REDES",
    "Eneco",
    "Enel Distribuzione",
    "EnergyControl",
    "Engie",
    "Enphase",
    "Fluvius",
    "GreenChoice",
    "Home Assistant",
    "HomeWizard",
    "iSolarCloud",
    "Liander",
    "MeterN",
    "Myenergi Zappi",
    "NEM12",
    "NextEnergy",
    "Oxxio",
    "P1mon",
    "Shelly EM3",
    "SlimmeMeterPortal",
    "SMA",
    "SolarEdge",
    "Solarman",
    "Solax",
    "United Power",
    "VanOns",
    "Xcel Energy",
    "Zonneplan",
]

# Database types
DB_TYPE_SQLITE = "sqlite"
DB_TYPE_MARIADB = "mariadb"

