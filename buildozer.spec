[app]

# Application
title = MedGen AI
package.name = medgenai
package.domain = org.medgenai

# Source
source.dir = .
source.include_exts = py,json,png,jpg,kv,txt

# Version
version = 1.1

# Icon
icon.filename = medgen_ai_icon.png

# Python / Kivy
requirements = python3==3.12.9,hostpython3==3.12.9,kivy==2.3.1

# Orientation
orientation = portrait
fullscreen = 0

# Android
android.api = 35
android.minapi = 24
android.ndk_api = 26
android.archs = arm64-v8a

# Permissions
android.permissions = INTERNET

# Android SDK license
android.accept_sdk_license = True

# Stable p4a branch
p4a.branch = master


[buildozer]

log_level = 2
warn_on_root = 1
