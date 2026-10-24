# -*- coding: utf-8 -*-
"""Markdown -> printable HTML (A4) for the lab report."""
import os
import re
import sys

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.abspath(os.path.join(HERE, '..'))
MD = os.path.join(DOCS, 'STM32_OLED_U8g2实验报告.md')
HTML = os.path.join(DOCS, 'STM32_OLED_U8g2实验报告.html')

CSS = """
@page { size: A4; margin: 16mm 14mm; }
body { font-family: "Microsoft YaHei", "微软雅黑", "PingFang SC", sans-serif;
       font-size: 10.5pt; line-height: 1.75; color: #222; margin: 0; }
h1 { font-size: 19pt; color: #1a365d; border-bottom: 3px solid #2b6cb0;
     padding-bottom: 8px; margin: 0 0 18px 0; }
h2 { font-size: 15pt; color: #2b6cb0; margin: 24px 0 10px 0;
     border-left: 5px solid #2b6cb0; padding-left: 10px; page-break-after: avoid; }
h3 { font-size: 12.5pt; color: #2c5282; margin: 16px 0 8px 0; page-break-after: avoid; }
h4 { font-size: 11pt; color: #2c5282; margin: 12px 0 6px 0; page-break-after: avoid; }
p { margin: 8px 0; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 9.6pt;
        page-break-inside: auto; }
table.keep { page-break-inside: avoid; }
tr { page-break-inside: avoid; }
th, td { border: 1px solid #b8c4d4; padding: 5px 9px; text-align: left; vertical-align: top; }
th { background: #eef3fa; font-weight: 600; }
code { font-family: Consolas, "Courier New", monospace; background: #f2f5f8;
       padding: 1px 5px; border-radius: 3px; font-size: 0.94em; color: #b03060; }
pre { background: #f6f8fa; border: 1px solid #dde3ea; border-radius: 5px;
      padding: 10px 12px; overflow-x: auto; page-break-inside: avoid;
      font-size: 9pt; line-height: 1.45; }
pre code { background: none; padding: 0; color: #24292e; }
blockquote { border-left: 4px solid #cbd5e0; margin: 10px 0; padding: 7px 14px;
             background: #f8fafc; color: #3d4852; page-break-inside: avoid; }
blockquote p { margin: 4px 0; }
img { max-width: 100%; max-height: 112mm; width: auto; height: auto;
      display: block; margin: 12px auto; page-break-inside: avoid; }
img[src*="screen_"] { width: 72%; }
img[src*="marquee_strip"] { width: 86%; }
img[src*="hw_screens"] { width: 80%; max-height: none; }
em { color: #4a5568; }
hr { border: none; border-top: 1px solid #e2e8f0; margin: 22px 0; }
ul, ol { padding-left: 26px; }
li { margin: 4px 0; }
a { color: #2b6cb0; text-decoration: none; }
"""


def main():
    src = open(MD, encoding='utf-8').read()
    body = markdown.markdown(
        src,
        extensions=['tables', 'fenced_code', 'sane_lists', 'nl2br'],
        output_format='html5',
    )
    # small tables should not be split across pages; long ones must be allowed to
    def keep_small(m):
        block = m.group(0)
        if block.count('<tr') <= 6:
            return block.replace('<table>', '<table class="keep">', 1)
        return block
    body = re.sub(r'<table>.*?</table>', keep_small, body, flags=re.S)
    html = (
        '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
        '<title>STM32 OLED 显示与 U8g2 移植实验报告</title>\n'
        '<style>%s</style>\n</head>\n<body>\n%s\n</body>\n</html>\n' % (CSS, body)
    )
    open(HTML, 'w', encoding='utf-8', newline='\n').write(html)
    print('html written:', HTML)


if __name__ == '__main__':
    main()
