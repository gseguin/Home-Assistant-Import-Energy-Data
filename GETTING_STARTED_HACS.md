# 🚀 Getting Started with HACS Integration

This guide will help you test the HACS integration locally before submitting a Pull Request.

## 📋 What Was Created

The HACS integration adds a native Home Assistant integration that makes it easy to import historical energy data through services instead of manual scripts.

### Key Components

**Integration Files:**

- ✅ `custom_components/energy_data_importer/` - Full Home Assistant integration
- ✅ `hacs.json` - HACS metadata for discovery
- ✅ GitHub Actions workflows for validation
- ✅ Comprehensive documentation and examples

**Two Main Services:**

1. `energy_data_importer.prepare_data` - Convert provider data to importable format
2. `energy_data_importer.import_data` - Import CSV data into Home Assistant database

**Supported:**

- 30+ energy data sources (all existing sources)
- SQLite and MariaDB databases
- Full automation support
- Backward compatible with existing scripts

## 🧪 Quick Local Test

### Step 1: Validate the Structure

```bash
cd /home/ghislain/src/Home-Assistant-Import-Energy-Data
python3 validate_hacs_integration.py
```

Expected output:

```
✅ All validations passed!
```

### Step 2: Run Tests

```bash
python3 tests/test_integration_structure.py
```

Expected output:

```
Results: 6 passed, 0 failed
```

## 🏠 Test in Home Assistant

### Option A: Test with Home Assistant Container

1. **Start a test Home Assistant instance:**

```bash
docker run -d \
  --name ha-test \
  --restart=unless-stopped \
  -e TZ=Europe/Brussels \
  -v /home/ghislain/src/Home-Assistant-Import-Energy-Data:/config \
  -p 8123:8123 \
  ghcr.io/home-assistant/home-assistant:stable
```

2. **Wait for Home Assistant to start** (check logs):

```bash
docker logs -f ha-test
```

3. **Access Home Assistant:**

   - Open browser to `http://localhost:8123`
   - Complete the onboarding wizard

4. **Add the integration:**

   - Settings → Devices & Services
   - "+ Add Integration"
   - Search for "Energy Data Importer"
   - Add it

5. **Test the services:**
   - Developer Tools → Services
   - Try `energy_data_importer.prepare_data`
   - Try `energy_data_importer.import_data`

### Option B: Test with Existing Home Assistant

If you have an existing Home Assistant instance:

1. **Copy the integration:**

```bash
# Find your HA config directory (usually ~/.homeassistant or /config)
HACONFIG="$HOME/.homeassistant"

# Copy integration
mkdir -p "$HACONFIG/custom_components"
cp -r custom_components/energy_data_importer "$HACONFIG/custom_components/"

# Copy datasources
cp -r Datasources "$HACONFIG/"
cp -r Database "$HACONFIG/"
```

2. **Restart Home Assistant**

3. **Add the integration** (same as Option A, step 4-5)

## 🧪 Example Test Scenarios

### Test 1: Prepare Sample Data

If you have sample files, test the prepare service:

```yaml
service: energy_data_importer.prepare_data
data:
  data_source: "Eneco" # Or any supported source
  input_file: "/config/Datasources/Eneco/Sample files/*.csv"
  output_prefix: "test"
```

### Test 2: Import to Database

⚠️ **IMPORTANT**: Test with a copy of your database, not the live one!

```bash
# Make a backup first
cp ~/.homeassistant/home-assistant_v2.db ~/.homeassistant/home-assistant_v2.db.backup
```

Then test import:

```yaml
service: energy_data_importer.import_data
data:
  db_type: "sqlite"
  sqlite_db: "/config/home-assistant_v2.db"
  input_file: "/config/test_*_high_resolution.csv"
```

### Test 3: Complete Workflow

Create a script to test end-to-end:

```yaml
# File: test_import_script.yaml
sequence:
  - service: system_log.write
    data:
      message: "Starting energy import test"
      level: info

  - service: energy_data_importer.prepare_data
    data:
      data_source: "Template"
      input_file: "/config/test_data.csv"

  - delay:
      seconds: 5

  - service: energy_data_importer.import_data
    data:
      db_type: "sqlite"
      sqlite_db: "/config/home-assistant_v2.db"
      input_file: "/config/*_resolution.csv"

  - service: system_log.write
    data:
      message: "Energy import test completed"
      level: info
```

## ✅ Validation Checklist

Before proceeding to PR, verify:

### Integration Installation

- [ ] Integration appears in Settings → Devices & Services
- [ ] Integration can be added without errors
- [ ] Integration icon displays correctly

### Services

- [ ] `energy_data_importer.prepare_data` appears in Developer Tools
- [ ] `energy_data_importer.import_data` appears in Developer Tools
- [ ] Service descriptions are clear
- [ ] Service parameters have proper selectors

### Functionality

- [ ] Prepare service runs without errors
- [ ] Import service runs without errors
- [ ] Output files are created correctly
- [ ] Data is imported into database
- [ ] No errors in Home Assistant logs

### Check Logs

```bash
# Look for any errors
docker logs ha-test | grep -i error
docker logs ha-test | grep energy_data_importer
```

## 🐛 Troubleshooting

### Issue: "Integration not found"

**Solution:**

- Ensure `custom_components/energy_data_importer` exists in your HA config
- Restart Home Assistant
- Check logs for import errors

### Issue: "No module named 'pandas'"

**Solution:**
The integration should auto-install dependencies. If not:

```bash
docker exec -it ha-test pip install pandas>=2.0.0 tzlocal>=5.0
```

### Issue: "Data preparation script not found"

**Solution:**

- Ensure `Datasources/` directory is copied to HA config
- Check that the directory structure is intact
- Verify file permissions

### Issue: Services don't appear

**Solution:**

- Check Home Assistant logs for integration load errors
- Verify `manifest.json` is valid JSON
- Ensure all required files exist
- Restart Home Assistant

## 📊 Expected Results

After successful testing, you should see:

1. **Integration installed:**

   - Appears in Settings → Devices & Services
   - Shows "Energy Data Importer" with icon

2. **Services available:**

   - `energy_data_importer.prepare_data`
   - `energy_data_importer.import_data`

3. **Logs clean:**

   - No errors related to energy_data_importer
   - Services execute successfully

4. **Files created:**
   - CSV files generated by prepare_data
   - Data imported into database

## 🎯 Next Steps

Once local testing is successful:

1. ✅ **Review all changes**

   ```bash
   git status
   git diff
   ```

2. ✅ **Run final validation**

   ```bash
   python3 validate_hacs_integration.py
   python3 tests/test_integration_structure.py
   ```

3. ✅ **Review documentation**

   - [ ] Read [PR_CHECKLIST.md](PR_CHECKLIST.md)
   - [ ] Review [HACS_INTEGRATION_SUMMARY.md](HACS_INTEGRATION_SUMMARY.md)

4. ✅ **Prepare PR**
   - Follow steps in [PR_CHECKLIST.md](PR_CHECKLIST.md)
   - Use suggested PR description
   - Include screenshots of successful tests

## 📚 Additional Resources

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [HACS Documentation](https://hacs.xyz/)
- [Original Project](https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data)
- [Integration README](custom_components/energy_data_importer/README.md)
- [Example Automations](custom_components/energy_data_importer/EXAMPLE_AUTOMATION.yaml)

## 💡 Tips

1. **Always test with a database backup**
2. **Start with small test datasets**
3. **Check logs frequently**
4. **Test multiple data sources if possible**
5. **Document any issues you encounter**

## 🎉 Success!

If all tests pass and the integration works as expected, you're ready to create a Pull Request!

Follow the [PR_CHECKLIST.md](PR_CHECKLIST.md) for detailed submission instructions.

Good luck! 🚀
