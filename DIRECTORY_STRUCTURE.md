# 📁 Directory Structure Guide

The Energy Data Importer integration uses an organized directory structure to manage the import workflow efficiently.

## Directory Layout

When you add the Energy Data Importer integration, it automatically creates the following directory structure in your Home Assistant config:

```
/config/
└── data/
    ├── energy/
    │   └── csv/                    # Generated CSV files ready for import
    │
    └── imports/
        ├── raw/                     # Raw data files from energy providers
        ├── processed/               # Successfully processed files (manual)
        └── failed/                  # Failed imports for review (manual)
```

## Directory Purposes

### `/config/data/energy/csv/`
**Purpose:** Store generated CSV files that are ready to be imported into Home Assistant

**Contents:**
- `*_high_resolution.csv` - High-resolution energy data (e.g., hourly)
- `*_low_resolution.csv` - Low-resolution energy data (e.g., daily)

**Usage:**
1. The `prepare_data` service generates files here (or outputs to current directory)
2. The `import_data` service reads files from here
3. Files should follow the naming convention: `{sensor_id}_{resolution}.csv`

**Example files:**
```
elec_feed_in_tariff_1_high_resolution.csv
elec_feed_out_tariff_1_high_resolution.csv
gas_high_resolution.csv
solar_high_resolution.csv
```

### `/config/data/imports/raw/`
**Purpose:** Place raw data files downloaded from your energy provider

**Contents:**
- Original CSV, XLSX, XLS, JSON, or DB files from energy providers
- Files in provider-specific formats

**Usage:**
1. Download data from your energy provider's website/API
2. Place files in this directory
3. Run `prepare_data` service pointing to these files
4. Optionally move to `processed/` after successful preparation

**Example workflow:**
```yaml
# Place file: /config/data/imports/raw/eneco_export_2024.csv

# Prepare data:
service: energy_data_importer.prepare_data
data:
  data_source: "Eneco"
  input_file: "/config/data/imports/raw/eneco_export_2024.csv"

# File is processed, optionally move to processed/
```

### `/config/data/imports/processed/`
**Purpose:** Archive successfully processed raw files

**Contents:**
- Raw files that have been successfully converted to CSV
- Moved here manually or via automation

**Usage:**
1. After successful preparation, move raw files here
2. Keeps `raw/` directory clean
3. Provides audit trail of processed files

**Example automation:**
```yaml
# In configuration.yaml:
shell_command:
  move_to_processed: mv /config/data/imports/raw/{{ filename }} /config/data/imports/processed/

# In automation:
- service: shell_command.move_to_processed
  data:
    filename: "eneco_export_2024.csv"
```

### `/config/data/imports/failed/`
**Purpose:** Store files that failed to process for later review

**Contents:**
- Raw files that encountered errors during processing
- Moved here manually or via automation

**Usage:**
1. When preparation fails, move the file here
2. Review file format and error logs
3. Fix issues and move back to `raw/` for retry

**Example automation:**
```yaml
# In configuration.yaml:
shell_command:
  move_to_failed: mv /config/data/imports/raw/{{ filename }} /config/data/imports/failed/

# In automation (with error handling):
action:
  - service: energy_data_importer.prepare_data
    data:
      data_source: "Eneco"
      input_file: "/config/data/imports/raw/{{ filename }}"
  rescue:
    - service: shell_command.move_to_failed
      data:
        filename: "{{ filename }}"
    - service: notify.notify
      data:
        message: "Import failed for {{ filename }}"
```

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Import Workflow                          │
└─────────────────────────────────────────────────────────────┘

1. Download from Provider
   ↓
   /config/data/imports/raw/
   (eneco_export.csv)
   ↓
2. prepare_data Service
   ↓
   /config/data/energy/csv/
   (elec_feed_in_tariff_1_high_resolution.csv, etc.)
   ↓
3. import_data Service
   ↓
   Home Assistant Database
   (statistics & statistics_short_term tables)
   ↓
4. File Management (Optional)
   ├─ Success → /config/data/imports/processed/
   └─ Failure → /config/data/imports/failed/
```

## Complete Example Automation

Here's a complete automation that uses the entire directory structure:

```yaml
automation:
  - id: energy_import_with_file_management
    alias: Energy Import with File Management
    description: Complete workflow with organized file management
    mode: single
    trigger:
      # Trigger when new file appears in raw directory
      - platform: event
        event_type: folder_watcher
        event_data:
          path: /config/data/imports/raw/
          file: "*.csv"
    
    action:
      # Step 1: Log start
      - service: system_log.write
        data:
          message: "Processing file: {{ trigger.event.data.file }}"
          level: info
      
      # Step 2: Prepare data
      - service: energy_data_importer.prepare_data
        data:
          data_source: "Eneco"
          input_file: "/config/data/imports/raw/{{ trigger.event.data.file }}"
        continue_on_error: true
        register: prepare_result
      
      # Step 3: Check if preparation was successful
      - choose:
          # Success path
          - conditions:
              - condition: template
                value_template: "{{ prepare_result.success | default(false) }}"
            sequence:
              # Wait for CSV files to be generated
              - delay:
                  seconds: 5
              
              # Import data
              - service: energy_data_importer.import_data
                data:
                  db_type: "sqlite"
                  sqlite_db: "/config/home-assistant_v2.db"
                  input_file: "/config/data/energy/csv/*_resolution.csv"
              
              # Move to processed
              - service: shell_command.move_to_processed
                data:
                  filename: "{{ trigger.event.data.file }}"
              
              # Notify success
              - service: notify.notify
                data:
                  title: "Energy Import Success"
                  message: "Successfully imported {{ trigger.event.data.file }}"
        
        # Failure path
        default:
          - service: shell_command.move_to_failed
            data:
              filename: "{{ trigger.event.data.file }}"
          
          - service: notify.notify
            data:
              title: "Energy Import Failed"
              message: "Failed to import {{ trigger.event.data.file }}"

# Required shell commands in configuration.yaml:
# shell_command:
#   move_to_processed: mv /config/data/imports/raw/{{ filename }} /config/data/imports/processed/
#   move_to_failed: mv /config/data/imports/raw/{{ filename }} /config/data/imports/failed/
```

## Maintenance Tips

### 1. Periodic Cleanup

Create an automation to archive old processed files:

```yaml
automation:
  - alias: Archive Old Energy Data
    trigger:
      - platform: time
        at: "03:00:00"
    condition:
      - condition: time
        weekday: [sun]
    action:
      - service: shell_command.archive_old_files
        # Archive files older than 90 days

# In configuration.yaml:
# shell_command:
#   archive_old_files: find /config/data/imports/processed -type f -mtime +90 -exec gzip {} \;
```

### 2. Monitor Directory Sizes

Track directory sizes to prevent disk space issues:

```yaml
sensor:
  - platform: folder
    folder: /config/data/imports/raw
  - platform: folder
    folder: /config/data/imports/processed
  - platform: folder
    folder: /config/data/energy/csv
```

### 3. Failed Import Review

Create a notification for files in the failed directory:

```yaml
automation:
  - alias: Notify Failed Imports
    trigger:
      - platform: event
        event_type: folder_watcher
        event_data:
          path: /config/data/imports/failed/
    action:
      - service: notify.notify
        data:
          title: "Failed Import Needs Review"
          message: "File in failed directory: {{ trigger.event.data.file }}"
```

## File Permissions

Ensure Home Assistant has read/write access to all directories:

```bash
# If using Docker or specific user:
chown -R homeassistant:homeassistant /config/data
chmod -R 755 /config/data
```

## Backup Recommendations

Include these directories in your backup strategy:

- ✅ `/config/data/imports/processed/` - Archive of imported data
- ⚠️ `/config/data/imports/raw/` - If you can't re-download from provider
- ❌ `/config/data/energy/csv/` - Generated files, can be recreated
- ❌ `/config/data/imports/failed/` - Temporary review files

## Troubleshooting

### Issue: Directories not created

**Solution:**
Restart Home Assistant after installing the integration, or manually create:

```bash
mkdir -p /config/data/energy/csv
mkdir -p /config/data/imports/{raw,processed,failed}
```

### Issue: Permission denied errors

**Solution:**
Check file permissions:

```bash
ls -la /config/data
# Should show homeassistant as owner
```

### Issue: Files not appearing

**Solution:**
- Check if files are in the correct directory
- Verify file extensions match service expectations
- Check Home Assistant logs for errors

## Custom Directory Structure

If you prefer a different structure, you can customize paths in service calls:

```yaml
service: energy_data_importer.prepare_data
data:
  data_source: "Eneco"
  input_file: "/config/my_custom_path/data.csv"
  # Output will still go to current directory
```

However, using the standard structure is recommended for:
- Consistency across automations
- Easier troubleshooting
- Community support
- Future integration updates

## Summary

The organized directory structure provides:

✅ **Clear workflow:** Raw → CSV → Import → Archive
✅ **Error handling:** Failed files are isolated for review  
✅ **Audit trail:** Processed files are archived  
✅ **Automation-friendly:** Easy to build automations around  
✅ **Maintainable:** Easy to clean up and manage

For more information, see:
- [Integration README](custom_components/energy_data_importer/README.md)
- [Example Automations](custom_components/energy_data_importer/EXAMPLE_AUTOMATION.yaml)
- [Main Documentation](README.md)

