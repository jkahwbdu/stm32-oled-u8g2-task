# -*- coding: utf-8 -*-
"""Decode the glyph list of a u8g2 font C file and check text coverage."""
import re, sys, codecs

def load_font_bytes(path):
    src = open(path, 'r', encoding='utf-8', errors='ignore').read()
    # grab the array initializer string chunks
    m = re.search(r'=\s*(.*?);\s*$', src, re.S | re.M)
    body = m.group(1) if m else src
    chunks = re.findall(r'"((?:[^"\\]|\\.)*)"', body)
    data = b''
    for c in chunks:
        # decode C octal/hex escapes
        b = codecs.escape_decode(c.encode('latin-1'))[0]
        data += b
    return data

def u16(d, o):
    return (d[o] << 8) | d[o + 1]

def main(path, texts):
    d = load_font_bytes(path)
    glyph_cnt = d[0]
    start_unicode = u16(d, 21)
    base = 23
    # ASCII glyphs
    p = base
    ascii_codes = []
    while True:
        if d[p + 1] == 0:
            break
        ascii_codes.append(d[p])
        p += d[p + 1]
    # unicode section
    sec = base + start_unicode
    table_size = u16(d, sec)
    p = sec + table_size
    uni = []
    while len(uni) < glyph_cnt - len(ascii_codes) and p + 3 <= len(d):
        e = u16(d, p)
        if e == 0:
            break
        size = d[p + 2]
        uni.append(e)
        p += size
    print('file:', path)
    print('glyph_cnt header:', glyph_cnt, 'ascii glyphs:', len(ascii_codes),
          'unicode glyphs:', len(uni))
    print('unicode chars:', ''.join(chr(c) for c in uni))
    # coverage check of strings passed on command line
    for s in texts:
        missing = sorted({ch for ch in s if ord(ch) > 127 and ord(ch) not in uni})
        print(f'text {s!r}: ' + ('OK' if not missing else 'MISSING ' + ''.join(missing)))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
