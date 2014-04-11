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

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <asm/types.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <linux/hiddev.h>

#include "pmd.h"
#include "usb-pdiso8.h"

#define FS_DELAY (1000)

/* reads digital port  */
__u8 usbDIn_USBPDISO8(int fd, __u8 port)
{
  __u8 value;
  
  PMD_SendOutputReport(fd, DIN, &port, 1, FS_DELAY);
  PMD_GetInputReport(fd, DIN, &value, sizeof(value), FS_DELAY);
  return value;
}

/* writes digital port */
void usbDOut_USBPDISO8(int fd, __u8 port, __u8 value) 
{
  __u8 cmd[2];
  
  cmd[0] = port;
  cmd[1] = value;

  PMD_SendOutputReport(fd, DOUT, cmd, sizeof(cmd), FS_DELAY);
}

/* reads digital port bit */
__u8 usbDBitIn_USBPDISO8(int fd, __u8 port, __u8 bit) 
{
  __u8 cmd[2];
  __u8 value;

  cmd[0] = port;
  cmd[1] = bit;

  PMD_SendOutputReport(fd, DBIT_IN, cmd, sizeof(cmd), FS_DELAY);
  PMD_GetInputReport(fd, DBIT_IN, &value, sizeof(value), FS_DELAY);

  return value;
}

/* writes digital port bit */
void usbDBitOut_USBPDISO8(int fd, __u8 port, __u8 bit, __u8 value)
{
  __u8 cmd[3];
  
  cmd[0] = port;
  cmd[1] = bit;
  cmd[2] = value;

  PMD_SendOutputReport(fd, DBIT_OUT, cmd, sizeof(cmd), FS_DELAY);
}

void usbReadMemory_USBPDISO8(int fd, __u16 address, __u8 count, __u8* memory)
{
  /*
    This command reads data from the configuration memory (EEPROM). All
    memory may be read.  Max number of bytes read is 4.
  */
  
  struct arg {
    __u16 address;
    __u8 type;
    __u8 count;
  } arg;

  if ( count > 4 ) count = 4;
  arg.type = 0;      // unused for this device.
  arg.address = address;
  arg.count = count;

  PMD_SendOutputReport(fd, MEM_READ, (__u8 *) &arg, sizeof(arg), FS_DELAY);
  PMD_GetInputReport(fd, MEM_READ, memory, count, FS_DELAY);
}

int usbWriteMemory_USBPDISO8(int fd, __u16 address, __u8 count, __u8* data)
{
  // Locations 0x00-0x0F are reserved for firmware and my not be written.
  
  int i;
  struct arg {
    __u16 address;
    __u8 count;
    __u8 data[count];
  } arg;

  if ( address <= 0xf ) return -1;
  if ( count > 4 ) count = 4;
  
  arg.address = address;
  arg.count = count;
  for ( i = 0; i < count; i++ ) {
    arg.data[i] = data[i];
  }
  PMD_SendOutputReport(fd, MEM_WRITE, (__u8 *) &arg, sizeof(arg), FS_DELAY);
  return 0;
}

/* blinks the LED of USB device */
int usbBlink_USBPDISO8(int fd)
{
  return PMD_SendOutputReport(fd, BLINK_LED, 0, 0, FS_DELAY);
}

void usbWriteSerial_USBPDISO8(int fd, __u8 serial[8])
{
  // Note: The new serial number will be programmed but not used until hardware reset.
  
  PMD_SendOutputReport(fd, WRITE_SERIAL, serial, 8, FS_DELAY);
}
