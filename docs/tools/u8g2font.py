# -*- coding: utf-8 -*-
"""Minimal decoder for u8g2 font C arrays + a tiny 1-bit canvas.

Used to (a) verify glyph coverage, (b) compose the marquee strip exactly as the
firmware's u8g2 fonts would render it, and (c) draw the report's screen mockups.
"""
import re
import codecs
from PIL import Image

U8G2_FONT_DATA_STRUCT_SIZE = 23


def _decode_c_string(body):
    out = b''
    for chunk in re.findall(r'"((?:[^"\\]|\\.)*)"', body):
        out += codecs.escape_decode(chunk.encode('latin-1'))[0]
    return out


class Font:
    def __init__(self, path, name=None):
        src = open(path, 'r', encoding='utf-8', errors='ignore').read()
        # the array initializer follows "U8G2_FONT_SECTION("...") ="
        m = re.search(r'U8G2_FONT_SECTION\([^)]*\)\s*=\s*', src)
        body = src[m.end():] if m else src
        self.data = _decode_c_string(body)
        d = self.data
        self.name = name or path
        self.glyph_cnt = d[0]
        self.bbx_mode = d[1]
        self.bits_per_0 = d[2]
        self.bits_per_1 = d[3]
        self.bits_w = d[4]
        self.bits_h = d[5]
        self.bits_x = d[6]
        self.bits_y = d[7]
        self.bits_d = d[8]
        self.max_w = d[9]
        self.max_h = d[10]
        self.x_offset = d[11]
        self.y_offset = d[12]
        self.ascent_A = d[13]
        self.descent_g = d[14]
        self.ascent_para = d[15]
        self.descent_para = d[16]
        self.pos_upper_A = self._u16(17)
        self.pos_lower_a = self._u16(19)
        self.pos_unicode = self._u16(21)

        self.glyphs = {}
        self._parse_ascii()
        self._parse_unicode()

    # ------------------------------------------------------------------ utils
    def _u16(self, off):
        return (self.data[off] << 8) | self.data[off + 1]

    class _Bits:
        def __init__(self, data):
            self.d = data
            self.pos = 0
            self.bit = 0

        def get(self, n):
            if n == 0:
                return 0
            if self.pos >= len(self.d):
                return 0
            v = self.d[self.pos] >> self.bit
            if self.bit + n >= 8:
                nxt = self.d[self.pos + 1] if self.pos + 1 < len(self.d) else 0
                v |= nxt << (8 - self.bit)
                self.pos += 1
            v &= (1 << n) - 1
            self.bit = (self.bit + n) % 8
            return v

    @staticmethod
    def _signed(v, n):
        return v - (1 << (n - 1))

    # ---------------------------------------------------------------- parsing
    def _parse_ascii(self):
        d = self.data
        p = U8G2_FONT_DATA_STRUCT_SIZE
        while True:
            size = d[p + 1]
            if size == 0:
                break
            enc = d[p]
            self.glyphs[enc] = self._decode(d[p + 2:p + size])
            p += size

    def _parse_unicode(self):
        d = self.data
        sec = U8G2_FONT_DATA_STRUCT_SIZE + self.pos_unicode
        table_size = self._u16_at(sec)
        p = sec + table_size
        while p + 3 <= len(d):
            enc = (d[p] << 8) | d[p + 1]
            if enc == 0:
                break
            size = d[p + 2]
            if size < 3:
                break
            self.glyphs[enc] = self._decode(d[p + 3:p + size])
            p += size

    def _u16_at(self, off):
        return (self.data[off] << 8) | self.data[off + 1]

    def _decode(self, data):
        br = self._Bits(data)
        w = br.get(self.bits_w)
        h = br.get(self.bits_h)
        gx = self._signed(br.get(self.bits_x), self.bits_x)
        gy = self._signed(br.get(self.bits_y), self.bits_y)
        adv = self._signed(br.get(self.bits_d), self.bits_d)
        bmp = [[0] * w for _ in range(h)]
        lx = ly = 0

        def run(length, color):
            nonlocal lx, ly
            cnt = length
            while True:
                rem = w - lx
                cur = cnt if cnt < rem else rem
                if color and ly < h:
                    for i in range(cur):
                        if 0 <= lx + i < w:
                            bmp[ly][lx + i] = 1
                if cnt < rem:
                    break
                cnt -= rem
                lx = 0
                ly += 1
                if ly >= h:
                    break
            lx += cnt

        guard = 0
        while guard < 4096:
            guard += 1
            a = br.get(self.bits_per_0)
            b = br.get(self.bits_per_1)
            while True:
                run(a, 0)
                run(b, 1)
                if br.get(1) == 0:
                    break
            if ly >= h:
                break
        return {'w': w, 'h': h, 'x': gx, 'y': gy, 'adv': adv, 'bmp': bmp}

    # ------------------------------------------------------------------- api
    def has(self, ch):
        return ord(ch) in self.glyphs

    def width(self, text):
        return sum(self.glyphs.get(ord(c), {'adv': 0})['adv'] for c in text)

    def draw(self, canvas, x, y, text, color=1, scale=1):
        """Draw UTF-8 text with its baseline at (x, y). scale=2 matches DrawUTF8X2."""
        pen = x
        for ch in text:
            g = self.glyphs.get(ord(ch))
            if g is None:
                continue
            left = pen + g['x']
            top = y - (g['h'] * scale + g['y'])
            for gy in range(g['h']):
                for gx in range(g['w']):
                    if g['bmp'][gy][gx]:
                        for sy in range(scale):
                            for sx in range(scale):
                                canvas.pixel(left + gx * scale + sx,
                                             top + gy * scale + sy, color)
            pen += g['adv'] * scale
        return pen


class Canvas:
    def __init__(self, w=128, h=64):
        self.w = w
        self.h = h
        self.px = [[0] * w for _ in range(h)]
        self.clip = (0, 0, w - 1, h - 1)

    def set_clip(self, x0, y0, x1, y1):
        self.clip = (x0, y0, x1, y1)

    def pixel(self, x, y, c=1):
        x0, y0, x1, y1 = self.clip
        if x0 <= x <= x1 and y0 <= y <= y1 and 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = c

    def hline(self, x, y, n, c=1):
        for i in range(n):
            self.pixel(x + i, y, c)

    def vline(self, x, y, n, c=1):
        for i in range(n):
            self.pixel(x, y + i, c)

    def box(self, x, y, w, h, c=1):
        for j in range(h):
            self.hline(x, y + j, w, c)

    def frame(self, x, y, w, h, c=1):
        self.hline(x, y, w, c)
        self.hline(x, y + h - 1, w, c)
        self.vline(x, y, h, c)
        self.vline(x + w - 1, y, h, c)

    def rbox(self, x, y, w, h, r, c=1):
        # crude rounded box: body + rounded corners
        self.box(x + r, y, w - 2 * r, h, c)
        self.box(x, y + r, r, h - 2 * r, c)
        self.box(x + w - r, y + r, r, h - 2 * r, c)

    def line(self, x0, y0, x1, y1, c=1):
        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.pixel(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c=1):
        x = r
        y = 0
        p = 1 - r
        while x >= y:
            for dx, dy in ((x, y), (y, x), (-y, x), (-x, y),
                           (-x, -y), (-y, -x), (y, -x), (x, -y)):
                self.pixel(cx + dx, cy + dy, c)
            y += 1
            if p <= 0:
                p += 2 * y + 1
            else:
                x -= 1
                p += 2 * (y - x) + 1

    def disc(self, cx, cy, r, c=1):
        for dy in range(-r, r + 1):
            w = int((r * r - dy * dy) ** 0.5)
            self.hline(cx - w, cy + dy, 2 * w + 1, c)

    def bitmap(self, x, y, w, h, bits, c=1):
        """bits: list of rows, each a list of 0/1."""
        for j in range(h):
            for i in range(w):
                if bits[j][i]:
                    self.pixel(x + i, y + j, c)

    def image(self, scale=4, border=False):
        im = Image.new('L', (self.w, self.h), 0)
        im.putdata([255 if v else 0 for row in self.px for v in row])
        if border:
            im = im.resize((self.w * scale, self.h * scale), Image.NEAREST)
        return im
