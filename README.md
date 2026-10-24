# OLED_U8g2_Task —— STM32F103C8T6 + 0.96" OLED + U8g2

第 6 周作业：在 STM32F103C8T6 上用 **硬件 I2C** 驱动 0.96 寸 SSD1306 OLED（128×64），
把 **U8g2** 裁剪、移植到 CubeMX + HAL 工程中，并完成五个展示页面（启动页 + 任务一/任务三的五个页面）。

> 姓名 / 学号：蒋俊熙 / 632407030418

## 显示效果

| 页面 | 内容 | 时间 |
| --- | --- | --- |
| BOOT | 边框、`U8g2`、芯片型号、进度条 | 1.5 s |
| ID CARD | 姓名（2 倍字号）+ 12 位学号 | 5 s |
| U8G2 DEMO | 文字、圆、圆盘、旋转线、柱状条 | 5 s |
| HELLO | 328 px 长句左右滚动 | 9.5 s |
| POEM | 《静夜思》上下滚动 | 9 s |
| AVATAR | 64×64 头像滑入 + 眨眼 | 6 s |

![页面总览](docs/images/screen_overview.png)

## 硬件连接

| OLED | STM32F103C8T6 | 说明 |
| --- | --- | --- |
| GND | GND | 共地 |
| VCC | 3V3 | 3.3 V，勿接 5 V |
| SCL | **PB6** | I2C1_SCL，开漏 + 上拉 |
| SDA | **PB7** | I2C1_SDA，开漏 + 上拉 |

- I2C1：**400 kHz**（CubeMX 默认 100 kHz，需在 `MX_I2C1_Init()` 里改），7 位地址，OLED 地址 **0x3C**（写 0x78）。
- 任务二（AHT20 温湿度）本次未做，代码中保留驱动与占位页；OLED 地址 0x3C。
- 下载：DAP-Link → SWD（3V3、GND、SWDIO-PA13、SWCLK-PA14）。
- 板载 LED：PC13，1 Hz 心跳。

![接线图](docs/images/fig_wiring.png)

## 目录结构

```text
OLED_U8g2_Task/
├── OLED_U8g2_Task.ioc          # CubeMX 配置（72 MHz / I2C1 400 kHz / PC13 LED）
├── Core/
│   ├── Inc/                    # app.h ui.h ui_assets.h ui_text.h oled_port.h（aht20.h 为任务二预留）
│   └── Src/                    # main.c app.c ui.c ui_assets.c oled_port.c（aht20.c 为任务二预留）
├── Middlewares/u8g2/           # 裁剪后的 u8g2（28 个 .c）+ fonts/
├── Drivers/                    # CMSIS + STM32F1xx HAL（FW_F1 V1.8.7）
├── MDK-ARM/                    # Keil 工程与编译产物（.hex/.axf）
└── docs/
    ├── STM32_OLED_U8g2实验报告.md / .pdf
    ├── images/
    └── tools/                  # 字库检查、字模/头像生成、界面渲染、插图脚本
```

## 编译

Keil MDK-ARM 5 打开 `MDK-ARM/OLED_U8g2_Task.uvprojx`，F7 编译。命令行：

```powershell
$uv = 'C:\Users\Administrator\Desktop\STM\UV4\UV4.exe'
Start-Process $uv -ArgumentList @('-r', 'MDK-ARM\OLED_U8g2_Task.uvprojx',
                                  '-j0', '-o', 'build.log') -Wait
```

当前结果：**0 Error(s), 0 Warning(s)**，
`Code=15358  RO-data=8374  RW-data=52  ZI-data=3340`
（Flash ≈ 23.2 KB / 64 KB，RAM ≈ 3.3 KB / 20 KB）。

烧录产物：`MDK-ARM/OLED_U8g2_Task/OLED_U8g2_Task.hex`。已在实物上验证：DAP-Link 烧录后 ID CARD 正常显示，五个展示页循环、长句滚动、诗句滚动和头像动画均正常。

## 实现要点

1. **u8g2 移植**：全屏缓冲模式 `u8g2_Setup_ssd1306_i2c_128x64_noname_f`，1 KB 显存；
   `Oled_ByteCb` 把 u8x8 的 START/SEND/END 合并成一次 `HAL_I2C_Master_Transmit`。
2. **整屏刷新**：每帧先画显存，再 `u8g2_SendBuffer()` 用硬件 I2C 一次写出 1024 B；
   400 kHz 下一帧约 25 ms，帧间隔 40 ms（25 fps）。
3. **长句滚动**：整句预渲染成 328×16 的页格式字模条（656 B Flash），按列偏移直接写显存，
   支持任意负偏移；竖滚动用 u8g2 文本 + `u8g2_SetClipWindow()`。
4. **字库裁剪**：只保留 141 个字形（95 ASCII + 46 汉字），3.3 KB；界面文字必须落在子集内。
5. **中文编码**：ARMCC 按 GBK 读源码，UTF-8 汉字会吞引号；因此 C 源码保持 ASCII，
   中文由 `docs/tools/gen_text.py` 生成 `ui_text.h` 的 `\xHH` 转义。
6. **任务二预留**：AHT20 驱动与占位页保留在工程中，本次无传感器，不计入演示与报告。

## 文档与工具

- 实验报告：[`docs/STM32_OLED_U8g2实验报告.pdf`](docs/STM32_OLED_U8g2实验报告.pdf)
  （源码：[`.md`](docs/STM32_OLED_U8g2实验报告.md)）
- `docs/tools/fontcheck.py`：检查界面文本是否被字库覆盖
- `docs/tools/gen_assets.py`：生成 64×64 头像与 328×16 滚动字模条
- `docs/tools/render_screens.py`：用真实字库渲染界面图（报告插图）
- `docs/tools/make_figs.py`：生成接线图、框图、I2C 时序图、流程图
- `docs/tools/make_hw_fig.py`：裁剪实机照片并拼成 2×2 证据图
- `docs/tools/make_zip.py`：打包 dist/ 提交 zip

## 提交说明

作业要求提交：工程 zip、实验报告（Markdown + PDF）、博客地址。
仓库根目录已包含工程与报告；`dist/` 下的 zip 可直接上传学习通。
博客可参考报告第八节“思考题”整理（Keil 逻辑分析仪为什么抓不到 I2C、如何用逻辑分析仪/示波器验证）。
