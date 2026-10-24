/**
  ******************************************************************************
  * @file    u8g2_kerning.c
  * @brief   Kerning stubs for the trimmed u8g2 tree
  *
  *   u8g2_DrawExtendedUTF8() / u8g2_DrawExtUTF8() in u8g2_font.c reference the
  *   two kerning helpers, but the trimmed copy of u8g2_font.c shipped with this
  *   project does not contain them (and no font here has a kerning table).
  *   Providing "no kerning" stubs keeps the linker happy without pulling the
  *   whole kerning feature into the image.
  ******************************************************************************
  */

#include "u8g2.h"

uint8_t u8g2_GetKerning(u8g2_t *u8g2, u8g2_kerning_t *kerning,
                        uint16_t e1, uint16_t e2)
{
  (void)u8g2;
  (void)kerning;
  (void)e1;
  (void)e2;
  return 0U;
}

uint8_t u8g2_GetKerningByTable(u8g2_t *u8g2, const uint16_t *kt,
                               uint16_t e1, uint16_t e2)
{
  (void)u8g2;
  (void)kt;
  (void)e1;
  (void)e2;
  return 0U;
}
