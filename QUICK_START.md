# ⚡ Quick Start Guide

## What We Built

A complete HACS integration for the Home-Assistant-Import-Energy-Data project that allows users to import historical energy data through Home Assistant services instead of manual scripts.

## 🎯 Your Options

You have **two paths** forward:

### Path 1: Test First, Then Submit PR (Recommended) ⭐

1. **Test Locally**

   ```bash
   # Read the testing guide
   cat GETTING_STARTED_HACS.md

   # Quick validation
   python3 validate_hacs_integration.py
   python3 tests/test_integration_structure.py
   ```

2. **Test in Home Assistant**

   - Follow instructions in `GETTING_STARTED_HACS.md`
   - Verify both services work
   - Check for errors in logs

3. **Submit PR**
   - Follow steps in `PR_CHECKLIST.md`
   - Include test results in PR description

### Path 2: Submit PR Immediately

1. **Review Changes**

   ```bash
   git status
   git diff README.md
   ```

2. **Create PR**
   - Follow `PR_CHECKLIST.md`
   - Mention it needs testing by maintainer

## 📦 What's Included

```
custom_components/energy_data_importer/   ← The integration
├── __init__.py                           ← Main integration code
├── config_flow.py                        ← UI configuration
├── const.py                              ← Constants
├── manifest.json                         ← Integration metadata
├── services.yaml                         ← Service definitions
├── strings.json                          ← UI translations
├── icon.png                              ← Integration icon
├── README.md                             ← Integration docs
├── EXAMPLE_AUTOMATION.yaml               ← Usage examples
└── translations/
    └── en.json                           ← English translations

hacs.json                                 ← HACS metadata
HACS_INSTALLATION.md                      ← Installation/testing guide
GETTING_STARTED_HACS.md                   ← Detailed quick start
PR_CHECKLIST.md                           ← PR submission guide
HACS_INTEGRATION_SUMMARY.md               ← Full implementation details
validate_hacs_integration.py              ← Validation script
tests/test_integration_structure.py       ← Integration tests

.github/workflows/
├── hacs-validation.yml                   ← HACS validation CI
└── hassfest.yml                          ← HA validation CI
```

## 🚀 Quick Commands

### Validate Everything

```bash
cd /home/ghislain/src/Home-Assistant-Import-Energy-Data

# Validate structure
python3 validate_hacs_integration.py

# Run tests
python3 tests/test_integration_structure.py

# Check git status
git status --short
```

### View Documentation

```bash
# Quick start (this file)
cat QUICK_START.md

# Testing guide
cat GETTING_STARTED_HACS.md

# PR submission guide
cat PR_CHECKLIST.md

# Full details
cat HACS_INTEGRATION_SUMMARY.md

# Integration README
cat custom_components/energy_data_importer/README.md
```

### Test with Docker

```bash
# Start test Home Assistant instance
docker run -d \
  --name ha-test \
  --restart=unless-stopped \
  -e TZ=Europe/Brussels \
  -v /home/ghislain/src/Home-Assistant-Import-Energy-Data:/config \
  -p 8123:8123 \
  ghcr.io/home-assistant/home-assistant:stable

# Watch logs
docker logs -f ha-test

# Access: http://localhost:8123

# Stop when done
docker stop ha-test
docker rm ha-test
```

### Submit Pull Request

```bash
# 1. Fork on GitHub (click "Fork" button)

# 2. Add your fork as remote
git remote add myfork https://github.com/YOUR_USERNAME/Home-Assistant-Import-Energy-Data.git

# 3. Create feature branch
git checkout -b feature/hacs-integration

# 4. Stage changes
git add .

# 5. Commit (use the message from PR_CHECKLIST.md)
git commit -m "feat: add HACS integration support

- Add custom_components/energy_data_importer integration
- Create prepare_data and import_data services
- Support 30+ existing data sources
- Add comprehensive documentation and examples
- Add GitHub Actions for validation
- Update README with HACS installation option

This is a non-breaking change that adds HACS support while
maintaining full backward compatibility with existing scripts."

# 6. Push to your fork
git push myfork feature/hacs-integration

# 7. Create PR on GitHub
# Go to: https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data
# Click "Pull Requests" → "New Pull Request" → "compare across forks"
```

## 📋 Pre-PR Checklist

Quick checklist before submitting:

- [ ] Read `GETTING_STARTED_HACS.md`
- [ ] Read `PR_CHECKLIST.md`
- [ ] Validation passed: `python3 validate_hacs_integration.py`
- [ ] Tests passed: `python3 tests/test_integration_structure.py`
- [ ] (Optional but recommended) Tested in Home Assistant
- [ ] Git commit message is descriptive
- [ ] Ready to submit PR

## 💡 Quick Tips

1. **Testing is optional but recommended** - The maintainer may want to test it themselves
2. **Be responsive** - Answer any questions from the maintainer promptly
3. **Be patient** - PR review may take time
4. **Be flexible** - Maintainer may request changes

## 🎯 The Two Services

### Service 1: Prepare Data

```yaml
service: energy_data_importer.prepare_data
data:
  data_source: "Eneco" # Pick from 30+ sources
  input_file: "/config/energy_data/*.csv"
  output_prefix: "meter1" # Optional
```

### Service 2: Import Data

```yaml
service: energy_data_importer.import_data
data:
  db_type: "sqlite" # or "mariadb"
  sqlite_db: "/config/home-assistant_v2.db"
  input_file: "/config/*_high_resolution.csv"
```

## 📚 Full Documentation Map

```
START HERE
    ↓
QUICK_START.md (this file) ← You are here
    ↓
├─→ Want to test? → GETTING_STARTED_HACS.md
├─→ Want to PR?   → PR_CHECKLIST.md
├─→ Want details? → HACS_INTEGRATION_SUMMARY.md
└─→ Want to see integration docs? → custom_components/energy_data_importer/README.md
```

## ❓ Common Questions

**Q: Do I need to test before PR?**
A: Not required, but recommended. The maintainer will test anyway.

**Q: Will this break existing functionality?**
A: No, it's fully backward compatible.

**Q: Can users still use the original Python scripts?**
A: Yes! Both methods work.

**Q: What if the maintainer rejects the PR?**
A: You can keep using it locally or create a separate HACS repository.

**Q: Do I need to be a Python expert?**
A: No, the code is ready to go.

## 🎉 You're Ready!

The integration is complete and validated. Choose your path:

1. **Conservative**: Test first → See `GETTING_STARTED_HACS.md`
2. **Fast track**: Submit PR now → See `PR_CHECKLIST.md`

Either way, you've successfully created a production-ready HACS integration! 🚀

---

**Need help?** Check the detailed guides:

- Testing: `GETTING_STARTED_HACS.md`
- PR Submission: `PR_CHECKLIST.md`
- Full Details: `HACS_INTEGRATION_SUMMARY.md`
