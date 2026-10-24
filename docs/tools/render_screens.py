# -*- coding: utf-8 -*-
"""Render the six OLED pages with the real u8g2 fonts.

The drawing code mirrors Core/Src/ui.c coordinate for coordinate, so the PNGs
are what the panel shows (the only difference is line/circle rasterisation,
which u8g2 does with its own algorithms).

Writes docs/images/screen_*.png and screen_overview.png.
"""
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from u8g2font import Font, Canvas  # noqa: E402

IMG = os.path.join(ROOT, 'docs', 'images')
FONTS = os.path.join(ROOT, 'Middlewares', 'u8g2', 'fonts')

W, H = 128, 64
f_small = Font(os.path.join(FONTS, 'u8g2_font_7x14B_ascii.c'))
f_big = Font(os.path.join(FONTS, 'u8g2_font_10x20_ascii.c'))
f_cn = Font(os.path.join(FONTS, 'u8g2_font_wqy12_cn.c'))

TXT_NAME = '蒋俊熙'
TXT_ID = '632407030418'
TXT_TEMP = '温度'
TXT_HUM = '湿度'
TXT_ROOM = '物联网205'
POEM = ['床前明月光', '疑是地上霜', '举头望明月', '低头思故乡']


# ---------------------------------------------------------------- C assets
def read_array(path, name):
    src = open(path, encoding='utf-8').read()
    m = re.search(r'%s\[[^\]]*\]\s*=\s*\{(.*?)\};' % re.escape(name), src, re.S)
    return [int(v, 16) for v in re.findall(r'0x([0-9A-Fa-f]{2})', m.group(1))]


ASSETS = os.path.join(ROOT, 'Core', 'Src', 'ui_assets.c')
AVATAR = read_array(ASSETS, 'ui_avatar_64x64')
MARQ_W = int(re.search(r'ui_marquee_width\s*=\s*(\d+)', open(ASSETS).read()).group(1))
MARQ = read_array(ASSETS, 'ui_marquee_strip')


# ----------------------------------------------------------------- helpers
def title(c, text, page):
    c.set_clip(0, 0, 127, 63)
    f_small.draw(c, 2, 10, text)
    for i in range(6):
        x = 96 + i * 5
        if i == page:
            c.box(x, 4, 3, 4)
        else:
            c.pixel(x + 1, 6)
    c.hline(0, 12, 128)


def center_cn(c, y, s):
    w = f_cn.width(s)
    f_cn.draw(c, (128 - w) // 2, y, s)


def bar(c, y, pct):
    c.frame(0, y, 128, 5)
    pct = max(0, min(100, pct))
    if pct:
        c.box(1, y + 1, 126 * pct // 100, 3)


def fmt1(v10):
    if v10 >= 1000:
        return '100.0'
    return '%02d.%d' % (v10 // 10, v10 % 10)


# ------------------------------------------------------------------- pages
def page_boot(t=900):
    c = Canvas()
    c.frame(1, 1, 126, 62)
    f_big.draw(c, 44, 32, 'U8g2')
    f_small.draw(c, 18, 48, 'STM32F103C8T6')
    c.hline(2, 57, 124)
    c.box(2, 56, min(16 + t // 12, 124), 3)
    return c


def page_id(t=0):
    c = Canvas()
    title(c, 'ID CARD', 0)
    f_cn.draw(c, (128 - f_cn.width(TXT_NAME) * 2) // 2, 44, TXT_NAME, scale=2)
    w = f_big.width(TXT_ID)
    f_big.draw(c, (128 - w) // 2, 62, TXT_ID)
    return c


def page_u8g2(t=800):
    c = Canvas()
    title(c, 'U8G2 DEMO', 1)
    f_big.draw(c, 2, 34, 'U8g2')
    f_small.draw(c, 2, 50, 'STM32F103')
    r = 7 + (t // 160) % 6
    d = (t // 120) % 16
    c.circle(103, 30, r)
    c.disc(103, 30, 2)
    angle = d * 22.5
    import math
    c.line(103, 30, int(103 + 16 * math.cos(math.radians(angle))),
           int(30 + 16 * math.sin(math.radians(angle))))
    for i in range(6):
        h = 2 + ((t // 90 + i * 3) % 7)
        c.box(4 + i * 6, 62 - h, 4, h)
    return c


def page_aht(temp=26.3, hum=58.7, ok=True, t=0):
    c = Canvas()
    title(c, 'AHT20' if ok else 'AHT20 SIM', 2)
    f_cn.draw(c, 2, 30, TXT_TEMP)
    f_cn.draw(c, 2, 54, TXT_HUM)
    t10 = int(temp * 10 + 0.5)
    h10 = int(hum * 10 + 0.5)
    f_big.draw(c, 48, 32, fmt1(t10) + ' C')
    f_big.draw(c, 48, 56, fmt1(h10) + ' %')
    bar(c, 34, min(100, t10 * 100 // 500))
    bar(c, 58, min(100, h10 // 10))
    return c


def page_marquee(t=2600):
    c = Canvas()
    title(c, 'HELLO', 3)
    x0 = 128 - (t * 60 // 1000) % (MARQ_W + 128)
    for x in range(MARQ_W):
        dx = x + x0
        if 0 <= dx < 128:
            b0 = MARQ[x * 2]
            b1 = MARQ[x * 2 + 1]
            for bit in range(8):
                if b0 & (1 << bit):
                    c.pixel(dx, 32 + bit)
                if b1 & (1 << bit):
                    c.pixel(dx, 40 + bit)
    f_cn.draw(c, 2, 61, TXT_ROOM)
    f_small.draw(c, 98, 61, 'U8g2')
    return c


def page_poem(t=1200):
    c = Canvas()
    title(c, 'POEM', 4)
    c.set_clip(0, 13, 127, 63)
    off = (t * 20 // 1000) % 72
    for i in range(-1, 5):
        y = 27 + i * 18 - off
        idx = i % 4
        if 27 <= y <= 70:
            center_cn(c, y, POEM[idx])
    c.set_clip(0, 0, 127, 63)
    return c


def page_avatar(t=2600):
    c = Canvas()
    x = 128 - t * 128 // 600 if t < 600 else 0
    for row in range(64):
        for xb in range(8):
            b = AVATAR[row * 8 + xb]
            for bit in range(8):
                if b & (1 << bit):
                    c.pixel(x + xb * 8 + bit, row)
    c.vline(66, 4, 56)
    f_cn.draw(c, 70, 22, TXT_NAME)
    f_small.draw(c, 70, 38, '632407')
    f_small.draw(c, 70, 52, '030418')
    if x == 0 and 2200 < t % 2400 < 2360:
        c.hline(21, 35, 8, 0)
        c.hline(35, 35, 8, 0)
    return c


# ------------------------------------------------------------------- main
PAGES = [
    ('boot', '启动画面 Boot', lambda: page_boot(900)),
    ('id', '学号与姓名 ID CARD', lambda: page_id()),
    ('u8g2', 'U8g2 图形演示 U8G2 DEMO', lambda: page_u8g2(800)),
    ('aht', '温湿度 AHT20', lambda: page_aht(26.3, 58.7, True)),
    ('aht_sim', '未接传感器时的 AHT20 SIM', lambda: page_aht(26.3, 58.7, False)),
    ('marquee', '左右滚动 HELLO', lambda: page_marquee(2600)),
    ('poem', '上下滚动 POEM', lambda: page_poem(900)),
    ('avatar', '头像 AVATAR', lambda: page_avatar(2600)),
]


def render_one(c, scale=4):
    im = Image.new('L', (W, H), 0)
    im.putdata([255 if v else 0 for row in c.px for v in row])
    return im.resize((W * scale, H * scale), Image.NEAREST)


def main():
    imgs = {}
    for key, label, fn in PAGES:
        c = fn()
        im = render_one(c)
        p = os.path.join(IMG, 'screen_%s.png' % key)
        im.save(p)
        imgs[key] = im
        print('wrote', p)

    # overview 3x2 with labels
    keys = ['boot', 'id', 'u8g2', 'marquee', 'poem', 'avatar']
    labels = dict((k, l) for k, l, _ in PAGES)
    cell_w, cell_h = 128 * 3, 64 * 3
    pad = 10
    try:
        font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 14)
    except Exception:
        font = ImageFont.load_default()
    cols, rows = 2, 3
    canvas = Image.new('RGB', (cols * (cell_w + pad) + pad,
                               rows * (cell_h + 24 + pad) + pad), (255, 255, 255))
    d = ImageDraw.Draw(canvas)
    for i, k in enumerate(keys):
        r, col = divmod(i, cols)
        x = pad + col * (cell_w + pad)
        y = pad + r * (cell_h + 24 + pad)
        canvas.paste(imgs[k].resize((cell_w, cell_h), Image.NEAREST).convert('RGB'), (x, y))
        d.text((x, y + cell_h + 2), labels[k], fill=(20, 20, 20), font=font)
    out = os.path.join(IMG, 'screen_overview.png')
    canvas.save(out)
    print('wrote', out)

    # dot-matrix detail of one Chinese glyph
    g = f_cn.glyphs[ord('蒋')]
    scale = 14
    gw, gh = g['w'], g['h']
    im = Image.new('RGB', ((gw + 2) * scale, (gh + 2) * scale), (255, 255, 255))
    d = ImageDraw.Draw(im)
    for yy in range(gh + 1):
        d.line([(scale, (yy + 1) * scale), ((gw + 1) * scale, (yy + 1) * scale)], fill=(210, 220, 235))
    for xx in range(gw + 1):
        d.line([((xx + 1) * scale, scale), ((xx + 1) * scale, (gh + 1) * scale)], fill=(210, 220, 235))
    for yy in range(gh):
        for xx in range(gw):
            if g['bmp'][yy][xx]:
                d.rectangle([(xx + 1) * scale + 1, (yy + 1) * scale + 1,
                             (xx + 2) * scale - 1, (yy + 2) * scale - 1], fill=(20, 40, 80))
    im.save(os.path.join(IMG, 'font_glyph.png'))
    print('wrote font_glyph.png (%dx%d)' % (gw, gh))


if __name__ == '__main__':
    main()
