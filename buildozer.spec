[app]

# (str) Title of your application
title = Sistema CELEX

# (str) Package name
package.name = celexapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.celex

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
# NOTA: Usamos pg8000 (Python puro) en lugar de psycopg2 para evitar errores de compilación C en Android
requirements = python3,kivy,kivymd,pg8000

# (str) Custom source folders for requirements
# Sets custom source for any requirement with recipes
# requirements.source.kivy = ../kivy

# (str) Preserved names for requirements
# preserve.requirements = 

# (list) Garden requirements
# garden_requirements =

# (str) Application versioning (method 1)
version = 0.1

# (list) Permissions
permissions = INTERNET, ACCESS_NETWORK_STATE

# (int) Target Android API, should be 33
android.api = 33

# (int) Minimum API supported
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (str) Android NDK API to use
android.ndk_api = 21

# (bool) Accept SDK license automatically
android.accept_sdk_license = True

# (list) The Android architectures to build for
android.archs = arm64-v8a

# (str) Android entrypoint, default is ok for Kivy-based app
android.entrypoint = org.kivy.android.PythonActivity

# (str) Android apptheme, default is ok for Kivy-based app
android.apptheme = @android:style/Theme.NoTitleBar

# (list) Pattern to whitelist or blacklist files
# android.whitelist =
# android.blacklist =

# (bool) Enable AndroidX support
android.enable_androidx = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = disable, 1 = enable)
warn_on_root = 1