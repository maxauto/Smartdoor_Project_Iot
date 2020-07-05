/*
 ***************************************************************
 * Smart Door project firmware
 ***************************************************************
 * Nares Chumaparat
 * 60070504008
 * Automation Engineering
 * Faculty of Engineering, KMUTT
 * 11 May, 2020
 ***************************************************************
*/

#include "os.h"
#include <stdlib.h>

void Worker3(void *param) {
    LED0_Off();  
}

void Worker2(void *param) {
    LED2_Off();  
}

void Worker1(void *param) {
    LED1_Off();  
}

void Ring(void *param) {
    LED1_On();
    Beep_PowerSet(0.2);
    Beep_FreqSet(2000);
    Beep(500);
    OS_TimerCreate(
            "Timer1",      
            2000,           
            TIMER_MODE_ONESHORT, 
            Worker1        
        );  
}

void gel_pump(void *param) {
    LED2_On();
    OS_TimerCreate(
            "Timer2",       
            2000,          
            TIMER_MODE_ONESHORT, 
            Worker2      
        );  
}

void unlock(void *param) {
    LED0_On();
       
          OS_TimerCreate(
            "Timer5",      
            3000,           
            TIMER_MODE_ONESHORT, 
            Worker3        
            );  
}




//!! UART1 Line Received Callback
void UartLineCallback(void *evt)
{
    //!! Pointer to void to pointer to uart_event_t
    uart_event_t *uart_event = (uart_event_t *)evt;

    //!! Data structure
    data_t uart_data = uart_event->data;

    //!! Line data
    const char *line_data = (const char *)uart_data.buffer;
    //!! Print received data
    char buff[32];
    char target[32];  
    strcpy(target,line_data);
    char * pch;
    char *buff1[10];
    int i = 0;
    pch = strtok(target,",");
    while (pch != NULL)
    {   
        buff1[i]=pch;
        pch = strtok (NULL, ",");
        i++;
    }
   



    

    if(!strcmp(line_data, "LED0_ON\r\n")) {
        LED0_On();
        sprintf(buff, "LED0,1\r\n");
        UART1_AsyncWriteString(buff);     // LED0 ON
    }
    else if(!strcmp(line_data, "LED0_OFF\r\n")) {
        LED0_Off();
        sprintf(buff, "LED0,0\r\n");
        UART1_AsyncWriteString(buff);    // LED0 OFF
    }
    else if(!strcmp(line_data, "LED1_ON\r\n")) {
        LED1_On();
        sprintf(buff, "LED1,1\r\n");
        UART1_AsyncWriteString(buff);     // LED1 ON
    }
    else if(!strcmp(line_data, "LED1_OFF\r\n")) {
        LED1_Off();
        sprintf(buff, "LED1,0\r\n");
        UART1_AsyncWriteString(buff);    // LED1 OFF
    }
    else if(!strcmp(line_data, "LED2_ON\r\n")) {
        LED2_On();
        sprintf(buff, "LED2,1\r\n");
        UART1_AsyncWriteString(buff);     // LED2 ON
    }
    else if(!strcmp(line_data, "LED2_OFF\r\n")) {
        LED2_Off();
        sprintf(buff, "LED2,0\r\n");
        UART1_AsyncWriteString(buff);    // LED2 OFF
    }
    else if(!strcmp(line_data, "LED3_ON\r\n")) {
        LED3_On();
        sprintf(buff, "LED3,1\r\n");
        UART1_AsyncWriteString(buff);     // LED3 ON
    }
    else if(!strcmp(line_data, "LED3_OFF\r\n")) {
        LED3_Off();
        sprintf(buff, "LED3,0\r\n");
        UART1_AsyncWriteString(buff);    // LED3 OFF
    }
    else if(!strcmp(line_data, "UNLOCK\r\n")) {
        sprintf(buff, "LED0,1\r\n");
        UART1_AsyncWriteString(buff);
        LED0_On();
       
          OS_TimerCreate(
            "Timer3",      
            3000,           
            TIMER_MODE_ONESHORT, 
            Worker3        
            );  
    }
    else if(!strcmp(line_data, "PUMP\r\n")) {
        sprintf(buff, "LED2,1\r\n");
        UART1_AsyncWriteString(buff);
        LED2_On();
       
          OS_TimerCreate(
            "Timer4",      
            2000,           
            TIMER_MODE_ONESHORT, 
            Worker2        
            );  
    }
    else if(!strcmp(line_data, "LED0_READ\r\n")) {
        int led0 = LED_Get(0); // READ LED0 
        sprintf(buff, "LED0,%d\r\n",led0);
        UART1_AsyncWriteString(buff);
    }
    else if(!strcmp(line_data, "LED1_READ\r\n")) {
        int led1 = LED_Get(1); // READ LED1
        sprintf(buff, "LED1,%d\r\n",led1);
        UART1_AsyncWriteString(buff);
    }
    else if(!strcmp(line_data, "LED2_READ\r\n")) {
        int led2 = LED_Get(2); // READ LED2
        sprintf(buff, "LED2,%d\r\n",led2);
        UART1_AsyncWriteString(buff);
    }
    else if(!strcmp(line_data, "LED3_READ\r\n")) {
        int led3 = LED_Get(3); // READ LED3
        sprintf(buff, "LED3,%d\r\n",led3);
        UART1_AsyncWriteString(buff);
    }
    else if(!strcmp(line_data, "PSW0_READ\r\n")) {
        int psw0 = PSW_Get(0); // READ PSW0
        sprintf(buff, "PSW0,%d\r\n",psw0);
        UART1_AsyncWriteString(buff);
    }
    else if(!strcmp(line_data, "PSW1_READ\r\n")) {
        int psw1 = PSW_Get(1); // READ PSW1
        sprintf(buff, "PSW1,%d\r\n",psw1);
        UART1_AsyncWriteString(buff);
    }
    else if(!strcmp(line_data, "PSW2_READ\r\n")) {
        int psw2 = PSW_Get(2); // READ PSW1
        sprintf(buff, "PSW2,%d\r\n",psw2);
        UART1_AsyncWriteString(buff);
    }
    else if(!strcmp(line_data, "PSW3_READ\r\n")) {
        int psw3 = PSW_Get(3); // READ PSW1
        sprintf(buff, "PSW3,%d\r\n",psw3);
        UART1_AsyncWriteString(buff);
    }
    else if(!strcmp(line_data, "ADC0_READ\r\n")) {
        int adc0 = ADC_Get(0); // READ ADC0  humidity 50-100% 0-1022
        float humidity = (100.0-50.0)*((float)adc0/1022.0)+50.0;
        sprintf(buff, "ADC0,%.1f\r\n",humidity);
        UART1_AsyncWriteString(buff);
    }
    else if(!strcmp(line_data, "ADC1_READ\r\n")) {
        int adc1 = ADC_Get(1); // READ ADC1  PM 2.5 0-500 μg/m3 0-1022
        float pm = (500.0)*((float)adc1/1022.0);
        sprintf(buff, "ADC1,%.1f\r\n",pm);
        UART1_AsyncWriteString(buff);
    }
    else if(!strcmp(line_data, "ADC2_READ\r\n")) {
        int adc2 = ADC_Get(2); // READ ADC2 air temperature 20-41 celsius 0-1022
        float airtemp = (41.0-20.0)*((float)adc2/1022.0)+20.0;
        sprintf(buff, "ADC2,%.1f\r\n",airtemp);
        UART1_AsyncWriteString(buff);
    }
    else if(!strcmp(line_data, "ADC3_READ\r\n")) {
        int adc3 = ADC_Get(3); // READ ADC3 human body temperature 20-50 celsius 0-1022
        float bodytemp = (50.0-20.0)*((float)adc3/1022.0)+20.0;
        sprintf(buff, "ADC3,%.1f\r\n",bodytemp);
        UART1_AsyncWriteString(buff);
    }
    else if(!strcmp(line_data, "TURN_ON\r\n")){
        LED_PwmSet(LED_ID_3, 1000, 0, 500);
    }
    else if(!strcmp(buff1[0], "PWM0")){
        float period = atoi(buff1[1]);
        float duty = atoi(buff1[2]);
        LED_PwmSet(LED_ID_3,period,0,duty);
    }

}


int main(void) {
    OS_Init();
    //Register UART1 Line Received Callback
    OS_Uart1SetLineReceivedCallback(UartLineCallback);

    OS_SwitchSetCallback(PSW_ID_0, Ring);
    OS_SwitchSetCallback(PSW_ID_3, gel_pump);
    OS_SwitchSetCallback(PSW_ID_2, unlock);


    OS_Start();
}
