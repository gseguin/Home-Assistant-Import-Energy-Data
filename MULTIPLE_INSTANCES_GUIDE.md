# 🔢 Multiple Instances Guide

The Energy Data Importer integration supports adding multiple instances to organize imports from different data sources.

## Why Multiple Instances?

Many users have energy data from multiple sources:

- **Grid electricity** from utility provider (Eneco, Fluvius, etc.)
- **Solar production** from solar inverter (SolarEdge, SMA, Enphase, etc.)
- **Gas consumption** from gas meter
- **Water consumption** from water meter
- **EV charging** from charging station (Myenergi Zappi, etc.)
- **Battery storage** from home battery system

Having separate instances helps:

- ✅ **Organize** different data sources
- ✅ **Identify** which logs belong to which source
- ✅ **Manage** configurations independently
- ✅ **Track** import status per source

## Adding Multiple Instances

### Step 1: Add First Instance

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"Energy Data Importer"**
4. Enter name: `Grid Energy`
5. Click **"Submit"**

### Step 2: Add More Instances

1. Click **"+ Add Integration"** again
2. Search for **"Energy Data Importer"**
3. Enter name: `Solar`
4. Click **"Submit"**

Repeat for each data source you want to manage separately.

### Example Configuration

```
Energy Data Importer instances:
├── Grid Energy       (for utility provider data)
├── Solar            (for solar panel data)
├── Gas              (for gas meter data)
└── Water            (for water meter data)
```

## Practical Example

Let's say you have:

- Electricity data from Eneco
- Solar data from SolarEdge
- Gas data from Fluvius

### Setup

Add three instances:

1. "Eneco Grid"
2. "SolarEdge Solar"
3. "Fluvius Gas"

### Directory Organization

Organize your raw files by source:

```
/config/data/imports/raw/
├── eneco/
│   └── eneco_export_2024.csv
├── solaredge/
│   └── solar_production_2024.csv
└── fluvius/
    └── gas_consumption_2024.csv
```

### Automation per Instance

Create separate automations for each source:

#### Eneco Grid Automation

```yaml
automation:
  - id: import_eneco_grid
    alias: Import Eneco Grid Data
    description: Import electricity data from Eneco
    trigger:
      - platform: event
        event_type: folder_watcher
        event_data:
          path: /config/data/imports/raw/eneco/
          file: "*.csv"
    action:
      - service: system_log.write
        data:
          message: "[Eneco Grid] Starting import"

      - service: energy_data_importer.prepare_data
        data:
          data_source: "Eneco"
          input_file: "/config/data/imports/raw/eneco/{{ trigger.event.data.file }}"
          output_prefix: "eneco"

      - delay:
          seconds: 10

      - service: energy_data_importer.import_data
        data:
          db_type: "sqlite"
          sqlite_db: "/config/home-assistant_v2.db"
          input_file: "/config/data/energy/csv/eneco_*_resolution.csv"

      - service: system_log.write
        data:
          message: "[Eneco Grid] Import completed"
```

#### SolarEdge Solar Automation

```yaml
automation:
  - id: import_solaredge_solar
    alias: Import SolarEdge Solar Data
    description: Import solar production data from SolarEdge
    trigger:
      - platform: event
        event_type: folder_watcher
        event_data:
          path: /config/data/imports/raw/solaredge/
          file: "*.csv"
    action:
      - service: system_log.write
        data:
          message: "[SolarEdge Solar] Starting import"

      - service: energy_data_importer.prepare_data
        data:
          data_source: "SolarEdge"
          input_file: "/config/data/imports/raw/solaredge/{{ trigger.event.data.file }}"
          output_prefix: "solar"

      - delay:
          seconds: 10

      - service: energy_data_importer.import_data
        data:
          db_type: "sqlite"
          sqlite_db: "/config/home-assistant_v2.db"
          input_file: "/config/data/energy/csv/solar_*_resolution.csv"

      - service: system_log.write
        data:
          message: "[SolarEdge Solar] Import completed"
```

#### Fluvius Gas Automation

```yaml
automation:
  - id: import_fluvius_gas
    alias: Import Fluvius Gas Data
    description: Import gas consumption data from Fluvius
    trigger:
      - platform: event
        event_type: folder_watcher
        event_data:
          path: /config/data/imports/raw/fluvius/
          file: "*.csv"
    action:
      - service: system_log.write
        data:
          message: "[Fluvius Gas] Starting import"

      - service: energy_data_importer.prepare_data
        data:
          data_source: "Fluvius"
          input_file: "/config/data/imports/raw/fluvius/{{ trigger.event.data.file }}"
          output_prefix: "gas"

      - delay:
          seconds: 10

      - service: energy_data_importer.import_data
        data:
          db_type: "sqlite"
          sqlite_db: "/config/home-assistant_v2.db"
          input_file: "/config/data/energy/csv/gas_*_resolution.csv"

      - service: system_log.write
        data:
          message: "[Fluvius Gas] Import completed"
```

## Log Identification

With multiple instances, logs are easier to identify:

```
[Grid Energy] Starting data preparation...
[Solar] Import completed successfully
[Gas] Error: Invalid file format
```

Use prefixes in your automations to make logs clearer.

## Managing Instances

### View All Instances

Settings → Devices & Services → Energy Data Importer section shows all instances

### Edit Instance

Click on an instance to see its configuration (currently only shows name, future versions may add more options)

### Remove Instance

Click on an instance → "Delete" to remove it

**Note:** Removing an instance doesn't delete any imported data or files.

## Best Practices

### 1. Descriptive Names

Use clear, descriptive names:

✅ Good:

- "Eneco Grid Electricity"
- "SolarEdge Rooftop"
- "Fluvius Gas Main"

❌ Avoid:

- "Import 1"
- "Data"
- "Energy"

### 2. Organize by Source

Keep files organized in subdirectories:

```
/config/data/imports/raw/
├── grid/
├── solar/
├── gas/
└── water/
```

### 3. Use Output Prefixes

Always use output prefixes to identify generated files:

```yaml
service: energy_data_importer.prepare_data
data:
  data_source: "Eneco"
  output_prefix: "eneco_grid" # Creates: eneco_grid_elec_feed_in_tariff_1_high_resolution.csv
```

### 4. Separate Automations

Create one automation per instance for clarity:

```
automations.yaml:
├── Import Eneco Grid
├── Import SolarEdge Solar
├── Import Fluvius Gas
└── Import HomeWizard Water
```

### 5. Error Handling per Instance

Handle errors differently for each instance:

```yaml
automation:
  - alias: Monitor Eneco Grid Import
    trigger:
      - platform: state
        entity_id: sensor.last_eneco_import
        to: "failed"
    action:
      - service: notify.notify
        data:
          title: "Eneco Grid Import Failed"
          message: "Check /config/data/imports/failed/eneco/"
```

## Scheduled Imports

Set up different schedules for different sources:

```yaml
automation:
  # Daily grid import (Eneco)
  - alias: Daily Eneco Import
    trigger:
      - platform: time
        at: "02:00:00"
    action:
      # Import yesterday's Eneco data

  # Weekly solar import (SolarEdge)
  - alias: Weekly Solar Import
    trigger:
      - platform: time
        at: "03:00:00"
    condition:
      - condition: time
        weekday: [mon]
    action:
      # Import last week's solar data

  # Monthly gas import (Fluvius)
  - alias: Monthly Gas Import
    trigger:
      - platform: time
        at: "04:00:00"
    condition:
      - condition: template
        value_template: "{{ now().day == 1 }}"
    action:
      # Import last month's gas data
```

## Combining Multiple Sources

Import data from all sources in sequence:

```yaml
script:
  import_all_energy_data:
    alias: Import All Energy Data
    description: Import data from all energy sources
    sequence:
      # 1. Grid electricity
      - service: system_log.write
        data:
          message: "Starting multi-source import: Grid"
      - service: energy_data_importer.prepare_data
        data:
          data_source: "Eneco"
          input_file: "/config/data/imports/raw/grid/*.csv"
          output_prefix: "grid"

      - delay:
          seconds: 5

      # 2. Solar
      - service: system_log.write
        data:
          message: "Starting multi-source import: Solar"
      - service: energy_data_importer.prepare_data
        data:
          data_source: "SolarEdge"
          input_file: "/config/data/imports/raw/solar/*.csv"
          output_prefix: "solar"

      - delay:
          seconds: 5

      # 3. Gas
      - service: system_log.write
        data:
          message: "Starting multi-source import: Gas"
      - service: energy_data_importer.prepare_data
        data:
          data_source: "Fluvius"
          input_file: "/config/data/imports/raw/gas/*.csv"
          output_prefix: "gas"

      - delay:
          seconds: 10

      # 4. Import all CSV files at once
      - service: energy_data_importer.import_data
        data:
          db_type: "sqlite"
          sqlite_db: "/config/home-assistant_v2.db"
          input_file: "/config/data/energy/csv/*_resolution.csv"

      - service: system_log.write
        data:
          message: "Multi-source import completed"
```

## Dashboard Integration

Create a dashboard to monitor all instances:

```yaml
type: entities
title: Energy Import Status
entities:
  - type: section
    label: Grid (Eneco)
  - entity: sensor.last_eneco_import_date
  - entity: sensor.eneco_import_status

  - type: section
    label: Solar (SolarEdge)
  - entity: sensor.last_solar_import_date
  - entity: sensor.solar_import_status

  - type: section
    label: Gas (Fluvius)
  - entity: sensor.last_gas_import_date
  - entity: sensor.gas_import_status
```

## Troubleshooting Multiple Instances

### Issue: Can't add another instance

**Cause:** Trying to use the same name twice

**Solution:** Use a unique name for each instance

### Issue: Logs are confusing

**Solution:** Add prefixes to your log messages:

```yaml
- service: system_log.write
  data:
    message: "[Instance Name] Your message here"
```

### Issue: Files getting mixed up

**Solution:** Use output prefixes and organize raw files in subdirectories

## Migration from Single Instance

If you already have a single instance:

1. Note your current configuration
2. Add new instances with descriptive names
3. Update automations to use new instance names
4. Remove old generic instance if needed

## Summary

Multiple instances provide:

✅ **Better organization** of different data sources  
✅ **Clearer logs** with instance identification  
✅ **Independent management** of each source  
✅ **Flexible automation** per source  
✅ **Easier troubleshooting** of specific sources

For more information, see:

- [Integration README](custom_components/energy_data_importer/README.md)
- [Directory Structure Guide](DIRECTORY_STRUCTURE.md)
- [Example Automations](custom_components/energy_data_importer/EXAMPLE_AUTOMATION.yaml)
