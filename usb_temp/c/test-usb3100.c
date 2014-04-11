/*
 *
 *  Copyright (c) 2006  Warren Jasper <wjasper@tx.ncsu.edu>
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

/*
 * your kernel needs to be configured with /dev/usb/hiddev support
 * I think most distros are already
 *
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
#include "usb-3100.h"

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

  int fd = -1;
  int flag;
  __u8 channel;
  int temp, i;
  int ch;
  int nInterfaces = 0;
  __u16 value;
  char serial[9];
  __u8 memory[62];

  
  if ((nInterfaces = PMD_Find(MCC_VID, USB3101_PID, &fd)) > 0) {
    printf("USB 3101 Device is found! Number of Interfaces = %d\n", nInterfaces);
  } else if ((nInterfaces = PMD_Find(MCC_VID, USB3102_PID, &fd)) > 0) {
    printf("USB 3102 Device is found! Number of Interfaces = %d\n", nInterfaces);
  } else if ((nInterfaces = PMD_Find(MCC_VID, USB3103_PID, &fd)) > 0) {
    printf("USB 3103 Device is found! Number of Interfaces = %d\n", nInterfaces);
  } else if ((nInterfaces = PMD_Find(MCC_VID, USB3104_PID, &fd)) > 0) {
    printf("USB 3104 Device is found! Number of Interfaces = %d\n", nInterfaces);
  } else if ((nInterfaces = PMD_Find(MCC_VID, USB3105_PID, &fd)) > 0) {
    printf("USB 3105 Device is found! Number of Interfaces = %d\n", nInterfaces);
  } else if ((nInterfaces = PMD_Find(MCC_VID, USB3106_PID, &fd)) > 0) {
    printf("USB 3106 Device is found! Number of Interfaces = %d\n", nInterfaces);
  } else if ((nInterfaces = PMD_Find(MCC_VID, USB3110_PID, &fd)) > 0) {
    printf("USB 3110 Device is found! Number of Interfaces = %d\n", nInterfaces);
  } else if ((nInterfaces = PMD_Find(MCC_VID, USB3112_PID, &fd)) > 0) {
    printf("USB 3112 Device is found! Number of Interfaces = %d\n", nInterfaces);
  } else if ((nInterfaces = PMD_Find(MCC_VID, USB3114_PID, &fd)) > 0) {
    printf("USB 3114 Device is found! Number of Interfaces = %d\n", nInterfaces);
  } else {
    fprintf(stderr, "USB 31XX  not found.\n");
    exit(1);	
  }

  /* config mask 0x01 means all inputs */
  usbDConfigPort_USB31XX(fd, DIO_DIR_OUT);
  usbDOut_USB31XX(fd, 0);

  // Configure all analog channels for 0-10V output
  for (i = 0; i < 8; i++) {
    usbAOutConfig_USB31XX(fd, i, UP_10_00V);
  }

  while(1) {
    printf("\nUSB 31XX Testing\n");
    printf("----------------\n");
    printf("Hit 'a' for analog out\n");
    printf("Hit 'b' to blink \n");
    printf("Hit 'c' to test counter\n");
    printf("Hit 'd' to test digital output\n");
    printf("Hit 'e' to exit\n");
    printf("Hit 'g' to get serial number\n");
    printf("Hit 'r' to reset\n");
    printf("Hit 's' to get status\n");
    printf("Hit 'R' to read memory\n");

    while((ch = getchar()) == '\0' ||
      ch == '\n');

    switch(ch) {
      case 'a':
	printf("Testing the analog output...\n");
        printf("Enter channel [0-15]:");
        scanf("%d", &temp);
        channel = (__u8) temp;
	for (value = 0; value < 0xff10; value += 0x10) {
	  usbAOut_USB31XX(fd, channel, value, 0);
	}
        usbAOut_USB31XX(fd, channel, 0x0, 0);
        break;
      case 'b': /* test to see if led blinks  4 times*/
        usbBlink_USB31XX(fd, 4);
        break;
      case 'c':
        printf("connect CTR and DIO0\n");
        usbInitCounter_USB31XX(fd);
        sleep(1);
        flag = fcntl(fileno(stdin), F_GETFL);
        fcntl(0, F_SETFL, flag | O_NONBLOCK);
        do {
          usbDOut_USB31XX(fd, 1);
	  usleep(200000);
          usbDOut_USB31XX(fd, 0);
	  printf("Counter = %d\n",usbReadCounter_USB31XX(fd));
        } while (!isalpha(getchar()));
        fcntl(fileno(stdin), F_SETFL, flag);
        break;
      case 'd':
	printf("\nTesting Digital I/O....\n");
        printf("Enter a byte number [0-0xff]: " );
        scanf("%x", &temp);
        usbDConfigPort_USB31XX(fd, DIO_DIR_OUT);
        usbDOut_USB31XX(fd, (__u8)temp);
        break;
      case 's':
        printf("Status = %#x\n", usbGetStatus_USB31XX(fd));
	break;
      case 'r':
        usbReset_USB31XX(fd);
        return 0;
	break;
      case 'e':
        close(fd);
        return 0;
	break;
      case 'g':
        strncpy(serial, PMD_GetSerialNumber(fd), 9);
        printf("Serial Number = %s\n", serial);
        break;
      case 'R':
        memset(memory, 0x0, 62);
        usbReadMemory_USB31XX(fd, 0x0000, 60, memory);
        printf("reading from EEPROM: \n");
	for (i = 0; i < 62; i+=2) {
	  printf("address = %#x \t value = %#x \t\t", i, memory[i]);
  	  printf("address = %#x \t value = %#x \t\n", i+1, memory[i+2]);
	}
	memset(memory, 0x0, 62);
        usbReadMemory_USB31XX(fd, 0x0100, 62, memory);
        printf("\nreading from FLASH: \n");
	for (i = 0; i < 62; i+=2) {
	  printf("address = %#x \t value = %#x \t\t", i+0x100, memory[i]);
  	  printf("address = %#x \t value = %#x \t\n", i+0x101, memory[i+2]);
	}
        break;
      default:
        break;
    }
  }
}
