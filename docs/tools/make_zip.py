# -*- coding: utf-8 -*-
"""Package the project + report into dist/OLED_U8g2_Task_632407030418.zip."""
import os
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DIST = os.path.join(ROOT, 'dist')
OUT = os.path.join(DIST, 'OLED_U8g2_Task_632407030418.zip')

EXCLUDE_DIRS = {'dist', '_pages', '_check', '_final', '__pycache__', '.git', 'Objects', 'Listings'}
EXCLUDE_EXT = {'.o', '.crf', '.d', '.dep', '.lnp', '.sct', '.htm', '.lst',
               '.map', '.iex', '.hex.bak', '.bak'}
EXCLUDE_FILES = {'build.log', 'JLinkLog.txt', '.mxproject.bak'}

# keep the .hex even though build products are excluded
KEEP = {'OLED_U8g2_Task.hex'}


def included(path, name):
    if name in EXCLUDE_FILES:
        return False
    if name in KEEP:
        return True
    ext = os.path.splitext(name)[1].lower()
    return ext not in EXCLUDE_EXT


def main():
    os.makedirs(DIST, exist_ok=True)
    if os.path.exists(OUT):
        os.remove(OUT)
    count = 0
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for base, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for f in files:
                full = os.path.join(base, f)
                if not included(full, f):
                    continue
                rel = os.path.relpath(full, ROOT)
                z.write(full, os.path.join('OLED_U8g2_Task', rel))
                count += 1
    size = os.path.getsize(OUT)
    print('zip: %s' % OUT)
    print('files: %d, size: %.2f MB' % (count, size / 1048576.0))


if __name__ == '__main__':
    main()
