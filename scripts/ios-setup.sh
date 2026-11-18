#!/bin/bash
# Runs after `npx cap add ios`: Game Center plugin, portrait only, iPhone only, export-compliance flag, display name.
set -e
APPDIR=ios/App/App
PLIST=$APPDIR/Info.plist
PB=/usr/libexec/PlistBuddy

cp native/GameCenterPlugin.swift native/MainViewController.swift native/App.entitlements $APPDIR/
gem list xcodeproj -i >/dev/null 2>&1 || gem install xcodeproj --no-document
ruby scripts/add-native.rb
sed -i '' 's/customClass="CAPBridgeViewController" customModule="Capacitor"/customClass="MainViewController" customModule="App" customModuleProvider="target"/' $APPDIR/Base.lproj/Main.storyboard
grep -q 'MainViewController' $APPDIR/Base.lproj/Main.storyboard || { echo "storyboard not updated"; exit 1; }

$PB -c "Set :CFBundleDisplayName 'Cape Cove'" $PLIST 2>/dev/null || $PB -c "Add :CFBundleDisplayName string 'Cape Cove'" $PLIST
$PB -c "Add :ITSAppUsesNonExemptEncryption bool false" $PLIST 2>/dev/null || $PB -c "Set :ITSAppUsesNonExemptEncryption false" $PLIST
$PB -c "Add :UIRequiresFullScreen bool true" $PLIST 2>/dev/null || true
$PB -c "Delete :UISupportedInterfaceOrientations" $PLIST 2>/dev/null || true
$PB -c "Add :UISupportedInterfaceOrientations array" $PLIST
$PB -c "Add :UISupportedInterfaceOrientations:0 string UIInterfaceOrientationPortrait" $PLIST
$PB -c "Delete :UISupportedInterfaceOrientations~ipad" $PLIST 2>/dev/null || true
$PB -c "Add :UIStatusBarHidden bool true" $PLIST 2>/dev/null || true
$PB -c "Add :UIViewControllerBasedStatusBarAppearance bool false" $PLIST 2>/dev/null || $PB -c "Set :UIViewControllerBasedStatusBarAppearance false" $PLIST
$PB -c "Add :GKGameCenterBadgingDisabled bool false" $PLIST 2>/dev/null || true
# iOS 15 minimum (Apple requirement from April 2027)
sed -i '' "s/platform :ios, '1[34].0'/platform :ios, '15.0'/" ios/App/Podfile
sed -i '' 's/IPHONEOS_DEPLOYMENT_TARGET = 1[34].0;/IPHONEOS_DEPLOYMENT_TARGET = 15.0;/g' ios/App/App.xcodeproj/project.pbxproj
echo "ios setup done"
