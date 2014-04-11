/*
 *
 *  Copyright (c) 2004-2005  Warren Jasper <wjasper@tx.ncsu.edu>
 *                           Mike Erickson <merickson@nc.rr.com>
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
#include <time.h>
#include <fcntl.h>
#include <ctype.h>
#include <sys/types.h>
#include <asm/types.h>

#include "pmd.h"
#include "usb-1208FS.h"

/* Test Program */
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
  
  int fd[4];
  int flag;
  signed short svalue;
  __u8 input, channel, gain, options;
  __u8 lowChan, highChan;
  __u16 value;
  __u16 out_data[1024];
  signed short in_data[1024];
  int count;
  int temp, i, j;
  int ch;
  int nInterfaces = 0;
  float freq;
  time_t startTime, endTime;

  nInterfaces = PMD_Find(MCC_VID, USB1208FS_PID, fd);

  if ( nInterfaces <= 0 ) {
    fprintf(stderr, "USB 1208FS not found.\n");
    exit(1);
  } else
    printf("USB 1208FS Device is found! Number of Interfaces = %d\n",
	   nInterfaces);

  /* config mask 0x01 means all inputs */
  usbDConfigPort_USB1208FS(fd[0], DIO_PORTA, DIO_DIR_OUT);
  usbDConfigPort_USB1208FS(fd[0], DIO_PORTB, DIO_DIR_IN);
  usbDOut_USB1208FS(fd[0], DIO_PORTA, 0);
  usbDOut_USB1208FS(fd[0], DIO_PORTA, 0);

  while(1) {
    printf("\nUSB 1208FS Testing\n");
    printf("----------------\n");
    printf("Hit 'a' to test analog output scan\n");    
    printf("Hit 'b' to blink LED\n");
    printf("Hit 'c' to test counter\n");
    printf("Hit 'e' to exit\n");
    printf("Hit 'd' to test digital I/O\n");
    printf("Hit 'g' to test analog input scan (differential)\n");
    printf("Hit 'j' to test analog input scan (single ended)\n");
    printf("Hit 'i' to test analog input (differential)\n");
    printf("Hit 'h' to test analog input (single ended)\n");
    printf("Hit 'o' to test analog output\n");
    printf("Hit 'r' to reset\n");
    printf("Hit 's' to get status\n");
    printf("Hit 'n' to get serial number\n");
    
    while((ch = getchar()) == '\0' || ch == '\n');

    switch(tolower(ch)) {
      case 'b': /* test to see if led blinks */
        usbBlink_USB1208FS(fd[0]);
        break;
      case 'c':
        printf("connect pin 20 and 21\n");
        usbInitCounter_USB1208FS(fd[0]);
        sleep(1);
        flag = fcntl(fileno(stdin), F_GETFL);
        fcntl(0, F_SETFL, flag | O_NONBLOCK);
        do {
          usbDOut_USB1208FS(fd[0], DIO_PORTA, 1);
	  sleep(1);
          usbDOut_USB1208FS(fd[0], DIO_PORTA, 0);
	  printf("Counter = %d\n",usbReadCounter_USB1208FS(fd[0]));
        } while (!isalpha(getchar()));
        fcntl(fileno(stdin), F_SETFL, flag);
        break;
      case 'd':
        printf("\nTesting Digital I/O....\n");
        printf("connect pins 21 through 28 <=> 32 through 39\n");
        do {
          printf("Enter a byte number [0-0xff]: " );
          scanf("%x", &temp);
          usbDOut_USB1208FS(fd[0], DIO_PORTA, (__u8)temp);
          usbDIn_USB1208FS(fd[0], DIO_PORTB, &input);
          printf("The number you entered = %#x\n",input);
        } while (toContinue());
        break;
      case 'o': /* test the analog output */
        printf("Testing the analog output...\n");
        printf("Enter channel [0-1] => (pin 13-14):");
        scanf("%d", &temp);
        channel = (__u8) temp;
        for ( i = 0; i < 3; i++ ) {
          for ( value = 0; value < 0xfff; value++ ) {
	    usbAOut_USB1208FS(fd[0], channel, value);
	  }
        }
        break;
      case 'a': /* test Analog Output Scan */
        printf("Enter desired frequency [Hz]: ");
        scanf("%f", &freq);
        for ( j = 0; j <  freq; j++ ) {
	  for (i = 0; i < 1024; i++) {
	    out_data[i] = i%2 ? 0 : 0xfff;
	  }
	  usbAOutScan_USB1208FS(fd, 0, 0, 1024, &freq, out_data);
	}
	break;
      case 'j':
        printf("Test of scan mode (single ended).\n");
        printf("Enter desired frequency [Hz]: ");
        scanf("%f", &freq);
        printf("Enter number of samples [1-1024]: ");
        scanf("%d", &count);
	printf("Enter Low Channel [0-7]: ");
        scanf("%hhd", &lowChan);
	printf("Enter High Channel [0-7]: ");
        scanf("%hhd", &highChan);

	options = AIN_EXECUTION | AIN_GAIN_QUEUE;
        for ( i = 0; i < 1024; i++ ) {  // load data with known value
	  in_data[i] = 0xbeef;
	}
        usbAInScan_USB1208FS_SE(fd, lowChan, highChan, count, &freq, options, in_data);
	for ( i = 0; i < count; i++ ) {
	  printf("data[%d] = %#hx  %.2fV\n", i, in_data[i], volts_SE(in_data[i]));
	}
	break;
      case 'g':
        printf("Enter desired frequency [Hz]: ");
        scanf("%f", &freq);
        printf("Enter number of samples [1-1024]: ");
        scanf("%d", &count);
        printf("\t\t1. +/- 20.V\n");
        printf("\t\t2. +/- 10.V\n");
        printf("\t\t3. +/- 5.V\n");
        printf("\t\t4. +/- 4.V\n");
        printf("\t\t5. +/- 2.5V\n");
        printf("\t\t6. +/- 2.0V\n");
        printf("\t\t7. +/- 1.25V\n");
        printf("\t\t8. +/- 1.0V\n");
        printf("Select gain: [1-8]\n");
        scanf("%d", &temp);
        switch(temp) {
          case 1: gain = BP_20_00V;
            break;
          case 2: gain = BP_10_00V;
            break;
          case 3: gain = BP_5_00V;
            break;
          case 4: gain = BP_4_00V;
            break;
          case 5: gain = BP_2_50V;
            break;
          case 6: gain = BP_2_00V;
            break;
          case 7: gain = BP_1_25V;
            break;
          case 8: gain = BP_1_00V;
            break;
          default:
            break;
	}
        svalue = usbAIn_USB1208FS(fd[0], 0, gain);
	options = AIN_EXECUTION;
        for ( i = 0; i < 1024; i++ ) {  // load data with known value
	  in_data[i] = 0xbeef;
	}
        usbAInScan_USB1208FS(fd, 0, 0, count, &freq, options, in_data);
	for ( i = 0; i < count; i++ ) {
	  printf("data[%d] = %#hx  %.2fV\n", i, in_data[i], volts_FS(gain, in_data[i]));
	}
	break;
      case 'h':
        printf("Testing Analog Input Single Ended Mode\n");
        printf("Select channel [0-7]: ");
        scanf("%d", &temp);
	channel = (__u8) (temp);
	gain =  SE_10_00V;
        flag = fcntl(fileno(stdin), F_GETFL);
        fcntl(0, F_SETFL, flag | O_NONBLOCK);
        do {
          sleep(1);
	  svalue = usbAIn_USB1208FS(fd[0], channel, gain);
	  printf("Channel: %d: value = %#hx, %.2fV\n",
		 channel, svalue, volts_SE(svalue));
	} while (!isalpha(getchar()));
	fcntl(fileno(stdin), F_SETFL, flag);
	break;
      case 'i':
        printf("Connect pin 1 - pin 21  and pin 2 - pin 3\n");
        printf("Select channel [0-3]: ");
        scanf("%d", &temp);
        if ( temp < 0 || temp > 3 ) break;
        channel = (__u8) temp;
        printf("\t\t1. +/- 20.V\n");
        printf("\t\t2. +/- 10.V\n");
        printf("\t\t3. +/- 5.V\n");
        printf("\t\t4. +/- 4.V\n");
        printf("\t\t5. +/- 2.5V\n");
        printf("\t\t6. +/- 2.0V\n");
        printf("\t\t7. +/- 1.25V\n");
        printf("\t\t8. +/- 1.0V\n");
        printf("Select gain: [1-8]\n");
        scanf("%d", &temp);
        switch(temp) {
          case 1: gain = BP_20_00V;
            break;
          case 2: gain = BP_10_00V;
            break;
          case 3: gain = BP_5_00V;
            break;
          case 4: gain = BP_4_00V;
            break;
          case 5: gain = BP_2_50V;
            break;
          case 6: gain = BP_2_00V;
            break;
          case 7: gain = BP_1_25V;
            break;
          case 8: gain = BP_1_00V;
            break;
          default:
            break;
	}
        printf("Hit s <CR> to stop.\n ");
        flag = fcntl(fileno(stdin), F_GETFL);
        fcntl(0, F_SETFL, flag | O_NONBLOCK);
        do {
          usbDOut_USB1208FS(fd[0], DIO_PORTA, 0);
	  sleep(1);
	  svalue = usbAIn_USB1208FS(fd[0], channel, gain);
	  printf("Channel: %d: value = %#hx, %.2fV\n",
		 channel, svalue, volts_FS(gain, svalue));
          usbDOut_USB1208FS(fd[0], DIO_PORTA, 0x1);
	  sleep(1);
	  svalue = usbAIn_USB1208FS(fd[0], channel, gain);
	  printf("Channel: %d: value = %#hx, %.2fV\n",
		 channel, svalue, volts_FS(gain, svalue));
	} while (!isalpha(getchar()));
	fcntl(fileno(stdin), F_SETFL, flag);
        printf("Doing a timing test.  Please wait ...\n");
        time(&startTime);
        for (count = 0; count < 500; count++) {
	  svalue = usbAIn_USB1208FS(fd[0], channel, gain);
	}
        time(&endTime);
        printf("Sampling speed is %ld Hz.\n", 500/(endTime - startTime));
	break;
      case 's':
        printf("Status = %#x\n", usbGetStatus_USB1208FS(fd[0]));
	break;
      case 'r':
        usbReset_USB1208FS(fd[0]);
        return 0;
	break;
      case 'e':
        close(fd[0]);
        close(fd[1]);
        close(fd[2]);
        close(fd[3]);
        return 0;
	break;
      case 'n':
	printf("Serial Number = %s\n", PMD_GetSerialNumber(fd[0]));
	break;
      default:
        break;
    }
  }
}
