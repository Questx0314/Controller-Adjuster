/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2024 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "usb_device.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "usbd_cdc_if.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */
#define FLASH_ADDR 0x080E0000  // Flash 存储的起始地址
#define MAX_TX_LEN 200
#define NUM_POINTS 10  // 5 个点的 X 和 Y 坐标，共 10 个数据
/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
typedef struct
{
    float points[NUM_POINTS];  // 5个点的x,y坐标
} PointsData;

PointsData pointsData;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

void SendResponse(char* response)
{
    uint8_t buffer[MAX_TX_LEN];
    uint16_t len = snprintf((char*)buffer, sizeof(buffer), "%s\r\n", response);
    
    CDC_Transmit_FS(buffer, len);  // 通过 USB 发送消息
}

void SendPoints()
{
    char buffer[MAX_TX_LEN];
    sprintf(buffer, "Controller send points:");
    
    // 读取存储�? pointsData 中的点数据并发�??
    for (int i = 0; i < 5; i++)
    {
        sprintf(buffer + strlen(buffer), "%f,%f", pointsData.points[i * 2], pointsData.points[i * 2 + 1]);
        if (i < 4)
            strcat(buffer, ",");  // 添加逗号分隔�?
    }
    strcat(buffer, "\r\n");

    CDC_Transmit_FS((uint8_t*)buffer, strlen(buffer));  // 发�?�点数据
}

void WritePointsToFlash(PointsData* pointsData)
{
    HAL_FLASH_Unlock();  // 解锁 Flash 写入

    // 将每个坐标点�? x �? y 写入 Flash
    for (int i = 0; i < 5; i++)
    {
        // 写入点的 x 坐标
        HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD, FLASH_ADDR + i * 2 * sizeof(float), pointsData->points[i * 2]);
        // 写入点的 y 坐标
        HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD, FLASH_ADDR + (i * 2 + 1) * sizeof(float), pointsData->points[i * 2 + 1]);
    }

    HAL_FLASH_Lock();  // 锁定 Flash
}

void ReadPointsFromFlash(PointsData* pointsData)
{
    for (int i = 0; i < 5; i++)
    {
        // 读取点的 x 坐标
        pointsData->points[i * 2] = *(float*)(FLASH_ADDR + i * 2 * sizeof(float));
        // 读取点的 y 坐标
        pointsData->points[i * 2 + 1] = *(float*)(FLASH_ADDR + (i * 2 + 1) * sizeof(float));
    }
}

// 解析接收到的点数据并更新
void UpdatePoints(uint8_t* data)
{
  char* token = strtok((char*)data, ",");
  int index = 1;

  // 遍历并解析点数据
  while (token != NULL && index < 10)  // 最多解析 10 个数据
  {
      // 转换为浮动点数
      float value = atof(token);

      // 验证每个坐标值是否在合理范围内 (0-100)
      if (value < 0.0f || value > 100.0f) 
      {
          SendResponse("Invalid data");  // 如果有无效的点，返回错误消息
          return;
      }

      pointsData.points[index] = value;  // 存储有效的坐标
      token = strtok(NULL, ",");
      index++;
  }

  // 确保数据完整：检查是否恰好有 10 个坐标数据
  if (index != 10)
  {
      SendResponse("Invalid number of points");  // 如果点数不等于 10，返回错误消息
      return;
  }

  // 将更新后的点数据保存到 Flash
  WritePointsToFlash(&pointsData);

  // 回复数据接收成功
  SendResponse("data send success");
}

// 处理接收到的数据
void ProcessReceivedData(uint8_t* data, uint32_t len)
{
    if (strstr((char*)data, "FS connect") == (char*)data)
    {
        SendResponse("connect success");
    }
    else if (strstr((char*)data, "FS request points") == (char*)data)
    {
        SendPoints();  // 回复当前点数据
    }
    else if (strstr((char*)data, "FS send points:") == (char*)data)
    {
        // 提取数字部分并更新点数据
        UpdatePoints(data + 16);  // 跳过 "FS send points:" 部分
    }
    else
    {
        SendResponse("Unknown command");  // 回传未识别的命令
    }
}


// 在重启单片机之后不需要插拔usb也能正确识别
void USB_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOA_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_11|GPIO_PIN_12, GPIO_PIN_RESET);

  /*Configure GPIO pin : PA8 */
  GPIO_InitStruct.Pin = GPIO_PIN_11|GPIO_PIN_12;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_PULLDOWN;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  HAL_Delay(10);
}
/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */
  USB_Init();
  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USB_DEVICE_Init();
  /* USER CODE BEGIN 2 */
  char msg[] = "Hello World!111";
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
		// SendResponse(msg);
    // CDC_Transmit_FS(msg,sizeof(msg));
    // HAL_Delay(1000);
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = 4;
  RCC_OscInitStruct.PLL.PLLN = 72;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = 3;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
