/**
  ******************************************************************************
  * @file    ui.h
  * @brief   Drawing routines for the six OLED demo pages (pure u8g2, no HAL)
  ******************************************************************************
  */

#ifndef __UI_H
#define __UI_H

#ifdef __cplusplus
extern "C" {
#endif

#include "u8g2.h"

/* Each function draws one full 128x64 frame into the u8g2 buffer.
   t = milliseconds since this page became visible (used for the animations). */

void UI_Boot(u8g2_t *u8g2, uint16_t t);
void UI_IdCard(u8g2_t *u8g2, uint16_t t);
void UI_U8g2Demo(u8g2_t *u8g2, uint16_t t);
void UI_Aht20(u8g2_t *u8g2, float temperature, float humidity,
              uint8_t sensor_ok, uint16_t t);
void UI_Marquee(u8g2_t *u8g2, uint16_t t);
void UI_Poem(u8g2_t *u8g2, uint16_t t);
void UI_Avatar(u8g2_t *u8g2, uint16_t t);

#ifdef __cplusplus
}
#endif

#endif /* __UI_H */
