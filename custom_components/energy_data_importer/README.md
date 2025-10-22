# Energy Data Importer - Home Assistant Custom Integration

This custom integration for Home Assistant allows you to import historical energy/water data from external data sources so that it can be used in the Energy Dashboard.

## Features

- Import historical energy, gas, and water data into Home Assistant
- Support for 30+ energy data sources including Eneco, Fluvius, SolarEdge, HomeWizard, and more
- Supports both SQLite (default) and MariaDB databases
- Service-based interface for easy automation
- Correctly handles high and low resolution data
- Supports sensor resets and dual tariffs
- Automatic directory structure creation for organized workflow

## Installation

### HACS (Recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed
2. Add this repository as a custom repository in HACS:
   - Open HACS
   - Go to "Integrations"
   - Click the three dots in the top right
   - Select "Custom repositories"
   - Add the repository URL and select "Integration" as the category
3. Click "Install"
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/energy_data_importer` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services
2. Click "+ Add Integration"
3. Search for "Energy Data Importer"
4. Enter a name for this instance (e.g., "Grid Energy", "Solar", "Gas")
5. Click "Submit"

**Multiple Instances**: You can add multiple instances to organize imports from different data sources. For example:

- "Grid Energy" for your main electricity meter
- "Solar" for solar panel data
- "Gas" for gas meter data
- "Water" for water meter data

Each instance uses the same services but can be identified in logs and managed separately.

The integration will automatically create the following directory structure in your Home Assistant config:

```
/config/
└── data/
    ├── energy/
    │   └── csv/          # Store your generated CSV files here
    │
    └── imports/
        ├── raw/          # Place raw data files from energy providers here
        ├── processed/    # Successfully processed files are moved here
        ├── failed/       # Failed imports are moved here for review
        └── backups/      # Automatic database backups (SQLite only)
```

## 🛡️ Safety Features

### Automatic Database Backup

**Enabled by default** - Before importing data, the integration automatically creates a timestamped backup of your SQLite database:

- Backups are stored in `/config/data/imports/backups/`
- Format: `home-assistant_v2_YYYYMMDD_HHMMSS.db`
- Keeps the last 10 backups automatically
- Can be disabled per import if needed (not recommended)

**Note:** Automatic backup is only available for SQLite. For MariaDB, please create manual backups before importing.

## Usage

This integration provides two services:

### 1. `energy_data_importer.prepare_data`

Prepare energy data from a specific data source for import.

**Example service call:**

```yaml
service: energy_data_importer.prepare_data
data:
  data_source: "Eneco"
  input_file: "/config/data/imports/raw/eneco_export.csv"
  output_prefix: "my_meter" # Optional
```

**Recommended workflow:**

1. Place raw data files in `/config/data/imports/raw/`
2. Run `prepare_data` service
3. Output files are created in the current directory (you can move them to `/config/data/energy/csv/`)

### 2. `energy_data_importer.import_data`

Import prepared CSV data into the Home Assistant database.

**Example service call (SQLite):**

```yaml
service: energy_data_importer.import_data
data:
  db_type: "sqlite"
  sqlite_db: "/config/home-assistant_v2.db"
  input_file: "/config/data/energy/csv/*_high_resolution.csv"
  auto_backup: true # Optional, enabled by default
```

**Recommended workflow:**

1. Ensure CSV files are in `/config/data/energy/csv/`
2. Run `import_data` service (automatic backup will be created)
3. Check logs for success/errors
4. If needed, restore from `/config/data/imports/backups/`

**Example service call (MariaDB):**

```yaml
service: energy_data_importer.import_data
data:
  db_type: "mariadb"
  mariadb_host: "localhost"
  mariadb_user: "homeassistant"
  mariadb_password: "your_password"
  mariadb_database: "homeassistant"
  input_file: "/config/energy_data/*_high_resolution.csv"
```

## Supported Data Sources

- Ameren Electric
- Domoticz
- DSMR-reader
- E-REDES
- Eneco
- Enel Distribuzione
- EnergyControl
- Engie
- Enphase
- Fluvius
- GreenChoice
- Home Assistant
- HomeWizard
- iSolarCloud (Sungrow)
- Liander
- MeterN
- Myenergi Zappi
- NEM12 (Australian format)
- NextEnergy
- Oxxio
- P1mon
- Shelly EM3
- SlimmeMeterPortal
- SMA
- SolarEdge
- Solarman
- Solax
- United Power
- VanOns
- Xcel Energy
- Zonneplan

**Note:** If your energy provider is not listed, you can use the generic `TemplateDataPrepare.py` as a starting point to create a custom data preparation script. See the [Datasources README](https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data/tree/main/Datasources) for more information.

## ⚠️ Important Warnings

1. **Database Safety**: This integration directly modifies your Home Assistant database
   - ✅ **Automatic backups enabled by default** for SQLite databases
   - ⚠️ **For MariaDB**: Create manual backups before importing
2. **Backup Location**: Check `/config/data/imports/backups/` for SQLite backups
3. Importing large amounts of data can take a long time
4. After importing, you'll need to execute SQL scripts to finalize the import (see main project documentation)

## Complete Workflow

The complete import process consists of three steps:

1. **Prepare your data** using `energy_data_importer.prepare_data`
2. **Import the CSV files** using `energy_data_importer.import_data`
3. **Execute SQL scripts** to finalize the import (see [Database documentation](https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data/tree/main/Database))

## Documentation

For detailed documentation, data source specific guides, and SQL scripts, see the main project repository:
https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data

## Support

For issues, questions, or feature requests:

- [GitHub Issues](https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data/issues)
- [Community Discussion](https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data/discussions)

## Credits

Created by Patrick Vorgers with contributions from the Home Assistant community.

## License

This project is licensed under the same license as the main project.
