import PyInstaller.__main__
import os
import sys

# Redirect stdout/stderr to file to capture build logs
sys.stdout = open('build_log.txt', 'w', encoding='utf-8')
sys.stderr = sys.stdout

print("Starting build with runtime mocks for eventlet and custom hooks...")

args = [
    'app.py',
    '--onefile',
    '--console',
    '--name=ChatBoot',
    '--add-data=templates;templates',
    '--add-data=static;static',
    '--hidden-import=engineio.async_drivers.threading',
    '--additional-hooks-dir=.',
    '--noconfirm',
    '--clean'
]

try:
    PyInstaller.__main__.run(args)
    print("Build finished successfully.")
except Exception as e:
    print(f"Build failed: {e}")
finally:
    sys.stdout.close()
