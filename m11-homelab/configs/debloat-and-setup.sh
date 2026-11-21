#!/data/data/com.termux/files/usr/bin/bash
# =============================================================================
# debloat-and-setup.sh — Samsung Galaxy M11 (rooted, Magisk v30.7)
# =============================================================================
# PLACEHOLDER SCRIPT — no destructive commands are wired up yet.
#
# Single home for the M11 debloat pass and Termux setup steps. Two audiences
# live in this file and must never be mixed:
#   1. LAPTOP SIDE — ADB commands run from the PC against the phone.
#   2. TERMUX SIDE — setup commands run on the phone itself.
#
# HARD LOCKS (never remove, under any circumstances):
#   com.android.settings, device drivers, telephony core, Magisk, Termux
#
# Run on the phone with:  bash ~/debloat-and-setup.sh
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# 1. LAPTOP SIDE — ADB debloat (PowerShell on the PC, not on the phone)
# -----------------------------------------------------------------------------
# adb devices
# adb shell pm uninstall -k --user 0 <package.name>     # reversible per-package
# Recovery if a package was removed by mistake:
# adb shell cmd package install-existing <package.name>

# -----------------------------------------------------------------------------
# 2. TERMUX SIDE — base services
# -----------------------------------------------------------------------------
# pkg update -y
# sshd                    # OpenSSH listener on port 8022

# -----------------------------------------------------------------------------
# 3. TERMUX SIDE — storage & media paths
# -----------------------------------------------------------------------------
# termux-setup-storage
# mkdir -p /storage/43CC-5E0C/Music

# -----------------------------------------------------------------------------
# 4. TODO (fill these in as each step is actually implemented)
# -----------------------------------------------------------------------------
# - [ ] Paste the approved round-3 debloat list (hard locks excluded).
# - [ ] ACC Magisk module install for the 24/7 charge cap.
# - [ ] Linux Deploy Debian bootstrap.
# - [ ] Navidrome service start/stop helpers (see navidrome.toml).
