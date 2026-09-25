[app]
title = MedGen AI
package.name = medgenai
package.domain = org.medgenai
source.dir = .
source.include_exts = py,json,png,jpg,kv
version = 1.0

requirements = python3,kivy==2.3.1

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 24
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
