#!/bin/bash

pyinstaller --noconfirm "Podcasts Export.spec" 

if [ "$1" != "dmg" ]; then
    exit 0
fi

# Create a folder (named dmg) to prepare our DMG in (if it doesn't already exist).
mkdir -p dist/dmg
# Empty the dmg folder.
rm -r dist/dmg/*
# Copy the app bundle to the dmg folder.
cp -r "dist/Podcasts Export.app" dist/dmg
# If the DMG already exists, delete it.
test -f "dist/Podcasts Export.dmg" && rm "dist/Podcasts Export.dmg"
create-dmg \
  --volname "Podcasts Export" \
  --volicon "icons/icon.icns" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "Podcasts Export.app" 175 120 \
  --hide-extension "Podcasts Export.app" \
  --app-drop-link 425 120 \
  "dist/Podcasts Export.dmg" \
  "dist/dmg/"