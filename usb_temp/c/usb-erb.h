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

#ifndef USB_ERB_H
#define USB_ERB_H

#ifdef __cplusplus
extern "C" { 
#endif 

#define USBERB08_PID  (0x008b)
#define USBERB24_PID  (0x008a)

#define DIO_PORTA     (0x0)
#define DIO_PORTB     (0x1)
#define DIO_PORTC_LOW (0x2)
#define DIO_PORTC_HI  (0x3)

/* Commands and Codes for USB ERB08/24 HID reports */
#define DIN              (0x03) // Read digital port
#define DOUT             (0x04) // Write digital port
#define DBIT_IN          (0x05) // Read Digital port bit
#define DBIT_OUT         (0x06) // Write Digital port bit

#define MEM_READ         (0x30) // Read Memory
#define MEM_WRITE        (0x31) // Write Memory

#define BLINK_LED        (0x40) // Causes LED to blink
#define RESET            (0x41) // Reset USB interface
#define GET_STATUS       (0x44) // Retrieve device status
#define GET_TEMP         (0x47) // Retrieve board temperature

#define PREPARE_DOWNLOAD (0x50) // Prepare for program memory download
#define WRITE_CODE       (0x51) // Write program memory
#define WRITE_SERIAL     (0x53) // Write new serial number to device
#define READ_CODE        (0x55) // Read program memory

  
/* function prototypes for the USB-ERB */
__u8 usbDIn_USBERB(int fd, __u8 port);
void usbDOut_USBERB(int fd, __u8 port, __u8 value);
__u8 usbDBitIn_USBERB(int fd, __u8 port, __u8 bit);
void usbDBitOut_USBERB(int fd, __u8 port, __u8 bit, __u8 value);
void usbReadMemory_USBERB(int fd, __u16 address, __u8 count, __u8* memory);
int usbWriteMemory_USBERB(int fd, __u16 address, __u8 count, __u8* data);
int usbBlink_USBERB(int fd);
int usbReset_USBERB(int fd);
__u16 usbGetStatus_USBERB(int fd);
float usbGetTemp_USBERB(int fd);

void usbPrepareDownload_USBERB(int fd);
void usbWriteSerial_USBERB(int fd, __u8 serial[8]);
void usbWriteCode_USBERB(int fd, __u32 address, __u8 count, __u8 data[]);
int usbReadCode_USBERB(int fd, __u32 address, __u8 count, __u8 data[]);

#ifdef __cplusplus
} /* closing brace for extern "C" */
#endif

#endif //USB_ERB_H



