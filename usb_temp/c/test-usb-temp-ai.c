
/*
 *
 *  Copyright (c) 2007  Warren Jasper <wjasper@tx.ncsu.edu>
 *                           Measurement Computing
 *                          
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 */

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <ctype.h>
#include <sys/types.h>
#include <asm/types.h>

#include "pmd.h"
#include "usb-tc-ai.h"

float volts_FS(const int gain, const signed short num);


/* Test Program */
float celsius2fahr( float celsius)
{
  return (celsius*9.0/5.0 + 32.);
}

float fahr2celsius( float fahr)
{
  return (fahr - 32.)*5.0/9.0;
}

int toContinue()
{
  int answer;
  answer = 0; //answer = getchar();
  printf("Continue [yY]? ");
  while((answer = getchar()) == '\0' ||
    answer == '\n');
  return ( answer == 'y' || answer == 'Y');
}

int main (int argc, char **argv) {

  int fd[1];
  int ch;
  int numInterfaces = 0;
  __u8 bIReg, bOReg;
  float temperature;
  float volts;
  float temperature_array[8];
  float value_1, value_2;
  float value;
  int nchan;
  __u8 in_options, out_options;
  int flag;
  char type[10];
  int i;
  char serial[9];
  float R0, A, B, C;      // RTD: Callendar-Van Dusen coefficients
  float A0, A1, A2;       // Thermistor: Steinhart-Hart coefficients
  float Offset, Scale;    // Semiconductor

  numInterfaces = PMD_Find(MCC_VID, USBTEMP_AI_PID, fd);

  if ( numInterfaces <= 0 ) {
    fprintf(stderr, "USB TC-AI not found.\n");
    exit(1);
  } else
    printf("USB TC-AI Device is found! Number of interfaces = %d\n",
	   numInterfaces);

  /* config mask 0x01 means all inputs */
  usbDConfigPort_USBTC_AI(fd[0], DIO_DIR_OUT);
  usbDOut_USBTC_AI(fd[0], 0);

  while(1) {
    printf("\nUSB TEMP-AI Testing\n");
    printf("----------------\n");
    printf("Hit 'a' to get alarm status\n");
    printf("Hit 'b' to blink\n");
    printf("Hit 'c' to calibrate\n");
    printf("Hit 'd' to test DIO\n");
    printf("Hit 'e' to exit\n");
    printf("Hit 'f' for burnout status\n");
    printf("Hit 'g' to get serial number\n");
    printf("Hit 'h' to run the counter\n");
    printf("Hit 'R' to reset\n");
    printf("Hit 'r' to measure RTD\n");
    printf("Hit 'p' read the CJC\n");
    printf("Hit 's' to get status\n");
    printf("Hit 'S' to measure temperature (Semiconductor)\n");
    printf("Hit 't' to measure temperature (channels 0-3).\n");
    printf("Hit 'T' to measure temperature (Thermistor)\n");    
    printf("Hit 'x' to measure temperature (Thermocouple) multiple channels\n");
    printf("Hit 'v' to measure voltage (channels 4-7)\n");

    while((ch = getchar()) == '\0' ||
      ch == '\n');

    switch(ch) {
      case 'a':
        for ( i = 0; i < 8; i++ ) {
	  value_1 = 1.0 + i;
	  value_2 = 0.0;
	  in_options = 0x40 | i;
	  out_options = 0x0;  // disable alarm
          usbConfigAlarm_USBTC_AI(fd[0], i, in_options, out_options, value_1, value_2);
          usleep(10000);
	}
	for ( i = 0; i < 8; i++ ) {
          usleep(100000);
	  usbGetAlarmConfig_USBTC_AI(fd[0], i, &in_options, &out_options, &value_1, &value_2);
	  printf("Alarm %d: input options = %#x  output options = %#x  value_1 = %f  value_2 = %f\n",
		 i, in_options, out_options, value_1, value_2);
	}
        printf("\n");
	break;
      case 'b': /* test to see if led blinks */
        usbBlink_USBTC_AI(fd[0]);
        break;
      case 'c': /* calibration */
        usbCalibrate_USBTC_AI(fd[0], 0);
        usbCalibrate_USBTC_AI(fd[0], 1);
        break;
      case 'f':  /* Get status of thermocouple burnout detection */
	 printf("Burnout status = %#x\n", usbGetBurnoutStatus_USBTC_AI(fd[0], 0xf));
	 break;
      case 'g':
        strncpy(serial, PMD_GetSerialNumber(fd[0]), 9);
        printf("Serial Number = %s\n", serial);
	break;
      case 'p':  /* read the CJC */
        usbAin_USBTC_AI(fd[0], CJC0, 0, &temperature);
	printf("CJC 0 = %.2f degress Celsius or %.2f degrees Fahrenheit.\n", temperature,
	        celsius2fahr(temperature));
        break;
      case 'd': /* test to see if led blinks */
        printf("conect DIO0 - DIO4\n");
	printf("conect DIO1 - DIO5\n");
	printf("conect DIO2 - DIO6\n");
	printf("conect DIO3 - DIO7\n");
	usbDConfigBit_USBTC_AI(fd[0], 0,  DIO_DIR_OUT);
	usbDConfigBit_USBTC_AI(fd[0], 1,  DIO_DIR_OUT);
	usbDConfigBit_USBTC_AI(fd[0], 2,  DIO_DIR_OUT);
	usbDConfigBit_USBTC_AI(fd[0], 3,  DIO_DIR_OUT);
	usbDConfigBit_USBTC_AI(fd[0], 4,  DIO_DIR_IN);
	usbDConfigBit_USBTC_AI(fd[0], 5,  DIO_DIR_IN);
	usbDConfigBit_USBTC_AI(fd[0], 6,  DIO_DIR_IN);
	usbDConfigBit_USBTC_AI(fd[0], 7,  DIO_DIR_IN);
	do {
  	  printf("Enter value [0-f]: ");
	  scanf("%hhx", &bIReg);
	  bIReg &= 0xf;
  	  usbDOut_USBTC_AI(fd[0], bIReg);
	  usbDIn_USBTC_AI(fd[0], &bOReg);
	  printf("value = %#x\n", bOReg);
	} while (toContinue());
	break;
      case 'h':
	printf("connect CTR to DIO0.\n");
	usbDConfigBit_USBTC_AI(fd[0], 0,  DIO_DIR_OUT);
	usbInitCounter_USBTC_AI(fd[0]);
        sleep(1);
        flag = fcntl(fileno(stdin), F_GETFL);
        fcntl(0, F_SETFL, flag | O_NONBLOCK);
        do {
          usbDOutBit_USBTC_AI(fd[0], 0, 1);
	  usleep(200000);
          usbDOutBit_USBTC_AI(fd[0], 0, 0);
	  printf("Counter = %d\n",usbReadCounter_USBTC_AI(fd[0]));
        } while (!isalpha(getchar()));
        fcntl(fileno(stdin), F_SETFL, flag);
	break;
      case 's':
        printf("Status = %#x\n", usbGetStatus_USBTC_AI(fd[0]));
	break;
      case 'S':
        printf("Sampling Semiconductor TMP36\n");
	printf("Enter channel number [0-7]: ");
	scanf("%d", &ch);
        usbSetItem_USBTEMP_AI(fd[0], ch/2, SENSOR_TYPE, SEMICONDUCTOR);
	printf("        1.  Single ended.\n");
	printf("        2.  Differential.\n");
	printf("Enter connector type [1-4]: \n");
	scanf("%d", &i);
	switch (i) {
	  case 1: usbSetItem_USBTEMP_AI(fd[0], ch/2, CONNECTION_TYPE, SINGLE_ENDED);break;
	  case 2: usbSetItem_USBTEMP_AI(fd[0], ch/2, CONNECTION_TYPE, DIFFERENTIAL); break;
	  default: printf("Unknown type\n"); break;
	}
	printf("Enter Offset: ");
	scanf("%f", &Offset);
	printf("Enter Scale: ");
	scanf("%f", &Scale);
	usbSetItem_USBTEMP_AI(fd[0], ch/2, EXCITATION, EXCITATION_OFF);
	usbSetItem_USBTEMP_AI(fd[0], ch/2, CH_0_GAIN + ch%2, 0x1);       // Set for Semiconductor
	usbSetItem_USBTEMP_AI(fd[0], ch/2, CH_0_COEF_0 + ch%2, Offset);  // Offset
	usbGetItem_USBTC_AI(fd[0], ch/2, CH_0_COEF_0 + ch%2, &value);
	printf("Offset = %f     ", value);
	usbSetItem_USBTEMP_AI(fd[0], ch/2, CH_0_COEF_1 + ch%2, Scale);   // Scale
	usbGetItem_USBTC_AI(fd[0], ch/2, CH_0_COEF_1 + ch%2, &value);
	printf("Scale = %f     ", value);
        flag = fcntl(fileno(stdin), F_GETFL);
        fcntl(fileno(stdin), F_SETFL, flag | O_NONBLOCK);
	do {
          usbAin_USBTC_AI(fd[0], ch, 0, &temperature);
  	  printf("Channel: %d  %.2f degress Celsius or %.2f degrees Fahrenheit.\n",
		 ch, temperature, celsius2fahr(temperature));
  	  sleep(1);
	} while (!isalpha(getchar()));
	fcntl(fileno(stdin), F_SETFL, flag);
	break;
      case 'r':
	printf("Sampling RTD\n");
	printf("Enter channel number [0-7]: ");
	scanf("%d", &ch);
        usbSetItem_USBTEMP_AI(fd[0], ch/2, SENSOR_TYPE, RTD);
	printf("        1.  2-wire with 1 sensor.\n");
	printf("        2.  2-wire with 2 sensors.\n");
	printf("        3.  3-wire. \n");
	printf("        4.  4-wire.\n");
	printf("Enter connector type [1-4]: \n");
	scanf("%d", &i);
	switch (i) {
	  case 1: usbSetItem_USBTEMP_AI(fd[0], ch/2, CONNECTION_TYPE, TWO_WIRE_ONE_SENSOR);break;
	  case 2: usbSetItem_USBTEMP_AI(fd[0], ch/2, CONNECTION_TYPE, TWO_WIRE_TWO_SENSOR); break;
	  case 3: usbSetItem_USBTEMP_AI(fd[0], ch/2, CONNECTION_TYPE, THREE_WIRE);
	    printf("Connection-type = 3 wire.\n");
	    break;
	  case 4: usbSetItem_USBTEMP_AI(fd[0], ch/2, CONNECTION_TYPE, FOUR_WIRE);
	    printf("Connection-type = 4 wire.\n");
	    break;
	}
	R0 = 100.;
	A = .003908;
	B = -5.8019E-7;
	C = -4.2735E-12;
	usbSetItem_USBTEMP_AI(fd[0], ch/2, EXCITATION, MU_A_210);
	usbSetItem_USBTEMP_AI(fd[0], ch/2, CH_0_GAIN + ch%2, 0x2);     // Set 0 - 0.5V for RTD
	usbSetItem_USBTEMP_AI(fd[0], ch/2, CH_0_COEF_0 + ch%2, R0);    // R0 value
	usbGetItem_USBTC_AI(fd[0], ch/2, CH_0_COEF_0 + ch%2, &value);
	printf("R0 = %f     ", value);
	usbSetItem_USBTEMP_AI(fd[0], ch/2, CH_0_COEF_1 + ch%2, A);     // Callendar-Van Dusen Coefficient A
	usbGetItem_USBTC_AI(fd[0], ch/2, CH_0_COEF_1 + ch%2, &value);
	printf("A = %e     ", value);
	usbSetItem_USBTEMP_AI(fd[0], ch/2, CH_0_COEF_2 + ch%2, B);     // Callendar-Van Dusen Coefficient B
	usbGetItem_USBTC_AI(fd[0], ch/2, CH_0_COEF_2 + ch%2, &value);
	printf("B = %e     ", value);
	usbSetItem_USBTEMP_AI(fd[0], ch/2, CH_0_COEF_3 + ch%2, C);     // Callendar-Van Dusen Coefficient C
	usbGetItem_USBTC_AI(fd[0], ch/2, CH_0_COEF_3 + ch%2, &value);
	printf("C = %e\n", value);
        flag = fcntl(fileno(stdin), F_GETFL);
        fcntl(fileno(stdin), F_SETFL, flag | O_NONBLOCK);
	do {
          usbAin_USBTC_AI(fd[0], ch, 0, &temperature);
  	  printf("Channel: %d  %.2f degress Celsius or %.2f degrees Fahrenheit.\n",
		 ch, temperature, celsius2fahr(temperature));
  	  sleep(1);
	} while (!isalpha(getchar()));
       	fcntl(fileno(stdin), F_SETFL, flag);
	break;
      case 'R':
        usbReset_USBTC_AI(fd[0]);
        return 0;
	break;
      case 'e':
        close(fd[0]);
        return 0;
	break;
      case 't':
        ch = 0;
	printf("Select Channel [0-3]: ");
        scanf("%d", &ch);
	while (ch > 3) {
          printf("Channel must be between 0-3.\n");
	  printf("Select Channel [0-3]: ");
	  scanf("%d", &ch);
	}
        printf("Connect thermocouple to channel %d.\n", ch);
        usbSetItem_USBTEMP_AI(fd[0], ch/2, SENSOR_TYPE, THERMOCOUPLE);
	printf(" Select Thermocouple Type [JKSRBETN]: ");
	scanf("%s", type);
	switch(type[0]) {
	case 'J':
	  bIReg = TYPE_J;
	  printf("Type J Thermocouple Selected: \n");
	  break;
	case 'K':
	  bIReg = TYPE_K;
  	  printf("Type K Thermocouple Selected: \n");
	  break;
	case 'T':
	  bIReg = TYPE_T;
    	  printf("Type T Thermocouple Selected: \n");
	  break;
	case 'E':
	  bIReg = TYPE_E;
    	  printf("Type E Thermocouple Selected: \n");
	  break;
	case 'R':
	  bIReg = TYPE_R;
      	  printf("Type R Thermocouple Selected: \n");
	  break;
	case 'S':
	  bIReg = TYPE_S;
       	  printf("Type S Thermocouple Selected: \n");
	  break;
	case 'B':
	  bIReg = TYPE_B;
       	  printf("Type B Thermocouple Selected: \n");
	  break;
	case 'N':
	  bIReg = TYPE_N;
       	  printf("Type N Thermocouple Selected: \n");
	  break;
        default:
	  printf("Unknown or unsupported thermocopule type.\n");
	  bIReg = TYPE_K;
	  break;
	}
	fflush(stdin);
        usbSetItem_USBTC_AI(fd[0], ch/2, ch%2+CH_0_TC, bIReg);
        flag = fcntl(fileno(stdin), F_GETFL);
        fcntl(0, F_SETFL, flag | O_NONBLOCK);
	do {
          usbAin_USBTC_AI(fd[0], i, 0, &temperature);
    	  printf("Channel: %d  %.2f degress Celsius or %.2f degrees Fahrenheit.\n",
		 ch, temperature, celsius2fahr(temperature));
  	  sleep(1);
	} while (!isalpha(getchar()));
	fcntl(fileno(stdin), F_SETFL, flag);
	break;
      case 'T':
        printf("Sampling Thermistor\n");
	printf("Enter channel number [0-7]: ");
	scanf("%d", &ch);
        usbSetItem_USBTEMP_AI(fd[0], ch/2, SENSOR_TYPE, THERMISTOR);
	printf("        1.  2-wire with 1 sensor.\n");
	printf("        2.  2-wire with 2 sensors.\n");
	printf("        3.  3-wire.\n");
	printf("        4.  4-wire.\n");
	printf("Enter connector type [1-4]: \n");
	scanf("%d", &i);
	switch (i) {
	  case 1: usbSetItem_USBTEMP_AI(fd[0], ch/2, CONNECTION_TYPE, TWO_WIRE_ONE_SENSOR);break;
	  case 2: usbSetItem_USBTEMP_AI(fd[0], ch/2, CONNECTION_TYPE, TWO_WIRE_TWO_SENSOR); break;
	  case 3: usbSetItem_USBTEMP_AI(fd[0], ch/2, CONNECTION_TYPE, THREE_WIRE);
	    printf("Connection-type = 3 wire.\n");
	    break;
	  case 4: usbSetItem_USBTEMP_AI(fd[0], ch/2, CONNECTION_TYPE, FOUR_WIRE);
	    printf("Connection-type = 4 wire.\n");
	    break;
	}
	printf("Enter Steinhart-Hart coefficient A0: ");
	scanf("%f", &A0);
	printf("Enter Steinhart-Hart coefficient A1: ");
	scanf("%f", &A1);
	printf("Enter Steinhart-Hart coefficient A2: ");
	scanf("%f", &A2);
	usbSetItem_USBTEMP_AI(fd[0], ch/2, EXCITATION, MU_A_10);
	usbSetItem_USBTEMP_AI(fd[0], ch/2, CH_0_GAIN + ch%2, 0x0);      // Set for Thermnistor
	usbSetItem_USBTEMP_AI(fd[0], ch/2, CH_0_COEF_0 + ch%2, A0);     // Steinhart-Hart coefficient A0
	usbGetItem_USBTC_AI(fd[0], ch/2, CH_0_COEF_0 + ch%2, &value);
	printf("A0 = %f     ", value);
	usbSetItem_USBTEMP_AI(fd[0], ch/2, CH_0_COEF_1 + ch%2, A1);     // Steinhart-Hart coefficient A1
	usbGetItem_USBTC_AI(fd[0], ch/2, CH_0_COEF_1 + ch%2, &value);
	printf("A1 = %e     ", value);
	usbSetItem_USBTEMP_AI(fd[0], ch/2, CH_0_COEF_2 + ch%2, A2);        // Steinhart-Hart coefficient A2
	usbGetItem_USBTC_AI(fd[0], ch/2, CH_0_COEF_2 + ch%2, &value);
	printf("A2 = %e     ", value);
        flag = fcntl(fileno(stdin), F_GETFL);
        fcntl(fileno(stdin), F_SETFL, flag | O_NONBLOCK);
	do {
          usbAin_USBTC_AI(fd[0], ch, 0, &temperature);
  	  printf("Channel: %d  %.2f degress Celsius or %.2f degrees Fahrenheit.\n",
		 ch, temperature, celsius2fahr(temperature));
  	  sleep(1);
	} while (!isalpha(getchar()));
	fcntl(fileno(stdin), F_SETFL, flag);
	break;
      case 'x':
	printf("Enter number of Channels (1-4): ");
	scanf("%d", &nchan);
        if (nchan > 4) nchan = 4;
	for ( i = 0; i < nchan; i++ ) {
          printf("Connect thermocouple to channel %d\n", i);
          usbSetItem_USBTEMP_AI(fd[0], i/2, SENSOR_TYPE, THERMOCOUPLE);
	  printf(" Select Thermocouple Type [JKSRBETN]: ");
	  scanf("%s", type);
	  switch(type[0]) {
	  case 'J':
	    bIReg = TYPE_J;
	    printf("Type J Thermocouple Selected: \n");
	    break;
	  case 'K':
	    bIReg = TYPE_K;
  	    printf("Type K Thermocouple Selected: \n");
	    break;
	  case 'T':
	    bIReg = TYPE_T;
    	    printf("Type T Thermocouple Selected: \n");
	    break;
	  case 'E':
	    bIReg = TYPE_E;
    	    printf("Type E Thermocouple Selected: \n");
	    break;
	  case 'R':
	    bIReg = TYPE_R;
      	    printf("Type R Thermocouple Selected: \n");
	    break;
	  case 'S':
	    bIReg = TYPE_S;
       	    printf("Type S Thermocouple Selected: \n");
	    break;
	  case 'B':
	    bIReg = TYPE_B;
       	    printf("Type B Thermocouple Selected: \n");
	    break;
	  case 'N':
	    bIReg = TYPE_N;
       	    printf("Type N Thermocouple Selected: \n");
	    break;
          default:
	    printf("Unknown or unsupported thermocopule type.\n");
	    break;
	  }
          usbSetItem_USBTC_AI(fd[0], i/2, i%2+CH_0_TC, bIReg);
	}
	fflush(stdin);
        flag = fcntl(fileno(stdin), F_GETFL);
        fcntl(0, F_SETFL, flag | O_NONBLOCK);
	do {
          usbAinScan_USBTC_AI(fd[0], CH0, nchan-1, 0, temperature_array);
	  for ( i = 0; i < nchan; i++ ) {
  	    printf("Channel %d:  %.2f degress Celsius or %.2f degrees Fahrenheit.\n",
		   i, temperature_array[i], celsius2fahr(temperature_array[i]));
	  }
	  printf("\n");
	  sleep(1);
	} while (!isalpha(getchar()));
	fcntl(fileno(stdin), F_SETFL, flag);
	break;
      case 'v':
      	printf("Select Channel [4-7]: ");
        scanf("%d", &i);
        if ( i < 4 || i > 7 ) {
	printf("Channel must be between 4-7 inclusive.  Setting to 4\n");
	i = 4;
    	}
	//	usbSetItem_USBTC_AI(fd[0], i/2, SENSOR_TYPE, VOLTAGE);
		usbSetItem_USBTC_AI(fd[0], i/2, i%2+CH_0_VOLT_CONN, DIFFERENTIAL);
		usbSetItem_USBTC_AI(fd[0], i/2, i%2+CH_0_GAIN, BP_10V);
        flag = fcntl(fileno(stdin), F_GETFL);
        fcntl(0, F_SETFL, flag | O_NONBLOCK);
	do {
          usbAin_USBTC_AI(fd[0], i, 0, &volts);
    	  printf("Channel: %d  %.2f Volts.\n", i, volts);
  	  sleep(1);
	} while (!isalpha(getchar()));
	fcntl(fileno(stdin), F_SETFL, flag);
        break;
      default:
        break;
    }
  }
}
