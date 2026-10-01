# Hermes integration

The portable Agent Skills live under `skills/adw/`. This integration adds the `/adw` router, optional persona, and a transactional installer for Hermes profiles.

Use the ready-to-paste command in the matching GitHub Release notes. It pins a 40-character commit SHA and the SHA-256 of the codeload archive; branches and tags are refused. The installer stages and validates all files, installs only the 13 skill directories (never `skills/_shared/`), and restores the previous installation if activation or the post-install Doctor check fails.

After installation, restart the Hermes gateway and run `/adw` for help. Uninstall with the same pinned script and `--uninstall`; only marker-owned paths are removed. Set `ADW_PROFILE` to choose a profile, `ADW_INSTALL_SOUL=yes` to install the optional persona, and `ADW_REPLACE_UNMANAGED=yes` only after reviewing a colliding unmanaged path.

Maintainers validate the integration with:

```bash
python3 tools/validate_adw_plugin_package.py
```
