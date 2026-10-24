# -*- coding: utf-8 -*-
"""Add the u8g2 sources + application files to the Keil project (idempotent)."""
import re
import sys

PROJ = r'C:\Users\Administrator\Desktop\STM\work\6\MDK-ARM\OLED_U8g2_Task.uvprojx'

groups = [
    ('Application/User/App', [
        '../Core/Src/app.c',
        '../Core/Src/ui.c',
        '../Core/Src/ui_assets.c',
        '../Core/Src/oled_port.c',
        '../Core/Src/aht20.c',
    ]),
    ('Middlewares/u8g2', [
        '../Middlewares/u8g2/u8g2_arc.c',
        '../Middlewares/u8g2/u8g2_bitmap.c',
        '../Middlewares/u8g2/u8g2_box.c',
        '../Middlewares/u8g2/u8g2_buffer.c',
        '../Middlewares/u8g2/u8g2_circle.c',
        '../Middlewares/u8g2/u8g2_cleardisplay.c',
        '../Middlewares/u8g2/u8g2_d_memory.c',
        '../Middlewares/u8g2/u8g2_d_setup.c',
        '../Middlewares/u8g2/u8g2_font.c',
        '../Middlewares/u8g2/u8g2_hvline.c',
        '../Middlewares/u8g2/u8g2_kerning.c',
        '../Middlewares/u8g2/u8g2_intersection.c',
        '../Middlewares/u8g2/u8g2_line.c',
        '../Middlewares/u8g2/u8g2_ll_hvline.c',
        '../Middlewares/u8g2/u8g2_setup.c',
        '../Middlewares/u8g2/u8x8_8x8.c',
        '../Middlewares/u8g2/u8x8_byte.c',
        '../Middlewares/u8g2/u8x8_capture.c',
        '../Middlewares/u8g2/u8x8_cad.c',
        '../Middlewares/u8g2/u8x8_d_ssd1306_128x64_noname.c',
        '../Middlewares/u8g2/u8x8_display.c',
        '../Middlewares/u8g2/u8x8_gpio.c',
        '../Middlewares/u8g2/u8x8_setup.c',
        '../Middlewares/u8g2/u8x8_u16toa.c',
        '../Middlewares/u8g2/u8x8_u8toa.c',
    ]),
    ('Middlewares/u8g2/fonts', [
        '../Middlewares/u8g2/fonts/u8g2_font_7x14B_ascii.c',
        '../Middlewares/u8g2/fonts/u8g2_font_10x20_ascii.c',
        '../Middlewares/u8g2/fonts/u8g2_font_wqy12_cn.c',
    ]),
]

src = open(PROJ, 'r', encoding='utf-8').read()

# 1) include paths
inc = '../Core/Inc;../Drivers/STM32F1xx_HAL_Driver/Inc;../Drivers/STM32F1xx_HAL_Driver/Inc/Legacy;../Drivers/CMSIS/Device/ST/STM32F1xx/Include;../Drivers/CMSIS/Include'
inc_new = inc + ';../Middlewares/u8g2;../Middlewares/u8g2/fonts'
if '../Middlewares/u8g2' not in src:
    assert inc in src, 'include path line not found'
    src = src.replace(inc, inc_new, 1)

# 2) groups: rebuild the three groups if they already exist
def build_group(name, files):
    out = ['        <Group>', '          <GroupName>%s</GroupName>' % name, '          <Files>']
    for f in files:
        base = f.rsplit('/', 1)[-1]
        out += ['            <File>',
                '              <FileName>%s</FileName>' % base,
                '              <FileType>1</FileType>',
                '              <FilePath>%s</FilePath>' % f,
                '            </File>']
    out += ['          </Files>', '        </Group>']
    return '\n'.join(out)

for name, files in groups:
    # drop an existing group with the same name (non-greedy up to </Group>)
    pattern = re.compile(r'\s*<Group>\s*<GroupName>%s</GroupName>.*?</Group>' % re.escape(name), re.S)
    src = pattern.sub('', src)

snippet = '\n'.join(build_group(n, f) for n, f in groups)
idx = src.rindex('      </Groups>')
src = src[:idx] + snippet + '\n' + src[idx:]

open(PROJ, 'w', encoding='utf-8', newline='\r\n').write(src)
print('project updated: %d groups, include path ok' % len(groups))
