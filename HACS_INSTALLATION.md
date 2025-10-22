# Testing the HACS Integration Locally

This guide explains how to test the Energy Data Importer HACS integration locally before submitting a PR.

## Prerequisites

- A running Home Assistant instance (can be a test instance)
- SSH access to your Home Assistant instance (or access to the file system)

## Local Testing Steps

### 1. Copy the Integration to Home Assistant

Copy the `custom_components/energy_data_importer` directory to your Home Assistant's `custom_components` directory:

```bash
# If using SSH/SCP:
scp -r custom_components/energy_data_importer user@homeassistant:/config/custom_components/

# Or if you have direct file system access:
cp -r custom_components/energy_data_importer /path/to/homeassistant/config/custom_components/
```

### 2. Copy the Datasources Directory

The integration needs access to the data preparation scripts:

```bash
# Copy the entire Datasources directory to your HA config:
scp -r Datasources user@homeassistant:/config/

# Or:
cp -r Datasources /path/to/homeassistant/config/
```

### 3. Restart Home Assistant

Restart Home Assistant to load the new integration:

```bash
# Via Home Assistant UI:
# Settings → System → Restart

# Or via CLI if you have access:
ha core restart
```

### 4. Add the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"Energy Data Importer"**
4. Click to add it

You should see the integration added successfully!

### 5. Test the Services

Create an automation or use Developer Tools → Services to test:

#### Test 1: Prepare Data

```yaml
service: energy_data_importer.prepare_data
data:
  data_source: "Template"
  input_file: "/config/Datasources/*/Sample files/*.csv"
```

#### Test 2: Import Data (SQLite)

```yaml
service: energy_data_importer.import_data
data:
  db_type: "sqlite"
  sqlite_db: "/config/home-assistant_v2.db"
  input_file: "/config/*_high_resolution.csv"
```

## Testing with Home Assistant Container

If you're using Docker, you can mount the repository:

```bash
docker run -d \
  --name homeassistant-test \
  --privileged \
  --restart=unless-stopped \
  -e TZ=YOUR_TIMEZONE \
  -v /path/to/this/repo:/config \
  -p 8123:8123 \
  ghcr.io/home-assistant/home-assistant:stable
```

Then follow steps 3-5 above.

## Validating the Integration

### Check Logs

Monitor the Home Assistant logs for any errors:

```bash
# Via UI: Settings → System → Logs

# Or via CLI:
tail -f /config/home-assistant.log
```

Look for lines containing `energy_data_importer`.

### Verify Services

Check that the services are registered:

```bash
# Via UI: Developer Tools → Services
# Search for "energy_data_importer"

# You should see:
# - energy_data_importer.prepare_data
# - energy_data_importer.import_data
```

## Common Issues

### Issue: "Integration not found"

**Solution**: Make sure the `custom_components/energy_data_importer` directory exists in your Home Assistant config directory and restart HA.

### Issue: "Module not found: pandas"

**Solution**: The integration should automatically install required packages. If not, you may need to install them manually:

```bash
# Inside Home Assistant container/venv:
pip install pandas>=2.0.0 tzlocal>=5.0 mysql-connector-python>=8.0.0
```

### Issue: "Data preparation script not found"

**Solution**: Make sure you copied the entire repository structure, including the `Datasources` directory, to your Home Assistant config.

## File Structure

Your Home Assistant config directory should look like this after installation:

```
/config/
├── custom_components/
│   └── energy_data_importer/
│       ├── __init__.py
│       ├── config_flow.py
│       ├── const.py
│       ├── manifest.json
│       ├── services.yaml
│       ├── strings.json
│       ├── translations/
│       │   └── en.json
│       └── README.md
├── Datasources/
│   ├── ImportData.py
│   ├── DataPrepareEngine.py
│   ├── Eneco/
│   ├── Fluvius/
│   └── ... (all other data source directories)
└── Database/
    ├── SQLite/
    └── MariaDB/
```

## Next Steps

Once local testing is successful:

1. Create a fork of the original repository
2. Create a new branch for your changes
3. Commit the changes with a descriptive message
4. Push to your fork
5. Create a Pull Request to the original repository

## HACS Validation

To validate that the integration will work with HACS, you can run the HACS action locally:

```bash
# Install the HACS CLI
pip install hacs-cli

# Validate the integration
hacs validate --category integration
```

## Further Reading

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [HACS Documentation](https://hacs.xyz/)
- [Original Project](https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data)
