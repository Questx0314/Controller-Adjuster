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
#define FLASH_ADDR ((uint32_t)0x080E0000)  // Flash 存储的起始地址?
#define MAX_TX_LEN 256
#define NUM_POINTS 10
#define FLASH_SECTOR_SIZE ((uint32_t)0x4000)  // 16 KB
/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
typedef struct
{
    float points[NUM_POINTS];  // 5个点的x,y坐标
} PointsData;
PointsData pointsData;

typedef struct 
{
  HAL_StatusTypeDef hal_status;
  char process[32];
  char detail[64];
}ErrorRecord;

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
// 获取 Flash 扇区编号
uint32_t GetSector(uint32_t address)
{
    if (address < 0x08004000) return FLASH_SECTOR_0;
    if (address < 0x08008000) return FLASH_SECTOR_1;
    if (address < 0x0800C000) return FLASH_SECTOR_2;
    if (address < 0x08010000) return FLASH_SECTOR_3;
    if (address < 0x08020000) return FLASH_SECTOR_4;
    if (address < 0x08040000) return FLASH_SECTOR_5;
    if (address < 0x08060000) return FLASH_SECTOR_6;
    if (address < 0x08080000) return FLASH_SECTOR_7;
    if (address < 0x080A0000) return FLASH_SECTOR_8;
    if (address < 0x080C0000) return FLASH_SECTOR_9;
    if (address < 0x080E0000) return FLASH_SECTOR_10;
    if (address < 0x08100000) return FLASH_SECTOR_11;
    return FLASH_SECTOR_11;  // 默认返回最后一个扇区
}

void SendError(ErrorRecord* errorRecord)
{
    uint8_t buffer[MAX_TX_LEN];

    // 格式化错误信息，包括出错过程、HAL 状态和详细描述
    uint16_t len = snprintf((char*)buffer, sizeof(buffer), 
                            "Error in process: %s\r\nHAL_Status: %d\r\nDetail: %s\r\n", 
                            errorRecord->process, 
                            errorRecord->hal_status, 
                            errorRecord->detail);

    // 通过 USB 发送错误信息
    CDC_Transmit_HS(buffer, len);
}

void ReportError(HAL_StatusTypeDef hal_status, const char* process, char* detail)
{
    ErrorRecord errorRecord;
    errorRecord.hal_status = hal_status;

    // 拷贝 process
    strncpy(errorRecord.process, process, sizeof(errorRecord.process));
    errorRecord.process[sizeof(errorRecord.process) - 1] = '\0';  // 确保字符串以 '\0' 结束

    // 拷贝 detail
    strncpy(errorRecord.detail, detail, sizeof(errorRecord.detail));
    errorRecord.detail[sizeof(errorRecord.detail) - 1] = '\0';  // 确保字符串以 '\0' 结束

    // 调用 SendError
    SendError(&errorRecord);
}

void SendResponse(char* response)
{
  uint8_t buffer[MAX_TX_LEN];
  uint16_t len = snprintf((char*)buffer, sizeof(buffer), "%s\r\n", response);
  
  CDC_Transmit_HS(buffer, len);  // 通过 USB 发送消息
}

void ReadPointsFromFlash(PointsData* pointsData)
{
  for (int i = 0; i < NUM_POINTS; i++)
  {
    float value = *(float*)(FLASH_ADDR + i * sizeof(float));
    pointsData->points[i] = value;
  }
}

HAL_StatusTypeDef EraseFlash(uint32_t startAddress, uint32_t endAddress)
{
    HAL_FLASH_Unlock();

    uint32_t sectorStart = GetSector(startAddress);
    uint32_t sectorEnd = GetSector(endAddress);

    FLASH_EraseInitTypeDef eraseInitStruct;
    uint32_t sectorError;

    eraseInitStruct.TypeErase = FLASH_TYPEERASE_SECTORS;
    eraseInitStruct.VoltageRange = FLASH_VOLTAGE_RANGE_3;

    for (uint32_t sector = sectorStart; sector <= sectorEnd; sector++) {
        eraseInitStruct.Sector = sector;
        eraseInitStruct.NbSectors = 1;

        if (HAL_FLASHEx_Erase(&eraseInitStruct, &sectorError) != HAL_OK) {
            char detail[64];
            snprintf(detail, sizeof(detail), "Sector: %lu", sector);
            ReportError(HAL_FLASH_GetError(), "EraseFlash", detail);
            HAL_FLASH_Lock();
            return HAL_ERROR;
        }
    }
    HAL_FLASH_Lock();
    return HAL_OK;
}

void WritePointsToFlash(PointsData* pointsData)
{
    if (EraseFlash(FLASH_ADDR, FLASH_ADDR + NUM_POINTS * sizeof(float) - 1) != HAL_OK)
    {
      return;
    }
    HAL_FLASH_Unlock();
    for (int i = 0; i < NUM_POINTS; i++) {
        float value = pointsData->points[i];
        uint32_t dataToWrite;
        memcpy(&dataToWrite, &value, sizeof(float));

        if (HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD, FLASH_ADDR + i * sizeof(float), dataToWrite) != HAL_OK) {
          char detail[64];
          snprintf(detail, sizeof(detail), "Index: %d, Value: %f", i, value);
          ReportError(HAL_FLASH_GetError(), "WritePointsToFlash", detail);
          HAL_FLASH_Lock();
          return;
        }
    }
    HAL_FLASH_Lock();
    SendResponse("data send success");
    return;
}

void SendPoints()
{
  ReadPointsFromFlash(&pointsData);
  char buffer[MAX_TX_LEN];
  int len = snprintf(buffer, sizeof(buffer), "Controller send points:");

    // 读取存储在 pointsData 中的点数据并发送
    for (int i = 0; i < NUM_POINTS; i++)
    {
        len += snprintf(buffer + len, sizeof(buffer) - len, "%f", pointsData.points[i]);
        if (i < NUM_POINTS - 1) {
            len += snprintf(buffer + len, sizeof(buffer) - len, ",");  // 添加逗号分隔符
        }
    }
    SendResponse(buffer);
}

// 解析接收到的点数据并更新
void UpdatePoints(uint8_t* data)
{
    char* token = strtok((char*)data, ",");
    int index = 0;

    // 遍历解析点数据
    while (token != NULL && index < NUM_POINTS)
    {
        float value = atof(token);
        // 验证数据范围
        if (value < 0.0f || value > 100.0f) 
        {
            char detail[64];
            snprintf(detail, sizeof(detail), "Invalid value: %f at index: %d", value, index);
            ReportError(HAL_ERROR, "UpdatePoints", detail);
            return;
        }
        // 存储有效的值到 pointsData
        pointsData.points[index] = value;  // 将解析的值存储到 pointsData 中
        token = strtok(NULL, ",");
        index++;
    }

    // 确保数据完整
    if (index != NUM_POINTS)
    {
        char detail[64];
        snprintf(detail, sizeof(detail), "Expected %d points, got %d", NUM_POINTS, index);
        ReportError(HAL_ERROR, "UpdatePoints", detail);
        return;
    }

    // 写入到 Flash
    WritePointsToFlash(&pointsData);
}


// 处理接收的数据
void ProcessReceivedData(uint8_t* data, uint32_t len)
{
    if (strstr((char*)data, "FS connect") == (char*)data)
    {
        SendResponse("connect success");
    }
    else if (strstr((char*)data, "FS request points") == (char*)data)
    {
        SendPoints();  // 回复当前点数量
    }
    else if (strstr((char*)data, "FS send points:") == (char*)data)
    {
        // 提取数字部分并更新点数据
        UpdatePoints(data + strlen("FS send points:"));  // 只传输FS send points：之后的部分
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
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOB, GPIO_PIN_14|GPIO_PIN_15, GPIO_PIN_RESET);

  /*Configure GPIO pin : PA8 */
  GPIO_InitStruct.Pin = GPIO_PIN_14|GPIO_PIN_15;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_PULLDOWN;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

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
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */

    // TestFlashReadWrite();  // 调用测试函数
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
