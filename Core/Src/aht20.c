/**
  ******************************************************************************
  * @file    aht20.c
  * @brief   AHT20 temperature / humidity sensor driver
  *
  *   Measurement sequence (datasheet 6.1):
  *     1. power on wait >= 40 ms
  *     2. read status; if the calibration bit (0x08) is clear, send 0xBE 0x08 0x00
  *     3. send 0xAC 0x33 0x00 to trigger a conversion, wait >= 80 ms
  *     4. read 7 bytes: status, 20-bit humidity, 20-bit temperature
  ******************************************************************************
  */

#include "aht20.h"

extern I2C_HandleTypeDef hi2c1;

#define AHT20_CMD_CALIBRATE   0xBEU
#define AHT20_CMD_TRIGGER     0xACU
#define AHT20_CMD_SOFT_RESET  0xBAU

#define AHT20_STATUS_BUSY     0x80U
#define AHT20_STATUS_CAL      0x08U

static uint8_t AHT20_WriteCmd(const uint8_t *cmd, uint16_t len)
{
  return (HAL_I2C_Master_Transmit(&hi2c1, AHT20_ADDR_WRITE,
                                  (uint8_t *)cmd, len, 100U) == HAL_OK) ? 0U : 1U;
}

static uint8_t AHT20_ReadBytes(uint8_t *buf, uint16_t len)
{
  return (HAL_I2C_Master_Receive(&hi2c1, AHT20_ADDR_READ,
                                 buf, len, 100U) == HAL_OK) ? 0U : 1U;
}

uint8_t AHT20_Init(void)
{
  uint8_t cmd[3];
  uint8_t status = 0U;

  HAL_Delay(40U);

  if (AHT20_ReadBytes(&status, 1U) != 0U)
  {
    return 1U;
  }

  if ((status & AHT20_STATUS_CAL) == 0U)
  {
    cmd[0] = AHT20_CMD_CALIBRATE;
    cmd[1] = 0x08U;
    cmd[2] = 0x00U;
    if (AHT20_WriteCmd(cmd, 3U) != 0U)
    {
      return 1U;
    }
    HAL_Delay(10U);
  }

  return 0U;
}

uint8_t AHT20_SoftReset(void)
{
  uint8_t cmd = AHT20_CMD_SOFT_RESET;

  if (AHT20_WriteCmd(&cmd, 1U) != 0U)
  {
    return 1U;
  }
  HAL_Delay(20U);
  return 0U;
}

uint8_t AHT20_Read(float *temperature, float *humidity)
{
  uint8_t cmd[3] = {AHT20_CMD_TRIGGER, 0x33U, 0x00U};
  uint8_t buf[7];
  uint32_t raw_hum;
  uint32_t raw_temp;
  uint8_t retry;

  if ((temperature == NULL) || (humidity == NULL))
  {
    return 1U;
  }

  if (AHT20_WriteCmd(cmd, 3U) != 0U)
  {
    return 1U;
  }

  /* conversion takes about 75 ms, poll the busy flag instead of a blind delay */
  for (retry = 0U; retry < 10U; retry++)
  {
    HAL_Delay(10U);
    if ((AHT20_ReadBytes(buf, 1U) == 0U) && ((buf[0] & AHT20_STATUS_BUSY) == 0U))
    {
      break;
    }
  }
  if (retry >= 10U)
  {
    return 1U;
  }

  if (AHT20_ReadBytes(buf, 7U) != 0U)
  {
    return 1U;
  }
  if ((buf[0] & AHT20_STATUS_BUSY) != 0U)
  {
    return 1U;
  }

  raw_hum  = ((uint32_t)buf[1] << 12) | ((uint32_t)buf[2] << 4) | ((uint32_t)buf[3] >> 4);
  raw_temp = (((uint32_t)buf[3] & 0x0FU) << 16) | ((uint32_t)buf[4] << 8) | (uint32_t)buf[5];

  *humidity    = (float)raw_hum  * 100.0f / 1048576.0f;
  *temperature = (float)raw_temp * 200.0f / 1048576.0f - 50.0f;

  return 0U;
}
