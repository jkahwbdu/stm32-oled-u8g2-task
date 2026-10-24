# -*- coding: utf-8 -*-
"""Draw the report diagrams (wiring, block, I2C timing, GDDRAM, flow)."""
import os

from PIL import Image, ImageDraw, ImageFont

IMG = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images'))
os.makedirs(IMG, exist_ok=True)

BLUE = (43, 108, 176)
DARK = (30, 41, 59)
GREY = (120, 130, 145)
LIGHT = (235, 241, 248)
RED = (200, 60, 60)
GREEN = (40, 140, 90)
YELLOW = (200, 150, 30)
BLACK = (20, 20, 20)


def font(size, bold=False):
    path = 'C:/Windows/Fonts/msyhbd.ttc' if bold else 'C:/Windows/Fonts/msyh.ttc'
    return ImageFont.truetype(path, size)


F14 = font(14)
F16 = font(16)
F18 = font(18, True)
F22 = font(22, True)
F12 = font(12)


def box(d, xy, text, fill=LIGHT, outline=BLUE, width=2, f=F16, sub=None):
    d.rounded_rectangle(xy, radius=8, fill=fill, outline=outline, width=width)
    x0, y0, x1, y1 = xy
    cx = (x0 + x1) / 2
    tw = d.textlength(text, font=f)
    top = (y0 + y1) / 2 - (26 if sub else 10)
    d.text((cx - tw / 2, top), text, font=f, fill=DARK)
    if sub:
        lines = sub.split('\n')
        y = top + 24
        for line in lines:
            sw = d.textlength(line, font=F12)
            d.text((cx - sw / 2, y), line, font=F12, fill=GREY)
            y += 17


def arrow(d, p0, p1, color=DARK, width=2, head=9):
    d.line([p0, p1], fill=color, width=width)
    import math
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    for s in (-0.5, 0.5):
        d.line([p1, (p1[0] - head * math.cos(ang + s), p1[1] - head * math.sin(ang + s))],
               fill=color, width=width)


def fig_wiring():
    im = Image.new('RGB', (1000, 580), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.text((30, 20), 'OLED 与 STM32F103C8T6 接线图（I2C1）', font=F22, fill=BLUE)

    # MCU board
    d.rounded_rectangle([60, 110, 320, 480], radius=12, fill=(28, 62, 110), outline=DARK, width=2)
    d.text((95, 130), 'STM32F103C8T6', font=F18, fill=(255, 255, 255))
    d.text((95, 158), '最小系统板 (Blue Pill)', font=F12, fill=(200, 220, 240))
    pins = [('3V3', 220, RED), ('GND', 265, BLACK), ('PB6  SCL', 310, YELLOW), ('PB7  SDA', 355, GREEN)]
    for name, y, col in pins:
        d.rectangle([298, y - 7, 320, y + 7], fill=(220, 200, 120), outline=DARK)
        d.text((150, y - 9), name, font=F14, fill=(255, 255, 255))

    # OLED
    d.rounded_rectangle([690, 160, 960, 430], radius=10, fill=(20, 30, 60), outline=DARK, width=2)
    d.rectangle([710, 185, 940, 340], fill=(5, 8, 15), outline=(90, 110, 150))
    d.text((745, 235), '0.96"  128x64', font=F16, fill=(180, 220, 255))
    d.text((785, 262), 'SSD1306', font=F14, fill=(140, 170, 210))
    oled_pins = [('VCC', 220, RED), ('GND', 265, BLACK), ('SCL', 310, YELLOW), ('SDA', 355, GREEN)]
    for name, y, col in oled_pins:
        d.rectangle([668, y - 7, 690, y + 7], fill=(220, 200, 120), outline=DARK)
        tw = d.textlength(name, font=F14)
        d.text((660 - tw, y - 22), name, font=F14, fill=DARK)

    for (name, y, col) in pins:
        d.line([(320, y), (668, y)], fill=col, width=4)
        d.text((440, y - 22), {'3V3': '3.3 V', 'GND': 'GND', 'PB6  SCL': 'SCL',
                               'PB7  SDA': 'SDA'}[name], font=F12, fill=col)

    # note
    d.text((30, 505), 'OLED 的 4 个引脚（模块丝印 GND / VCC / SCL / SDA）分别接 3V3、GND、PB6、PB7；'
                      '模块自带 4.7 kΩ 上拉。', font=F12, fill=GREY)
    d.text((30, 528), 'I2C1 速率 400 kHz，OLED 从机地址 0x3C（写 0x78）。', font=F12, fill=GREY)
    d.text((30, 551), '照片中的 OLED 尚未插线，按上图连接即可。', font=F12, fill=(180, 80, 40))
    im.save(os.path.join(IMG, 'fig_wiring.png'))




def fig_block():
    im = Image.new('RGB', (1000, 430), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.text((30, 20), '系统框图', font=F22, fill=BLUE)

    box(d, (390, 160, 610, 290), 'STM32F103C8T6', sub='Cortex-M3  72 MHz', f=F18)
    box(d, (760, 120, 960, 220), 'OLED 128x64', sub='SSD1306  0x3C', f=F16)
    box(d, (60, 120, 260, 220), 'DAP-Link', sub='SWD 下载/调试', f=F16)
    box(d, (60, 250, 260, 350), '3.3 V 电源', sub='VCC / GND', f=F16)

    arrow(d, (260, 170), (390, 200))
    d.text((285, 150), 'SWD', font=F12, fill=GREY)
    arrow(d, (260, 300), (390, 260))
    d.text((290, 300), '3.3V', font=F12, fill=GREY)
    arrow(d, (610, 190), (760, 165))
    d.text((640, 145), 'I2C1  PB6/PB7', font=F12, fill=BLUE)

    d.text((30, 390), '每帧先在 1 KB 显存中画好，再经硬件 I2C 整屏刷新；'
                      'PC13 板载 LED 作 1 Hz 心跳。', font=F12, fill=GREY)
    im.save(os.path.join(IMG, 'fig_block.png'))


def fig_i2c():
    im = Image.new('RGB', (1000, 430), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.text((30, 16), 'I2C 一次写传输的 SCL / SDA 波形（示意）', font=F22, fill=BLUE)

    x0 = 90
    cell = 28
    scl_y, sda_y = 150, 270
    hi = 34
    lo = 34

    # cell sequence: START preamble, 0x78 bits + ACK, 0x40 bits + ACK, 0xA5 bits + ACK, STOP
    levels = [1]                      # START preamble (SDA high, falls later)
    levels += [0, 1, 1, 1, 1, 0, 0, 0]  # 0x78
    levels += [0]                     # ACK
    levels += [0, 1, 0, 0, 0, 0, 0, 0]  # 0x40
    levels += [0]                     # ACK
    levels += [1, 0, 1, 0, 0, 1, 0, 1]  # 0xA5
    levels += [0]                     # ACK
    levels += [0]                     # STOP preamble

    def sx(i):
        return x0 + i * cell

    # SCL: low 8, high 14, low 6  (data stable while high)
    for i in range(len(levels)):
        x = sx(i)
        d.line([(x, scl_y + lo), (x + 8, scl_y + lo)], fill=BLUE, width=3)
        d.line([(x + 8, scl_y + lo), (x + 8, scl_y - hi)], fill=BLUE, width=3)
        d.line([(x + 8, scl_y - hi), (x + 22, scl_y - hi)], fill=BLUE, width=3)
        d.line([(x + 22, scl_y - hi), (x + 22, scl_y + lo)], fill=BLUE, width=3)
        d.line([(x + 22, scl_y + lo), (x + cell, scl_y + lo)], fill=BLUE, width=3)

    # SDA: level held from cell start to cell end, transition at start (SCL low)
    for i, lv in enumerate(levels):
        x = sx(i)
        y = sda_y - hi if lv else sda_y + lo
        d.line([(x, y), (x + cell, y)], fill=GREEN, width=3)

    # START: SDA falls while SCL is high in cell 0
    d.line([(sx(0) - 24, sda_y - hi), (sx(0) + 12, sda_y - hi)], fill=GREEN, width=3)
    d.line([(sx(0) + 12, sda_y - hi), (sx(0) + 12, sda_y + lo)], fill=GREEN, width=3)
    # STOP: SDA rises while SCL high in the last cell
    last = len(levels) - 1
    d.line([(sx(last), sda_y + lo), (sx(last) + 12, sda_y + lo)], fill=GREEN, width=3)
    d.line([(sx(last) + 12, sda_y + lo), (sx(last) + 12, sda_y - hi)], fill=GREEN, width=3)

    d.text((70, scl_y - hi - 28), 'SCL', font=F14, fill=BLUE)
    d.text((70, sda_y - hi - 28), 'SDA', font=F14, fill=GREEN)

    # group annotations
    def group(a, b, text):
        xa, xb = sx(a), sx(b)
        d.line([(xa, 345), (xb, 345)], fill=GREY, width=1)
        d.line([(xa, 340), (xa, 350)], fill=GREY, width=1)
        d.line([(xb, 340), (xb, 350)], fill=GREY, width=1)
        tw = d.textlength(text, font=F12)
        d.text(((xa + xb - tw) / 2, 355), text, font=F12, fill=DARK)

    d.text((sx(0) - 26, 355), 'START', font=F12, fill=DARK)
    group(1, 9, '地址 0x78（0x3C<<1 | W）')
    d.text((sx(9) + 2, 355), 'ACK', font=F12, fill=DARK)
    group(10, 18, '控制字节 0x40（数据）')
    d.text((sx(18) + 2, 355), 'ACK', font=F12, fill=DARK)
    group(19, 27, '数据字节 0xA5')
    d.text((sx(28) + 4, 355), 'STOP', font=F12, fill=DARK)

    d.text((30, 395), 'SCL 高电平期间 SDA 下降 = START，上升 = STOP；数据在 SCL 低电平期间改变、'
                      '高电平期间保持稳定。', font=F12, fill=GREY)
    im.save(os.path.join(IMG, 'fig_i2c.png'))


def fig_gddram():
    im = Image.new('RGB', (1000, 440), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.text((30, 16), 'SSD1306 显存（GDDRAM）组织：8 页 × 128 列 × 8 bit = 1024 B', font=F22, fill=BLUE)

    x0, y0 = 100, 90
    cw, ch = 6, 26
    W = 128 * cw
    for page in range(8):
        y = y0 + page * ch
        d.rectangle([x0, y, x0 + W, y + ch], fill=(235, 241, 248), outline=(170, 185, 205))
        for col in range(0, 129, 8):
            d.line([(x0 + col * cw, y), (x0 + col * cw, y + ch)], fill=(190, 205, 225))
        d.text((x0 - 76, y + 5), 'PAGE %d' % page, font=F12, fill=DARK)
        d.text((x0 + W + 10, y + 5), 'bit7 … bit0', font=F12, fill=GREY)

    # highlight one byte
    hx = x0 + 16 * cw
    hy = y0 + 2 * ch
    d.rectangle([hx, hy, hx + cw, hy + ch], fill=(255, 226, 150), outline=(200, 140, 30), width=2)
    d.line([(hx + cw, hy + ch / 2), (hx + 150, hy - 30)], fill=(200, 140, 30), width=2)
    d.text((hx + 155, hy - 48), '1 字节 = 该列 8 个垂直像素', font=F12, fill=(150, 100, 20))

    for col in (0, 32, 64, 96, 127):
        d.text((x0 + col * cw - 8, y0 + 8 * ch + 8), str(col), font=F12, fill=GREY)
    d.text((x0 + W / 2 - 70, y0 + 8 * ch + 30), '列地址 0…127', font=F12, fill=GREY)

    d.text((30, 400), '写 1 字节 = 点亮/熄灭同一列上的 8 个像素；整屏刷新 = 8 页 × 128 字节 = 1024 B。',
           font=F12, fill=GREY)
    im.save(os.path.join(IMG, 'fig_gddram.png'))


def fig_flow():
    im = Image.new('RGB', (1000, 640), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.text((30, 16), '程序流程', font=F22, fill=BLUE)

    box(d, (50, 60, 320, 150), '上电 / 复位', sub='HAL_Init()  SystemClock_Config()', f=F16)
    box(d, (50, 185, 320, 285), '外设与显示初始化', sub='MX_GPIO_Init  MX_I2C1_Init\nOLED_Init', f=F16)
    box(d, (50, 320, 320, 420), '主循环 App_Task()', sub='每 40 ms 处理一帧；PC13 1 Hz 心跳', f=F16)
    box(d, (400, 320, 670, 420), '合成当前页', sub='u8g2 显存 + OLED_Refresh()\n整屏一次写出 1024 B', f=F16)
    box(d, (750, 320, 960, 420), '本页时间到？', sub='是：切到下一展示页\n否：继续画', f=F16)

    arrow(d, (185, 150), (185, 185))
    arrow(d, (185, 285), (185, 320))
    arrow(d, (320, 370), (400, 370))
    arrow(d, (670, 370), (750, 370))

    # loop back arrow down/around to App_Task
    d.line([(855, 420), (855, 455), (185, 455), (185, 420)], fill=DARK, width=2)
    arrow(d, (185, 455), (185, 420))

    d.text((30, 480), '页面顺序：BOOT 1.5 s → ID 5 s → U8G2 5 s → 横向滚动 9.5 s '
                      '→ 纵向滚动 9 s → 头像 6 s → 循环。', font=F12, fill=GREY)
    d.text((30, 505), '每帧先在 RAM 中合成 128×64 单色位图，再用一次 u8g2_SendBuffer() 整屏刷新，'
                      '避免逐页刷新闪烁。', font=F12, fill=GREY)
    im.save(os.path.join(IMG, 'fig_flow.png'))


if __name__ == '__main__':
    fig_wiring()
    fig_block()
    fig_i2c()
    fig_gddram()
    fig_flow()
    print('figures written')
