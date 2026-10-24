/**
  ******************************************************************************
  * @file    oled_port.h
  * @brief   U8g2 -> STM32 HAL (hardware I2C1) port layer
  ******************************************************************************
  */

#ifndef __OLED_PORT_H
#define __OLED_PORT_H

#ifdef __cplusplus
extern "C" {
#endif

#include "u8g2.h"

/* OLED SSD1306 128x64, 4-wire I2C, default slave address 0x3C */
extern u8g2_t u8g2;

void OLED_Init(void);
void OLED_Refresh(void);

#ifdef __cplusplus
}
#endif

#endif /* __OLED_PORT_H */
