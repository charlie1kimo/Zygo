/*
 *
 *  Copyright (c) 2006        Warren Jasper <wjasper@tx.ncsu.edu>
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
#include "usb-pdiso8.h"

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
  int temp;
  int ch;
  int nInterfaces;
  char serial[9];
  __u8 port;
  __u8 pin = 0;
  __u8 bit_value;

  if ((nInterfaces = PMD_Find(MCC_VID, USBPDISO8_PID, &fd)) > 0) {
   printf("USB PDISO8 Device is found! Number of Interfaces = %d\n", nInterfaces);
  } else if ((nInterfaces = PMD_Find(MCC_VID, USBSWITCH_AND_SENSE_PID, &fd)) > 0) {
   printf("USB Switch & Sense 8/8 Device is found! Number of Interfaces = %d\n", nInterfaces);
  } else {
    fprintf(stderr, "USB PDISO8 24 & 08  or Switch & Sense 8/8 not found.\n");
    exit(1);	
  }

  while(1) {
    printf("\nUSB PDISO8 or Switch & Sense 8/8 Testing\n");
    printf("----------------\n");
    printf("Hit 'b' to blink LED\n");
    printf("Hit 'd' to test digital I/O \n");
    printf("Hit 'e' to exit\n");
    printf("Hit 'g' to get serial number\n");
    printf("Hit 't' to test digital bit I/O\n");
    
    while((ch = getchar()) == '\0' || ch == '\n');
    
    switch(ch) {
    case 'b': /* test to see if led blinks */
      usbBlink_USBPDISO8(fd);
      break;
    case 'd':
      printf("\nTesting Digital I/O....\n");
      do {
	printf("Enter a port number: 0 - Relay Port, 1 - ISO Port: ");
	scanf("%hhd", &port);
	switch (port) {
          case 0:  // Relay Port output only
            printf("Enter a byte number [0-0xff] : " );
            scanf("%x", &temp);
            usbDOut_USBPDISO8(fd, port, (__u8)temp);
            break;
          case 1:  // ISO Port input only
	    printf("ISO Port = %#x\n", usbDIn_USBPDISO8(fd, port));
	    break;
          default:
	    printf("Invalid port number.\n");
            break;
	}
      } while (toContinue());
      break;
    case 'g':
      strncpy(serial, PMD_GetSerialNumber(fd), 9);
      printf("Serial Number = %s\n", serial);
      break;
    case 't':
      do {
	printf("\nTesting Digital Bit I/O....\n");
	printf("Enter a port number: 0 - Relay Port, 1 - ISO Port: ");
	scanf("%hhd", &port);
	printf("Select the Pin in port  %d  [0-7] :", port);
	scanf("%hhd", &pin);
	if (pin > 7) break;
	switch (port) {
        case 0:  // Relay Port output only
	  printf("Enter a bit value for output (0 | 1) : ");
	  scanf("%hhd", &bit_value);
	  usbDBitOut_USBPDISO8(fd, port, pin, bit_value);
          break;
	case 1:
	  printf("ISO Port = %d  Pin = %d, Value = %d\n", port, pin, usbDBitIn_USBPDISO8(fd, port, pin));
          break;
	default:
	  printf("Invalid port number.\n");
	  break;
	}
      } while (toContinue());
      break;    
    case 'e':
      close(fd);
      return 0;
      break;
    default:
      break;
    }
  }
}
  



