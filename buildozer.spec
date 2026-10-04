[app]

# (str) Title of your application
title = MedGen AI

# (str) Package name
package.name = medgenai

# (str) Package domain
package.domain = org.medgenai

# (str) Source code directory
source.dir = .

# (list) Source file extensions
source.include_exts = py,json,png,jpg,kv,txt

# (str) Application version
version = 1.1

# (str) Application icon
icon.filename = medgen_ai_icon.png

# (str) Python/Kivy requirements
requirements = python3,kivy==2.3.1,liblzma

# (str) Orientation
orientation = portrait

# (bool) Fullscreen
fullscreen = 0

# (str) Android API
android.api = 35

# (str) Minimum Android API
android.minapi = 24

# (str) Android architectures
android.archs = arm64-v8a

# (list) Android permissions
android.permissions = INTERNET

# (bool) Accept Android SDK license
android.accept_sdk_license = True


# --------------------------------------------------
# Python-for-Android configuration
# --------------------------------------------------

# Use a stable p4a release instead of current develop
p4a.url = https://github.com/kivy/python-for-android.git
p4a.branch = master
p4a.commit = v2024.01.21

# SDL2 bootstrap for Kivy
p4a.bootstrap = sdl2


[buildozer]

# Buildozer log level
log_level = 2

# Warn when running as root
warn_on_root = 1
