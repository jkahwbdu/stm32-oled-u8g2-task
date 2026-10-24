# -*- coding: utf-8 -*-
"""Crop the four on-hardware OLED photos and build a 2x2 evidence figure."""
import os

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

TX = r'C:\Users\Administrator\Desktop\tx'
IMG = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images'))

SRC = [
    ('AD7979CC0E3D23F535076C167CF432B8.jpg', 'hw_idcard.jpg', 'ID CARD：学号 + 姓名',
     (330, 830, 710, 1250)),
    ('410214285B5254B9DD7EDDD8C6F39A03.jpg', 'hw_u8g2.jpg', 'U8G2 DEMO：图形演示',
     (330, 830, 710, 1250)),
    ('96D18330D8B4DB63825DD413293FE729.jpg', 'hw_marquee.jpg', 'HELLO：长句左右滚动',
     (330, 830, 710, 1250)),
    ('28FD6A657B0A582D97D45D408C36C779.jpg', 'hw_avatar.jpg', 'AVATAR：头像 + 姓名',
     (480, 900, 860, 1320)),
]

CELL = (600, 663)
GAP = 14
CAP_H = 34


def main():
    cells = []
    for src, dst, cap, box in SRC:
        im = Image.open(os.path.join(TX, src)).convert('RGB').crop(box)
        im = im.resize(CELL, Image.LANCZOS)
        im = ImageEnhance.Brightness(im).enhance(1.08)
        im = ImageEnhance.Contrast(im).enhance(1.05)
        im.save(os.path.join(IMG, dst), quality=92)
        cells.append((im, cap))

    cols, rows = 2, 2
    W = cols * CELL[0] + (cols + 1) * GAP
    H = rows * (CELL[1] + CAP_H) + (rows + 1) * GAP
    out = Image.new('RGB', (W, H), (255, 255, 255))
    d = ImageDraw.Draw(out)
    try:
        font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 22)
    except Exception:
        font = ImageFont.load_default()

    for i, (im, cap) in enumerate(cells):
        r, c = divmod(i, cols)
        x = GAP + c * (CELL[0] + GAP)
        y = GAP + r * (CELL[1] + CAP_H + GAP)
        out.paste(im, (x, y))
        d.rectangle([x, y, x + CELL[0] - 1, y + CELL[1] - 1], outline=(190, 200, 215))
        tw = d.textlength(cap, font=font)
        d.text((x + (CELL[0] - tw) / 2, y + CELL[1] + 6), cap, font=font, fill=(30, 41, 59))

    p = os.path.join(IMG, 'hw_screens.jpg')
    out.save(p, quality=92)
    print('wrote', p, out.size)


if __name__ == '__main__':
    main()
