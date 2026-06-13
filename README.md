 Personal Diary — Android App (Kivy + Python)

A full-featured journal app: write, edit, delete, search, and timestamp
daily entries, with mood tags, stored locally in SQLite.

## Features

- New entry screen with title, mood emoji picker, and multi-line body
- Auto timestamping (created + last-edited times)
- Entry list with previews, sorted newest-first
- Live search across titles and entry text
- Edit existing entries
- Delete with confirmation
- Local SQLite storage (private to the app, persists across launches)

## Project files

```
diary_kivy/
├── main.py            # App source (UI + database logic)
├── buildozer.spec     # Android build configuration
└── README.md
```

## Run on your computer first (recommended)

Before building the APK, test the app on your desktop:

```bash
pip install kivy
python3 main.py
```

A window opens with the journal UI. Try adding, searching, editing, and
deleting entries — `diary.db` is created in the same folder.

## Build the Android APK

APK building requires **Linux** (Ubuntu/Debian works best) or **WSL on
Windows**. It cannot be done on macOS or plain Windows directly.

### 1. Install Buildozer and dependencies

```bash
sudo apt update
sudo apt install -y python3-pip build-essential git python3-dev \
    ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
    zlib1g-dev openjdk-17-jdk unzip

pip3 install --user buildozer cython
```

### 2. Build the debug APK

From inside the `diary_kivy/` folder (where `buildozer.spec` lives):

```bash
buildozer android debug
```

The first build downloads the Android SDK/NDK automatically — this can
take 20–60 minutes and several GB of disk space. Subsequent builds are
much faster.

The finished APK appears at:

```
bin/personaldiary-1.0-arm64-v8a-debug.apk
```

### 3. Install on your phone

With your phone connected via USB and developer mode/USB debugging on:

```bash
buildozer android deploy run
```

Or transfer the APK file to your phone and tap it to install (enable
"Install from unknown sources" if prompted).

## Notes

- Data is stored in `diary.db` inside the app's private storage on
  Android, so it persists between launches but is removed if you
  uninstall the app.
- To change the app icon or splash screen, add `icon.png` /
  `presplash.png` to a `data/` folder and uncomment the relevant lines
  in `buildozer.spec`.
- If the build fails on first run, re-running `buildozer android debug`
  often resolves transient SDK download issues.
