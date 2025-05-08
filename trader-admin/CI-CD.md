# TraderAdmin Installer CI/CD Pipeline

This document explains the continuous integration and continuous deployment (CI/CD) pipeline for building the TraderAdmin NSIS installer.

## Overview

The CI/CD pipeline automatically builds the TraderAdmin Windows installer on commits and pull requests, ensuring that the installer is always up-to-date with the latest code changes. The pipeline is implemented using GitHub Actions.

## Workflow Configuration

The pipeline is defined in `.github/workflows/build-installer.yml` and performs the following steps:

1. **Trigger Conditions**:
   - Pushes to `main` or `master` branches that include changes to the `trader-admin/` directory
   - Pull requests targeting `main` or `master` branches with changes to the `trader-admin/` directory
   - Manual triggers via GitHub Actions UI (workflow_dispatch)

2. **Build Environment**:
   - Windows Server (Latest)
   - Go 1.20+
   - Wails CLI
   - NSIS (Nullsoft Scriptable Install System)
   - Node.js 18

3. **Build Process**:
   - Install dependencies (Go, Wails, NSIS, Node.js)
   - Build the Wails TraderAdmin application
   - Ensure LICENSE.txt exists
   - Build the NSIS installer
   - Extract version number from the NSIS script

4. **Artifacts**:
   - The installer is uploaded as a build artifact
   - Artifacts are retained for 30 days
   - Installer filename format: `TraderAdmin-Setup-{version}.exe`

5. **Release Creation**:
   - When a new tag is pushed, a draft GitHub release is created
   - The installer is automatically attached to the release
   - Release includes basic system requirements information

## Using the Pipeline

### For Development

- The pipeline automatically runs on all qualifying pull requests
- Developers can download the installer artifact from the GitHub Actions run page
- This allows testing the installer before merging changes

### For Releases

1. Update the version number in `trader-admin/TraderAdmin-Installer.nsi`:
   ```nsi
   !define VERSION "x.y.z"
   ```

2. Commit and push the changes to the main/master branch

3. Create and push a tag with the same version number:
   ```bash
   git tag vx.y.z
   git push origin vx.y.z
   ```

4. The pipeline will:
   - Build the installer
   - Create a draft release
   - Attach the installer to the release

5. Review and publish the draft release on GitHub

## Troubleshooting

If the build fails, check the following:

1. **Wails Build Issues**:
   - Ensure frontend dependencies are correctly installed
   - Verify the Go code compiles successfully locally

2. **NSIS Issues**:
   - Check for syntax errors in the `TraderAdmin-Installer.nsi` file
   - Verify all required files exist in the expected locations

3. **Version Extraction**:
   - Make sure the VERSION definition in the NSIS script follows the format: `!define VERSION "x.y.z"`

## Manual Builds

For local development and testing, you can still use the `build-installer.bat` script:
```bash
cd trader-admin
.\build-installer.bat
```
