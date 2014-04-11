/*
 *
 *  Copyright (c) 2006-2012  Warren Jasper <wjasper@tx.ncsu.edu>
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
#include "usb-3100.h"

#define FS_DELAY 1000

static USB31XX_CalibrationTable CalTable[NCHAN_31XX];

/* configures digital port */
void usbDConfigPort_USB31XX(int fd, __u8 direction)
{
  __u8 cmd[1];

  cmd[0] = direction;

  PMD_SendOutputReport(fd, DCONFIG, cmd, sizeof(cmd), FS_DELAY);
}

/* configures digital bit */
void usbDConfigBit_USB31XX(int fd, __u8 bit_num, __u8 direction)
{
  __u8 cmd[2];

  cmd[0] = bit_num;
  cmd[1] = direction;

  PMD_SendOutputReport(fd, DCONFIG_BIT, cmd, sizeof(cmd), FS_DELAY);
}

/* reads digital port  */
void usbDIn_USB31XX(int fd, __u8* value)
{
  PMD_SendOutputReport(fd, DIN, 0, 0, FS_DELAY);
  PMD_GetInputReport(fd, DIN, value, sizeof(value), FS_DELAY);
 
  return;
}

/* reads digital bit  */
void usbDInBit_USB31XX(int fd, __u8 bit_num, __u8* value)
{
  __u8 cmd[1];

  cmd[0] = bit_num;

  PMD_SendOutputReport(fd, DBIT_IN, cmd, sizeof(cmd), FS_DELAY);
  PMD_GetInputReport(fd, DBIT_IN, value, sizeof(*value), FS_DELAY);
 
  return;
}

/* writes digital port */
void usbDOut_USB31XX(int fd, __u8 value)
{
  __u8 cmd[1];

  cmd[0] = value;

  PMD_SendOutputReport(fd, DOUT, cmd, sizeof(cmd), FS_DELAY);
}

/* writes digital bit  */
void usbDOutBit_USB31XX(int fd, __u8 bit_num, __u8 value)
{
  __u8 cmd[2];

  cmd[0] = bit_num;
  cmd[1] = value;

  PMD_SendOutputReport(fd, DBIT_OUT, cmd, sizeof(cmd), FS_DELAY);
  return;
}

/* Analog Out */
void usbAOutConfig_USB31XX(int fd, __u8 channel, __u8 range)
{
  __u8 cmd[2];
  __u16 address;

  if (channel > NCHAN_31XX) channel = NCHAN_31XX;
  cmd[0] = channel;
  cmd[1] = range;

  switch (range) {
    case UP_10_00V:
      address = 0x100 + 0x10*channel;
      break;
    case BP_10_00V:
      address = 0x108 + 0x10*channel;
      break;
    case I_0_20_mA:
      address = 0x200 + 0x8*channel;
      cmd[1] = 0;
      break;
    default:
      address = 0x100 + 0x10*channel;
  }

  PMD_SendOutputReport(fd, AOUT_CONFIG, cmd, sizeof(cmd), FS_DELAY);
  usbReadMemory_USB31XX(fd, address, sizeof(float), (__u8*) &CalTable[channel].slope);
  usbReadMemory_USB31XX(fd, address+0x4, sizeof(float), (__u8*) &CalTable[channel].offset);
  printf("Channel = %d    Slope = %f    Offset = %f\n", channel, CalTable[channel].slope, CalTable[channel].offset);
}
 
/* writes to analog out */
void usbAOut_USB31XX(int fd, __u8 channel, __u16 value, __u8 update)
{
  __u8 cmd[4];
  double dvalue;

  if (update != 1) update = 0;
  if (channel > NCHAN_31XX) channel = NCHAN_31XX;

  dvalue = CalTable[channel].slope*value + CalTable[channel].offset;

  if (dvalue > 0xffff) {
    value = 0xffff;
  } else if (dvalue < 0) {
    value = 0;
  } else {
    value = (__u16) dvalue;
  }

  cmd[0] = channel;                         // 0 - 15
  cmd[1] = (__u8) (value & 0xff);           // low byte
  cmd[2] = (__u8) ((value >> 0x8) & 0xff);  // high byte
  cmd[3] = update;

  PMD_SendOutputReport(fd, AOUT, cmd, sizeof(cmd), FS_DELAY);
}

void usbAOutSync_USB31XX(int fd)
{
  PMD_SendOutputReport(fd, AOUT_SYNC, 0, 0, FS_DELAY);
}

/* Initialize the counter */
void usbInitCounter_USB31XX(int fd)
{
  PMD_SendOutputReport(fd, CINIT, 0, 0, FS_DELAY);
}

__u32 usbReadCounter_USB31XX(int fd)
{
  __u32 value;

  PMD_SendOutputReport(fd, CIN, 0, 0, FS_DELAY);
  PMD_GetInputReport(fd, CIN, (__u8  *) &value, sizeof(value), FS_DELAY);

  return value;
}

/* blinks the LED of USB device */
void usbBlink_USB31XX(int fd, __u8 count)
{
  __u8 cmd[1];

  cmd[0] = count;

  PMD_SendOutputReport(fd, BLINK_LED, cmd, sizeof(cmd), FS_DELAY);
}

int usbReset_USB31XX(int fd)
{
  return PMD_SendOutputReport(fd, RESET, 0, 0, FS_DELAY);
}

void usbSetSync_USB31XX(int fd, __u8 type)
{
  PMD_SendOutputReport(fd, SET_SYNC, &type, sizeof(type), FS_DELAY);
}

__u16 usbGetStatus_USB31XX(int fd)
{
  __u16 status;

  PMD_SendOutputReport(fd, GET_STATUS, 0, 0, FS_DELAY);
  PMD_GetInputReport(fd, GET_STATUS, (__u8 *) &status, sizeof(status), FS_DELAY);
  return status;
}

void usbReadMemory_USB31XX( int fd, __u16 address, __u8 count, __u8* memory)
{
  // Addresses 0x000  - 0x0FF address  of EEPROM
  // Addresses 0x0100 - 0x02FF address of FLASH
  
  struct arg {
    __u16 address;
    __u8 type;  // not used
    __u8 count; // number of bytes to be read.  62 max.
  } arg;

  if ( count > 62 ) count = 62;
  arg.address = address;
  arg.count = count;

  PMD_SendOutputReport(fd, MEM_READ, (__u8 *) &arg, sizeof(arg), FS_DELAY);
  PMD_GetInputReport(fd, MEM_READ, memory, count, FS_DELAY);
}

int usbWriteMemory_USB31XX(int fd, __u16 address, __u8 count, __u8 data[])
{
  /*
    This command writes to the non-volatile memory on the device.  The
    non-volatile memory is used to store calibration coefficients,
    system information, and user data.  There are 256 bytes of EEPROM
    (address 0x0000 - 0x00FF) available for general use and 512 bytes
    of FLASH (address 0x0100 - 0x2FF) used for calibration.

    The EEPROM may be written at any address 1 - 59 bytes of data in a
    write.

    The FLASH memory has stricter requirements for writing.  The
    memory is written in blocks of 32 bytes and erased in sectors of
    64 bytes.  The FLASH memory must be erased before being written.
    To ensure this, when writing to FLASH, the firmware will AND the
    start address with 0xFFE0.  If the bit 0x0020 is clear, this write
    is the first 32 bytes of a sector and the sector will be erased.
    Once erased, the first block will be written.  Do not have a
    starting address to the FLASH that does not begin on a 32-byte
    boundary.  The count should be 32 bytes when writing to FLASH, and
    any more than that will be truncated.

    The FLASH memory is reserved for calibration data and requires the unlock
    sequence prior to writing.

    Unlock sequence: Write 2 bytes with the value 0xaa55 to address
    0x500 to unlock.  The unlock status can be checked with GetStatus.
    The unlock will remain in effect until the device is powered off
    or reset.
  */
    
  struct arg {
    __u16 address;
    __u8 count;
    __u8 data[count];
  } arg;

  if (address <= 0x00ff) {  // EEPROM
    if (count > 59) {
      printf("Maximum of 59 bytes allow when writing to EEPROM\n");
      return -1;
    }
  } else if (address >= 0x0100 && address <= 0x02ff) {  // FLASH
    if (count != 32) {
      printf("Count must equal 32 bytes.\n");
      return -1;
    }
    if (address & ~0x1f) {
      printf("Address must be on a 32 bit boundary.\n");
      return -1;
    }
  } else {
    printf("Invalid address %#x\n", address);
    return -1;
  }
  
  arg.address = address;
  arg.count = count;
  memcpy(arg.data, data, count);
  PMD_SendOutputReport(fd, MEM_WRITE, (__u8 *) &arg, sizeof(arg), FS_DELAY);
  return 0;
}

void usbPrepareDownload_USB31XX(int fd)
{
  /*
    This command puts the device into code update mode.  The unlock code must be correct as a
    further safety device.  Call this once before sending code with usbWriteCode.  If not in
    code update mode, any usbWriteCode will be ignored.  A usbReset command must be issued at
    the end of the code download in order to return the device to operation with the new code.
  */

  __u8 unlock_code = 0xad;

  PMD_SendOutputReport(fd, PREPARE_DOWNLOAD, &unlock_code, sizeof(__u8), FS_DELAY);
}

int usbWriteCode_USB31XX(int fd, __u32 address, __u8 count, __u8 data[])
{
  /*
    This command writes to the program memory in the device.  This
    command is not accepted unless the device is in update mode.  The
    command will normally be used when downloading a new hex file, so
    it supports the memory ranges that may be found in the hex file.

    The address ranges are:

    0x000000 - 0x007AFF:  FLASH program memory
    0x200000 - 0x200007:  ID memory (serial number is stored here)
    0x300000 - 0x30000F:  CONFIG memory (processor configuration data)
    0xF00000 - 0xF03FFF:  EEPROM memory

    FLASH program memory: The device must receive data in 64-byte
    segments that begin on a 64 byte boundary.  The data is sent in
    messages containing 32 bytes.  count must always equal 32.

    Other memory: Any number up to the maximum may be sent.

  */

  struct t_arg {
    __u8 address[3];
    __u8 count;        // 32 bytes max
    __u8 data[32];     // the program data, 32 bytes max
  } arg;

  if (count > 32) count = 32;

  if (address <= 0x007aff) {  // FLASH
    count = 32;
    if (address & ~0x1f) {
      printf("Address must be on a 32 bit boundary.\n");
      return -1;
    }
  }

  memcpy(&arg.address[0], &address, 3);   // 24 bit address
  arg.count = count;                      // number of bytes to be written
  memcpy(&arg.data[0], data, count);      
  PMD_SendOutputReport(fd, WRITE_CODE, (__u8 *) &arg, count+4, FS_DELAY);
  return count;
}

void usbWriteSerial_USB31XX(int fd, __u8 serial[8])
{
  // Note: The new serial number will be programmed but not used until hardware reset.
  
  PMD_SendOutputReport(fd, WRITE_SERIAL, serial, 8, FS_DELAY);
}
