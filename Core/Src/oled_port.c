/**
  ******************************************************************************
  * @file    oled_port.c
  * @brief   U8g2 -> STM32 HAL port: byte transfer over hardware I2C1 (PB6/PB7)
  *
  *   U8g2 works bottom-up: it calls the "byte" callback to move raw bytes to the
  *   display and the "gpio & delay" callback for timing.  Here both callbacks are
  *   mapped onto the STM32 HAL, which is what "porting U8g2 to HAL" really means.
  ******************************************************************************
  */

#include "oled_port.h"
#include "main.h"

extern I2C_HandleTypeDef hi2c1;

u8g2_t u8g2;

/* ---------------------------------------------------------------- internal */

#define I2C_TX_MAX   64U

static uint8_t s_tx_buf[I2C_TX_MAX];
static uint8_t s_tx_len;

/**
  * @brief  Microsecond busy-wait, only used by the U8g2 reset/delay sequence.
  */
static void OLED_DelayUs(uint16_t us)
{
  uint32_t loops = (SystemCoreClock / 1000000U) * (uint32_t)us / 4U;
  while (loops-- > 0U)
  {
    __NOP();
  }
}

/**
  * @brief  U8g2 byte callback: START / SEND / END are collapsed into one HAL
  *         I2C master transfer, because SSD1306 expects [addr][ctrl][data...]
  *         inside a single I2C frame.
  */
static uint8_t OLED_ByteCb(u8x8_t *u8x8, uint8_t msg, uint8_t arg_int, void *arg_ptr)
{
  uint8_t *src = (uint8_t *)arg_ptr;

  switch (msg)
  {
    case U8X8_MSG_BYTE_INIT:
      /* I2C1 is already initialised by MX_I2C1_Init() */
      break;

    case U8X8_MSG_BYTE_START_TRANSFER:
      s_tx_len = 0U;
      /* u8x8 keeps the 8-bit form of the address (0x78 = 0x3C << 1),
         which is exactly what HAL_I2C_Master_Transmit() expects */
      s_tx_buf[s_tx_len++] = (uint8_t)u8x8_GetI2CAddress(u8x8);
      break;

    case U8X8_MSG_BYTE_SEND:
      while ((arg_int-- > 0U) && (s_tx_len < I2C_TX_MAX))
      {
        s_tx_buf[s_tx_len++] = *src++;
      }
      break;

    case U8X8_MSG_BYTE_END_TRANSFER:
      if (s_tx_len > 1U)
      {
        (void)HAL_I2C_Master_Transmit(&hi2c1, s_tx_buf[0],
                                      &s_tx_buf[1], (uint16_t)(s_tx_len - 1U), 100U);
      }
      s_tx_len = 0U;
      break;

    default:
      return 0U;
  }
  return 1U;
}

/**
  * @brief  U8g2 gpio/delay callback: only delays are needed for I2C (no RST pin).
  */
static uint8_t OLED_GpioDelayCb(u8x8_t *u8x8, uint8_t msg, uint8_t arg_int, void *arg_ptr)
{
  (void)u8x8;
  (void)arg_ptr;

  switch (msg)
  {
    case U8X8_MSG_DELAY_MILLI:
      HAL_Delay((uint32_t)arg_int);
      break;

    case U8X8_MSG_DELAY_10MICRO:
      OLED_DelayUs((uint16_t)(arg_int * 10U));
      break;

    case U8X8_MSG_DELAY_100NANO:
      OLED_DelayUs(1U);
      break;

    case U8X8_MSG_DELAY_I2C:
      /* only used by software I2C drivers, arg_int is in microseconds */
      OLED_DelayUs((uint16_t)arg_int);
      break;

    case U8X8_MSG_DELAY_NANO:
    case U8X8_MSG_GPIO_AND_DELAY_INIT:
      break;

    default:
      return 0U;
  }
  return 1U;
}

/* ------------------------------------------------------------------- API */

void OLED_Init(void)
{
  /* "_f" = full screen buffer (1 KiB).  Every frame is composed in RAM and then
     pushed to the panel with a single u8g2_SendBuffer(), i.e. hardware refresh. */
  u8g2_Setup_ssd1306_i2c_128x64_noname_f(&u8g2, U8G2_R0,
                                         OLED_ByteCb, OLED_GpioDelayCb);
  u8g2_InitDisplay(&u8g2);
  u8g2_SetPowerSave(&u8g2, 0);
  u8g2_ClearBuffer(&u8g2);
  u8g2_SendBuffer(&u8g2);
}

void OLED_Refresh(void)
{
  u8g2_SendBuffer(&u8g2);
}
