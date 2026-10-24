/**
  ******************************************************************************
  * @file    app.c
  * @brief   Demo state machine: cycles through the six OLED pages
  ******************************************************************************
  */

#include "app.h"
#include "main.h"
#include "oled_port.h"
#include "ui.h"
#include "aht20.h"

#define APP_FRAME_MS      40U    /* ~25 fps, one full 1 KiB I2C refresh per frame */
#define APP_AHT_PERIOD_MS 2000U  /* AHT20 measurement period */

/* page indices and their visible time */
enum
{
  SCR_BOOT = 0,
  SCR_ID,
  SCR_U8G2,
  SCR_AHT,
  SCR_MARQUEE,
  SCR_POEM,
  SCR_AVATAR,
  SCR_COUNT
};

static const uint16_t kDuration[SCR_COUNT] =
{
  1500U, 5000U, 5000U, 6000U, 9500U, 9000U, 6000U
};

static uint8_t  s_screen;
static uint32_t s_page_start;
static uint32_t s_last_frame;
static uint32_t s_last_led;
static uint32_t s_last_aht;
static uint8_t  s_aht_ok;
static float    s_temperature = 25.6f;
static float    s_humidity    = 52.4f;

/* 32 point sine, +-71: used to animate the AHT20 page when no sensor is attached */
static const int8_t kSine32[32] =
{
   0,  10,  20,  29,  38,  46,  54,  60,  65,  69,  71,  71,  71,  69,  65,  60,
  54,  46,  38,  29,  20,  10,   0, -10, -20, -29, -38, -46, -54, -60, -65, -71
};

/**
  * @brief  Fill s_temperature / s_humidity with a slow simulated curve.
  */
static void App_Simulate(uint32_t now)
{
  int8_t s = kSine32[(now / 80U) % 32U];

  s_temperature = 25.0f + (float)s / 10.0f;   /* 17.9 .. 32.1 C */
  s_humidity    = 55.0f + (float)s / 2.0f;    /* 19.5 .. 90.5 % */
}

/**
  * @brief  Try to refresh the AHT20 reading; fall back to the simulated curve.
  */
static void App_UpdateAht(uint32_t now)
{
  float t;
  float h;

  if (AHT20_Read(&t, &h) == 0U)
  {
    s_temperature = t;
    s_humidity = h;
    s_aht_ok = 1U;
  }
  else
  {
    s_aht_ok = 0U;
    App_Simulate(now);
  }
  s_last_aht = now;
}

void App_Init(void)
{
  uint32_t now;

  OLED_Init();
  u8g2_SetFontMode(&u8g2, 1);     /* transparent text background */
  u8g2_SetDrawColor(&u8g2, 1);

  now = HAL_GetTick();

  if (AHT20_Init() == 0U)
  {
    App_UpdateAht(now);
  }
  else
  {
    s_aht_ok = 0U;
    App_Simulate(now);
  }

  s_screen = SCR_BOOT;
  s_page_start = now;
  s_last_frame = now;
  s_last_led = now;
  s_last_aht = now;

  /* draw the first frame immediately so the panel lights up right after reset */
  u8g2_ClearBuffer(&u8g2);
  UI_Boot(&u8g2, 0U);
  OLED_Refresh();
}

void App_Task(void)
{
  uint32_t now = HAL_GetTick();
  uint16_t t;
  uint8_t  page;

  if ((uint32_t)(now - s_last_frame) < APP_FRAME_MS)
  {
    return;
  }
  s_last_frame = now;

  t = (uint16_t)(now - s_page_start);
  if (t >= kDuration[s_screen])
  {
    s_screen = (uint8_t)((s_screen + 1U) % SCR_COUNT);
    s_page_start = now;
    t = 0U;

    if (s_screen == SCR_AHT)
    {
      App_UpdateAht(now);
    }
  }

  page = s_screen;

  if ((page == SCR_AHT) && ((uint32_t)(now - s_last_aht) >= APP_AHT_PERIOD_MS))
  {
    App_UpdateAht(now);
  }

  u8g2_ClearBuffer(&u8g2);

  switch (page)
  {
    case SCR_BOOT:
      UI_Boot(&u8g2, t);
      break;

    case SCR_ID:
      UI_IdCard(&u8g2, t);
      break;

    case SCR_U8G2:
      UI_U8g2Demo(&u8g2, t);
      break;

    case SCR_AHT:
      UI_Aht20(&u8g2, s_temperature, s_humidity, s_aht_ok, t);
      break;

    case SCR_MARQUEE:
      UI_Marquee(&u8g2, t);
      break;

    case SCR_POEM:
      UI_Poem(&u8g2, t);
      break;

    case SCR_AVATAR:
    default:
      UI_Avatar(&u8g2, t);
      break;
  }

  OLED_Refresh();

  /* 1 Hz heartbeat on the on-board LED (PC13, active low) */
  if ((uint32_t)(now - s_last_led) >= 500U)
  {
    s_last_led = now;
    HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
  }
}
