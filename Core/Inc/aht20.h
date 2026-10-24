/**
  ******************************************************************************
  * @file    aht20.h
  * @brief   AHT20 temperature / humidity sensor driver (I2C, address 0x38)
  ******************************************************************************
  */

#ifndef __AHT20_H
#define __AHT20_H

#ifdef __cplusplus
extern "C" {
#endif

#include "main.h"

/* AHT20 7-bit address is 0x38, HAL wants it already shifted left */
#define AHT20_ADDR_WRITE   (0x38 << 1)
#define AHT20_ADDR_READ    ((0x38 << 1) | 1)

uint8_t AHT20_Init(void);
uint8_t AHT20_Read(float *temperature, float *humidity);

#ifdef __cplusplus
}
#endif

#endif /* __AHT20_H */
