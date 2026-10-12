[app]
title = Sistema CELEX
package.name = celexapp
package.domain = org.celex
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
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

# (list) List of inclusions
requirements = python3,kivy,kivymd,pg8000

version = 0.1
requirements = python3,kivy==2.3.1,kivymd==2.0.0,psycopg2-binary,requests,certifi,urllib3

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.sdk_build_tools_version = 33.0.2
android.accept_sdk_license = True
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
