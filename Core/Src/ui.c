/**
  ******************************************************************************
  * @file    ui.c
  * @brief   Six demo pages for the 0.96" SSD1306 (128x64) on I2C1
  *
  *   page 0  ID CARD    name (double size) + student number
  *   page 1  U8G2 DEMO  text + moving circle/line (u8g2 geometry demo)
  *   page 2  AHT20      temperature / humidity + bars (SIM tag w/o sensor)
  *   page 3  HELLO      long Chinese sentence, left-right marquee
  *   page 4  POEM       four lines, bottom-up scrolling
  *   page 5  AVATAR     64x64 bitmap, slide-in + blink animation
  *
  *   All Chinese glyphs come from the trimmed wqy12 font (see docs/).
  ******************************************************************************
  */

#include "ui.h"
#include "ui_assets.h"
#include "ui_text.h"
#include <string.h>

/* Fonts compiled into the project (Middlewares/u8g2/fonts). */
extern const uint8_t u8g2_font_7x14B_ascii[];
extern const uint8_t u8g2_font_10x20_ascii[];
extern const uint8_t u8g2_font_wqy12_cn[];

#define UI_W            128U
#define UI_H            64U
#define UI_PAGE_COUNT   6U

/* Strings shown on the panel.  Keep every character inside the trimmed font
   (docs/tools/fontcheck.py can verify the coverage). */
#define UI_ID           "632407030418"

static const char *const kPoem[4] =
{
  UI_TXT_POEM0, UI_TXT_POEM1, UI_TXT_POEM2, UI_TXT_POEM3
};

/* 16 directions for the rotating line on the u8g2 demo page */
static const int8_t kDirX[16] =
{
  16, 15, 11, 6, 0, -6, -11, -15, -16, -15, -11, -6, 0, 6, 11, 15
};
static const int8_t kDirY[16] =
{
  0, 6, 11, 15, 16, 15, 11, 6, 0, -6, -11, -15, -16, -15, -11, -6
};

/* ------------------------------------------------------------------ helpers */

/**
  * @brief  Page title (small ASCII font) + page indicator dots.
  * @param  page 0..5, or 0xFF to hide the dots
  */
static void UI_Title(u8g2_t *u8g2, const char *title, uint8_t page)
{
  uint8_t i;

  u8g2_SetFont(u8g2, u8g2_font_7x14B_ascii);
  u8g2_DrawStr(u8g2, 2, 10, title);

  if (page < UI_PAGE_COUNT)
  {
    for (i = 0U; i < UI_PAGE_COUNT; i++)
    {
      uint8_t x = (uint8_t)(96U + i * 5U);
      if (i == page)
      {
        u8g2_DrawBox(u8g2, x, 4, 3, 4);
      }
      else
      {
        u8g2_DrawPixel(u8g2, x + 1, 6);
      }
    }
  }
  u8g2_DrawHLine(u8g2, 0, 12, UI_W);
}

/**
  * @brief  Draw a UTF-8 string horizontally centred on the 128 px panel.
  */
static void UI_CenterUtf8(u8g2_t *u8g2, uint8_t y, const char *s)
{
  u8g2_uint_t w = u8g2_GetUTF8Width(u8g2, s);

  if (w >= UI_W)
  {
    u8g2_DrawUTF8(u8g2, 0, y, s);
  }
  else
  {
    u8g2_DrawUTF8(u8g2, (u8g2_uint_t)((UI_W - w) / 2U), y, s);
  }
}

/**
  * @brief  Fixed point formatter: value*10 -> "25.6" (0..100.0).
  */
static void UI_Fmt1(char *out, int16_t v10)
{
  if (v10 < 0)
  {
    v10 = 0;
  }
  if (v10 >= 1000)
  {
    out[0] = '1'; out[1] = '0'; out[2] = '0'; out[3] = '.'; out[4] = '0';
    out[5] = '\0';
    return;
  }
  out[0] = (char)('0' + (v10 / 100) % 10);
  out[1] = (char)('0' + (v10 / 10) % 10);
  out[2] = '.';
  out[3] = (char)('0' + (v10 % 10));
  out[4] = '\0';
}

/**
  * @brief  Horizontal gauge: 1 px frame with a 3 px filled bar inside.
  */
static void UI_Bar(u8g2_t *u8g2, uint8_t y, uint8_t percent)
{
  u8g2_DrawFrame(u8g2, 0, y, UI_W, 5);

  if (percent > 100U)
  {
    percent = 100U;
  }
  if (percent > 0U)
  {
    u8g2_DrawBox(u8g2, 1, (u8g2_uint_t)(y + 1U),
                 (u8g2_uint_t)((126U * percent) / 100U), 3);
  }
}

/**
  * @brief  Blit the 328x16 marquee strip into the u8g2 framebuffer at x0.
  *
  *   The strip is stored in SSD1306 page format (2 bytes per column), so it can
  *   be copied straight into the full-screen buffer - this is what allows a
  *   sentence much wider than the panel to scroll smoothly.  Page 4/5 = y 32..47.
  */
static void UI_MarqueeStrip(u8g2_t *u8g2, int16_t x0)
{
  uint8_t *buf = u8g2_GetBufferPtr(u8g2);
  uint16_t x;

  for (x = 0U; x < ui_marquee_width; x++)
  {
    int16_t dx = (int16_t)x + x0;

    if ((dx < 0) || (dx >= (int16_t)UI_W))
    {
      continue;
    }
    buf[4U * 128U + (uint16_t)dx] = ui_marquee_strip[x * 2U];
    buf[5U * 128U + (uint16_t)dx] = ui_marquee_strip[x * 2U + 1U];
  }
}

/* ------------------------------------------------------------------- pages */

void UI_Boot(u8g2_t *u8g2, uint16_t t)
{
  uint16_t w = (uint16_t)(16U + (uint32_t)t / 12U);

  if (w > (UI_W - 4U))
  {
    w = UI_W - 4U;
  }

  u8g2_DrawFrame(u8g2, 1, 1, UI_W - 2U, UI_H - 2U);

  u8g2_SetFont(u8g2, u8g2_font_10x20_ascii);
  u8g2_DrawStr(u8g2, 44, 32, "U8g2");

  u8g2_SetFont(u8g2, u8g2_font_7x14B_ascii);
  u8g2_DrawStr(u8g2, 18, 48, "STM32F103C8T6");

  /* progress line under the text */
  u8g2_DrawHLine(u8g2, 2, 57, UI_W - 4U);
  u8g2_DrawBox(u8g2, 2, 56, w, 3);
}

void UI_IdCard(u8g2_t *u8g2, uint16_t t)
{
  u8g2_uint_t w;

  (void)t;

  UI_Title(u8g2, "ID CARD", 0U);

  u8g2_SetFont(u8g2, u8g2_font_wqy12_cn);
  w = u8g2_GetUTF8Width(u8g2, UI_TXT_NAME) * 2U;
  u8g2_DrawUTF8X2(u8g2, (u8g2_uint_t)((UI_W - w) / 2U), 44, UI_TXT_NAME);

  u8g2_SetFont(u8g2, u8g2_font_10x20_ascii);
  w = u8g2_GetUTF8Width(u8g2, UI_ID);
  u8g2_DrawStr(u8g2, (u8g2_uint_t)((UI_W - w) / 2U), 62, UI_ID);
}

void UI_U8g2Demo(u8g2_t *u8g2, uint16_t t)
{
  uint8_t  r = (uint8_t)(7U + ((t / 160U) % 6U));
  uint8_t  dir = (uint8_t)((t / 120U) % 16U);
  uint8_t  i;

  UI_Title(u8g2, "U8G2 DEMO", 1U);

  u8g2_SetFont(u8g2, u8g2_font_10x20_ascii);
  u8g2_DrawStr(u8g2, 2, 34, "U8g2");

  u8g2_SetFont(u8g2, u8g2_font_7x14B_ascii);
  u8g2_DrawStr(u8g2, 2, 50, "STM32F103");

  /* animated geometry on the right half */
  u8g2_DrawCircle(u8g2, 103, 30, r, U8G2_DRAW_ALL);
  u8g2_DrawDisc(u8g2, 103, 30, 2, U8G2_DRAW_ALL);
  u8g2_DrawLine(u8g2, 103, 30,
                (u8g2_uint_t)(103 + kDirX[dir]),
                (u8g2_uint_t)(30 + kDirY[dir]));

  /* small "equalizer" made of 6 boxes, phase shifted */
  for (i = 0U; i < 6U; i++)
  {
    uint8_t h = (uint8_t)(2U + ((t / 90U + i * 3U) % 7U));
    u8g2_DrawBox(u8g2, (u8g2_uint_t)(4U + i * 6U), (u8g2_uint_t)(62U - h), 4, h);
  }
}

void UI_Aht20(u8g2_t *u8g2, float temperature, float humidity,
              uint8_t sensor_ok, uint16_t t)
{
  char buf[12];
  uint8_t n;
  int16_t t10;
  int16_t h10;
  uint8_t t_pct;
  uint8_t h_pct;

  (void)t;

  t10 = (int16_t)(temperature * 10.0f + 0.5f);
  h10 = (int16_t)(humidity * 10.0f + 0.5f);
  if (t10 < 0)
  {
    t10 = 0;
  }

  t_pct = (uint8_t)((t10 > 500) ? 100 : (t10 * 100) / 500);
  h_pct = (uint8_t)((h10 > 1000) ? 100 : (h10 / 10));

  UI_Title(u8g2, sensor_ok ? "AHT20" : "AHT20 SIM", 2U);

  u8g2_SetFont(u8g2, u8g2_font_wqy12_cn);
  u8g2_DrawUTF8(u8g2, 2, 30, UI_TXT_TEMP);
  u8g2_DrawUTF8(u8g2, 2, 54, UI_TXT_HUM);

  u8g2_SetFont(u8g2, u8g2_font_10x20_ascii);
  UI_Fmt1(buf, t10);
  n = (uint8_t)strlen(buf);
  buf[n] = ' ';
  buf[n + 1] = 'C';
  buf[n + 2] = '\0';
  u8g2_DrawStr(u8g2, 48, 32, buf);

  UI_Fmt1(buf, h10);
  n = (uint8_t)strlen(buf);
  buf[n] = ' ';
  buf[n + 1] = '%';
  buf[n + 2] = '\0';
  u8g2_DrawStr(u8g2, 48, 56, buf);

  UI_Bar(u8g2, 34, t_pct);
  UI_Bar(u8g2, 58, h_pct);
}

void UI_Marquee(u8g2_t *u8g2, uint16_t t)
{
  int16_t x0 = (int16_t)((int32_t)UI_W -
                         (int32_t)(((uint32_t)t * 60U / 1000U) %
                                   (uint32_t)(ui_marquee_width + UI_W)));

  UI_Title(u8g2, "HELLO", 3U);

  UI_MarqueeStrip(u8g2, x0);

  u8g2_SetFont(u8g2, u8g2_font_wqy12_cn);
  u8g2_DrawUTF8(u8g2, 2, 61, UI_TXT_ROOM);

  u8g2_SetFont(u8g2, u8g2_font_7x14B_ascii);
  u8g2_DrawStr(u8g2, 98, 61, "U8g2");
}

void UI_Poem(u8g2_t *u8g2, uint16_t t)
{
  int8_t  i;
  uint8_t off = (uint8_t)(((uint32_t)t * 20U / 1000U) % 72U);

  UI_Title(u8g2, "POEM", 4U);

  u8g2_SetFont(u8g2, u8g2_font_wqy12_cn);
  u8g2_SetClipWindow(u8g2, 0, 13, 127, 63);

  /* six slots: one line above the screen and one below, so the scroll wraps */
  for (i = -1; i <= 4; i++)
  {
    int16_t y = (int16_t)(27 + i * 18 - (int16_t)off);
    uint8_t idx = (uint8_t)(((i % 4) + 4) % 4);

    if ((y >= 27) && (y <= 70))
    {
      UI_CenterUtf8(u8g2, (uint8_t)y, kPoem[idx]);
    }
  }
  u8g2_SetMaxClipWindow(u8g2);
}

void UI_Avatar(u8g2_t *u8g2, uint16_t t)
{
  int16_t x = 0;

  if (t < 600U)
  {
    x = (int16_t)(128 - ((int32_t)t * 128 / 600));
  }

  u8g2_DrawXBMP(u8g2, (u8g2_uint_t)x, 0, 64, 64, ui_avatar_64x64);

  u8g2_DrawVLine(u8g2, 66, 4, 56);

  u8g2_SetFont(u8g2, u8g2_font_wqy12_cn);
  u8g2_DrawUTF8(u8g2, 70, 22, UI_TXT_NAME);

  u8g2_SetFont(u8g2, u8g2_font_7x14B_ascii);
  u8g2_DrawStr(u8g2, 70, 38, "632407");
  u8g2_DrawStr(u8g2, 70, 52, "030418");

  /* blink: close both "lenses" for 160 ms every 2.4 s */
  if ((x == 0) && ((t % 2400U) > 2200U) && ((t % 2400U) < 2360U))
  {
    u8g2_SetDrawColor(u8g2, 0);
    u8g2_DrawHLine(u8g2, 21, 35, 8);
    u8g2_DrawHLine(u8g2, 35, 35, 8);
    u8g2_SetDrawColor(u8g2, 1);
  }
}
