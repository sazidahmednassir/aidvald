#!/usr/bin/env bash
# device-check.sh — READ-ONLY Phase 4 device/app verification for AID validation.
# Never uninstalls, clears data, resets, or changes device settings.
#
# Usage:
#   device-check.sh android <serial> <package> [appium_host:port]
#   device-check.sh ios     <udid>   <bundleId> [appium_host:port]
#
# Prints the facts for one device. The agent reads the output and fills the
# Phase 4 status table; it does not decide "matches target build" here —
# that comparison is made against the user-confirmed target build.

set -uo pipefail

PLATFORM="${1:-}"
DEVICE_ID="${2:-}"
APP_ID="${3:-}"
APPIUM="${4:-}"

die() { echo "ERROR: $*" >&2; exit 2; }
section() { echo; echo "== $1 =="; }

[ -n "$PLATFORM" ] && [ -n "$DEVICE_ID" ] && [ -n "$APP_ID" ] || \
  die "usage: device-check.sh <android|ios> <device-id> <app-id> [appium_host:port]"

check_appium() {
  [ -n "$APPIUM" ] || { echo "(no appium host:port passed — skip)"; return; }
  section "Appium server ($APPIUM)"
  if curl -s --max-time 5 "http://$APPIUM/status" ; then echo; else echo "NOT REACHABLE"; fi
  echo
  echo "-- installed drivers --"
  command -v appium >/dev/null 2>&1 && appium driver list --installed 2>&1 || echo "(appium CLI not found)"
}

case "$PLATFORM" in
  android)
    command -v adb >/dev/null 2>&1 || die "adb not found on PATH"
    section "adb devices"
    adb devices -l | grep -w "$DEVICE_ID" || echo "DEVICE $DEVICE_ID NOT LISTED"
    section "OS version (ro.build.version.release)"
    adb -s "$DEVICE_ID" shell getprop ro.build.version.release 2>&1
    section "Model (ro.product.model)"
    adb -s "$DEVICE_ID" shell getprop ro.product.model 2>&1
    section "App installed ($APP_ID)"
    adb -s "$DEVICE_ID" shell pm list packages 2>&1 | grep -w "$APP_ID" || echo "NOT INSTALLED"
    section "Installed build (versionName/versionCode)"
    adb -s "$DEVICE_ID" shell dumpsys package "$APP_ID" 2>&1 | grep -E "versionName|versionCode" | head -4 || echo "NO VERSION INFO"
    check_appium
    ;;
  ios)
    section "Device present"
    if command -v idevice_id >/dev/null 2>&1; then
      idevice_id -l 2>&1 | grep -w "$DEVICE_ID" || echo "UDID $DEVICE_ID NOT LISTED (idevice_id)"
    elif command -v xcrun >/dev/null 2>&1; then
      xcrun xctrace list devices 2>&1 | grep -i "$DEVICE_ID" || echo "UDID $DEVICE_ID NOT LISTED (xctrace)"
    else
      echo "(neither libimobiledevice nor xcrun found — ask before installing)"
    fi
    section "OS version (ProductVersion)"
    command -v ideviceinfo >/dev/null 2>&1 && ideviceinfo -u "$DEVICE_ID" -k ProductVersion 2>&1 || echo "(ideviceinfo not found)"
    section "App installed ($APP_ID) + version/build"
    if command -v ideviceinstaller >/dev/null 2>&1; then
      ideviceinstaller -u "$DEVICE_ID" -l 2>&1 | grep -i "$APP_ID" || echo "NOT INSTALLED / not found"
    elif command -v xcrun >/dev/null 2>&1; then
      xcrun devicectl device info apps --device "$DEVICE_ID" 2>&1 | grep -i "$APP_ID" || echo "NOT INSTALLED / not found"
    else
      echo "(no ideviceinstaller/devicectl — ask before installing libimobiledevice)"
    fi
    check_appium
    ;;
  *)
    die "unknown platform '$PLATFORM' (use android or ios)"
    ;;
esac

echo
echo "== DONE (read-only). Compare 'Installed build' with the user-confirmed target build. =="
