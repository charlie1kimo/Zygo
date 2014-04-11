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
#include "usb-4303.h"

#define FS_DELAY (1000)
__u8 usbDIn_USB4303(int fd)
{
  __u8 value;
  
  PMD_SendOutputReport(fd, DIN, 0, 0, FS_DELAY);
  PMD_GetInputReport(fd, DIN, &value, sizeof(value), FS_DELAY);
  return value;
}

/* writes digital port */
void usbDOut_USB4303(int fd, __u8 value) 
{
  PMD_SendOutputReport(fd, DOUT, &value, sizeof(value), FS_DELAY);
}

/* reads digital port bit */
__u8 usbDBitIn_USB4303(int fd, __u8 bit) 
{
  __u8 value;

  PMD_SendOutputReport(fd, DBIT_IN, &bit, sizeof(bit), FS_DELAY);
  PMD_GetInputReport(fd, DBIT_IN, &value, sizeof(value), FS_DELAY);

  return value;
}

/* writes digital port bit */
void usbDBitOut_USB4303(int fd, __u8 bit, __u8 value)
{
  __u8 cmd[2];
  
  cmd[0] = bit;
  cmd[1] = value;

  PMD_SendOutputReport(fd, DBIT_OUT, cmd, sizeof(cmd), FS_DELAY);
}

void usbLoad_USB4303(int fd, __u8 chip, __u8 counters)
{
  /*
     This command loads the selected counters with current load or hold register value.  If counter is
     armed, the source register will be the one to be used for the upcoming terminal count value.  If
     the counter is disarmed, the counter will be loaded from the load register, unless in mode S or V,
     in which case, the counter gate input will select the source register.
  */

  struct t_load {
    __u8 chip;      // 1 = chip 1,  2 = chip 2
    __u8 counters;  
  } load;

  load.chip = chip;
  load.counters = counters;
  PMD_SendOutputReport(fd, LOAD, (__u8 *) &load, sizeof(load), FS_DELAY);
}

void usbSave_USB4303(int fd, __u8 chip, __u8 counters)
{
  /*
    This command saves the current counter value(s) to the associated hold register(s).  Any
    previous hold register contents will be overwritten.  This could cause problems if the hold
    register is being used for loading the counter (modes G-L, S and V).
  */

  struct t_save {
    __u8 chip;      // 1 = chip 1,  2 = chip 2
    __u8 counters;  
  } save;

  save.chip = chip;
  save.counters = counters;
  PMD_SendOutputReport(fd, SAVE, (__u8 *) &save, sizeof(save), FS_DELAY);
}

void usbArm_USB4303(int fd, __u8 chip, __u8 counters)
{
  /*
    This function arms the selected counters and begins counting.  If the counter is using
    mode G-L (alternate loading from load then hold register), arming the counter resets the
    load/hold logic; the counter will be loaded from the hold register on the next TC, and then
    alternate thereafter.
  */

  struct t_arm {
    __u8 chip;      // 1 = chip 1,  2 = chip 2
    __u8 counters;  
  } arm;

  arm.chip = chip;
  arm.counters = counters;
  PMD_SendOutputReport(fd, ARM, (__u8 *) &arm, sizeof(arm), FS_DELAY);
}

void usbDisarm_USB4303(int fd, __u8 chip, __u8 counters)
{
  /*
    This function disarms the selected counter(s) and stops counting.
  */

  struct t_disarm {
    __u8 chip;      // 1 = chip 1,  2 = chip 2
    __u8 counters;  
  } disarm;

  disarm.chip = chip;
  disarm.counters = counters;
  PMD_SendOutputReport(fd, DISARM, (__u8 *) &disarm, sizeof(disarm), FS_DELAY);
}

__u16 usbRead_USB4303(int fd, __u8 chip, __u8 counter)
{
  /*
    This function reads the current value of the 16-bit counter. To accomplish this, the counter
    value is latched out to the HOLD register and the HOLD register value is returned.  If the
    counter is in a mode that uses the HOLD register to load the counter (modes G-L, S and V), 
    this function returns 0.
  */

  struct t_read {
    __u8 chip;      // 1 = chip 1,  2 = chip 2
    __u8 counter;   // Only use bits [0:2].  
  } read;

  __u16 value;

  read.chip = chip;
  switch (counter) {
    case COUNTER_1:  read.counter = 0x1; break;
    case COUNTER_2:  read.counter = 0x2; break;
    case COUNTER_3:  read.counter = 0x3; break;
    case COUNTER_4:  read.counter = 0x4; break;
    case COUNTER_5:  read.counter = 0x5; break;
    default: return 0; break;
  }

  PMD_SendOutputReport(fd, READ, (__u8 *) &read, sizeof(read), FS_DELAY);
  PMD_GetInputReport(fd, READ, (__u8 *) &value, sizeof(value), FS_DELAY);
  return value;
}

void usbSetToggle_USB4303(int fd, __u8 chip, __u8 counter, __u8 set)
{
  /*
    This function sets or clears the selected counter output if the counter output is set
    to toggle on terminal count. There is no effect for other ouptut modes.
  */
  struct t_setToggle {
    __u8 chip;      // 1 = chip 1,  2 = chip 2
    __u8 counter;   // Only use bits [0:2]. 
    __u8 set;       // 0 = clear ouptut, 1 = set output
  } setToggle;

  setToggle.chip = chip;
  switch (counter) {
    case COUNTER_1:  setToggle.counter = 0x1; break;
    case COUNTER_2:  setToggle.counter = 0x2; break;
    case COUNTER_3:  setToggle.counter = 0x3; break;
    case COUNTER_4:  setToggle.counter = 0x4; break;
    case COUNTER_5:  setToggle.counter = 0x5; break;
    default: return ; break;
  }

  PMD_SendOutputReport(fd, SET_TOGGLE, (__u8 *) &setToggle, sizeof(setToggle), FS_DELAY);
}

void usbStep_USB4303(int fd, __u8 chip, __u8 counter)
{
  /*
    This function steps the selected counter value up or down.  It will increment if the counter is
    configured to count up and decrement if the counter is configured to count down
  */

  struct t_step {
    __u8 chip;      // 1 = chip 1,  2 = chip 2
    __u8 counter;   // Only use bits [0:2]. 
  } step;

  step.chip = chip;
  switch (counter) {
    case COUNTER_1:  step.counter = 0x1; break;
    case COUNTER_2:  step.counter = 0x2; break;
    case COUNTER_3:  step.counter = 0x3; break;
    case COUNTER_4:  step.counter = 0x4; break;
    case COUNTER_5:  step.counter = 0x5; break;
    default: return ; break;
  }

  PMD_SendOutputReport(fd, STEP, (__u8 *) &step, sizeof(step), FS_DELAY);
}

void usbSet9513Config_USB4303(int fd, __u8 chip, __u16 settings)
{
  /*
    The command sets the configuration options for the 9513 chip through the Master Mode
    Register.  The default for the "settings" parameter upon initialization of the device
    is 0x8000.  Refer to the 9513A datasheet for details.
  */
  struct t_set9513Config {
    __u8 chip;          // 1 = chip 1,  2 = chip 2
    __u8 settings[2];   
  } set9513Config;

  set9513Config.chip = chip;
  set9513Config.settings[0] = (__u8) (settings & 0xff);          // low byte
  set9513Config.settings[1] = (__u8) (settings >> 0x8) & 0xff;   // hight byte

  PMD_SendOutputReport(fd, SET9513CONFIG, (__u8 *) &set9513Config, sizeof(set9513Config), FS_DELAY);
}

__u16 usbGet9513Config_USB4303(int fd, __u8 chip)
{
  /*
    The command returns the 9513 configuration settings.
  */
  __u16 value;

  PMD_SendOutputReport(fd, GET9513CONFIG, (__u8 *) &chip, sizeof(chip), FS_DELAY);
  PMD_GetInputReport(fd, GET9513CONFIG, (__u8 *) &value, sizeof(value), FS_DELAY);
  return value;
}

void usbSetOscOut_USB4303(int fd, __u8 chip, __u8 enable)
{
  /*
    This command enables or disables the oscillator output.
  */

  struct t_setOscOut {
    __u8 chip;    // 1 = chip 1 ,  2 = chip 2
    __u8 enable;  // 0 = disable,  1 = enable
  } setOscOut;

  setOscOut.chip = chip;
  setOscOut.enable = enable;
  PMD_SendOutputReport(fd, SETOSCOUT, (__u8 *) &setOscOut, sizeof(setOscOut), FS_DELAY);
}

void usbSetRegister_USB4303(int fd, __u8 chip, __u8 reg, __u16 value)
{
  /*
    This command sets the value of the selected 9513 register.
  */

  struct t_setReg {
    __u8 chip;
    __u8 reg;
    __u16 value;
  } setReg;

  setReg.chip = chip;
  setReg.reg = reg;
  setReg.value = value;

  PMD_SendOutputReport(fd, SETREGISTER, (__u8 *) &setReg, sizeof(setReg), FS_DELAY);
}

__u16 usbGetRegister_USB4303(int fd, __u8 chip, __u8 reg)
{
  /*
    This command returns the value of the selected 9513 register
  */

  struct t_getReg {
    __u8 chip;
    __u8 reg;
  } getReg;

  __u16 value;

  getReg.chip = chip;
  getReg.reg = reg;

  PMD_SendOutputReport(fd, GETREGISTER, (__u8 *) &getReg, sizeof(getReg), FS_DELAY);
  PMD_GetInputReport(fd, GETREGISTER, (__u8 *) &value, sizeof(value), FS_DELAY);
  return value;
}

void usbReset9513_USB4303(int fd, __u8 chip)
{
  /* This command resets the 9513 chip to default values and initializes the counter registers to 
     all zeros.
  */
  PMD_SendOutputReport(fd, RESET, (__u8 *) &chip, sizeof(chip), FS_DELAY);
}

void usbSelect9513Clock_USB4303(int fd, __u8 clock)
{
  /*
    This command selects the initial clock frequency for the 9513 coungter.  On the USB-4303,
    this clock frequency is input to both chips, they cannot be selected individually.

   Values of clock are:
       0x00  =  1 MHz
       0x01  =  1.66667 MHz
       0x02  =  3.33333 MHz
       0x03  =  5 MHz (default)
       all other values = no change
  */
  PMD_SendOutputReport(fd, SELECT9513CLOCK, (__u8 *) &clock, sizeof(clock), FS_DELAY);
}

__u16 usbReadFreq_USB4303(int fd, __u8 chip, __u8 source, __u16 interval_counts)
{
  /*
    This command configures counters 4 and 5 on the selected chip to measure frequency.  This
    requires connecting the output pin of counter 4 to the gate of counter 5.  The gating 
    interval depends on the internal clock selected (with Select9513Clock).

    (gating interval in ms) = interval_counts / (internal clock frequency in MHz)

    The response is the total number of rising edges received on the input specificied by source
    during the gating interval.  To calculate the frequency from this use the following:

    (frequency in Hz) = [(received pulses) / (gating interval in ms)] * 1000

    If an overrun occurs (more than 65,535 rising edges are received during the gatin interval), the
    response will be 0xff.
  */

  struct t_readFreq {
    __u8 chip;
    __u8 source;
    __u16 interval_counts;
  } readFreq;

  __u16 value;

  readFreq.chip = chip;
  readFreq.source = source;
  readFreq.interval_counts = interval_counts;

  PMD_SendOutputReport(fd, READFREQ, (__u8 *) &readFreq, sizeof(readFreq), FS_DELAY);
  PMD_GetInputReport(fd, READFREQ, (__u8 *) &value, sizeof(value), FS_DELAY);
  return value;
}

void usbReadMemory_USB4303(int fd, __u16 address, __u8 count, __u8* memory)
{
  /*
    The command reads data from the EEPROM configuration memory.  There are 256 bytes
    available in the EEPROM (address 0x00 to 0xff).
  */

  struct t_arg {
    __u16 address;  // the start address for the read
    __u8 type;      // not used
    __u8 count;     // the number of bytes to read (62 max)
  } arg;

  if ( count > 62 ) count = 62;
  arg.type = 0;      // unused for this device.
  arg.address = address;
  arg.count = count;

  PMD_SendOutputReport(fd, MEM_READ, (__u8 *) &arg, sizeof(arg), FS_DELAY);
  PMD_GetInputReport(fd, MEM_READ, memory, count, FS_DELAY);
}

int usbWriteMemory_USB4303(int fd, __u16 address, __u8 count, __u8* data)
{
  /*
    The command writes to the EEPROM on the device micrprocessor.  This non-volatile memory
    is used to store system information and user data.  

    The EEPROM may be written at any address with 1-60 bytes of data in a write.
  */
  
  int i;
  struct t_arg {
    __u16 address;     // the start address for the write
    __u8 count;        // the number of bytes to write (60 max)
    __u8 data[count];  // the data to be written (60 bytes max)
  } arg;

  if ( count > 60 ) count = 60;
  
  arg.address = address;
  arg.count = count;
  for ( i = 0; i < count; i++ ) {
    arg.data[i] = data[i];
  }
  PMD_SendOutputReport(fd, MEM_WRITE, (__u8 *) &arg, count+3, FS_DELAY);
  return 0;
}

/* blinks the LED of USB device */
int usbBlink_USB4303(int fd, __u8 count)
{
  /* 
    This command causes the LED to blink "count" times.
  */
  return PMD_SendOutputReport(fd, BLINK_LED, (__u8 *) &count, sizeof(count), FS_DELAY);
}

int usbReset_USB4303(int fd)
{
  /*
    This function causes the device to perform a reset.  The device disconnects from the USB bus
    and resets the microcontroller.
  */
  return PMD_SendOutputReport(fd, RESET, 0, 0, FS_DELAY);
}

__u32 usbGetStatus_USB4303(int fd)
{
  /*
    This command retrives the status of the device.
  */
  __u32 value;

  PMD_SendOutputReport(fd, GET_STATUS, 0, 0, FS_DELAY);
  PMD_GetInputReport(fd, GET_STATUS, (__u8 *) &value, sizeof(value), FS_DELAY);
  return value;
}

void usbInterruptConfig_USB4303(int fd, __u16 config, __u16 data[10])
{
  /*
    This command configures the external interrupt pin.  It can generate an event notification
    to the PC, latch the digital inputs, latch the digital outputs, and/or generate a SAVE command
    for and/all counters on either/both 9513s.  All interrupt settings initializes to off, with 
    rising edge triggering.

    The response for this command is sent to the PC whenever the interrupt edge is received if
    event notification is on.  If digital input latch in on, DIn and DBitIn will return the data 
    that was latched in the most recent interrupt edge.  If digital output latch is on, when the 
    interrupt edge is received, the most recently received data via DOut or DBitOut will be latched out.

    Note that setting digital input latch to on will immediately latch in the current input value, and
    setting digital output latch to on will initialize th edata to be latched out to 0.  Also note that the
    SAVE command overwrites the HOLD register contents and thus can cause unpredictable results on 
    counters that are using modes G-L, S or V.
  */
  PMD_SendOutputReport(fd, INTERRUPT_CONFIG, (__u8 *) &config, sizeof(config), FS_DELAY);
  PMD_GetInputReport(fd, INTERRUPT_CONFIG, (__u8 *) &data, sizeof(data), FS_DELAY);
}

void usbPrepareDownload_USB4303(int fd)
{
  /*
    This command puts the device into code update mode.  The unlock code must be correct as a
    further safety device.  Call this once before sending code with WriteCode.  If not in code
    update mode, any WriteCode commands will be ignored.
  */

  const __u8 unlock_code = 0xad;

  __u8 cmd = unlock_code;

  PMD_SendOutputReport(fd, PREPARE_DOWNLOAD, &cmd, sizeof(cmd), FS_DELAY);
}

void usbWriteCode_USB4303(int fd, __u32 address, __u8 count, __u8 data[])
{
  /*
    This command writes to the program memory in the device.  This command is not accepted
    unless the device is in update mode.  This command will normally be used when downloading
    a new hex file, so it supports memory ranges that may be found in the hex file.  

    The address ranges are:

    0x000000 - 0x007AFF:  Microcontroller FLASH program memory
    0x200000 - 0x200007:  ID memory (serial number is stored here on main micro)
    0x300000 - 0x30000F:  CONFIG memory (processor configuration data)
    0xF00000 - 0xF03FFF:  EEPROM memory

    FLASH program memory: The device must receive data in 64-byte segments that begin
    on a 64-byte boundary.  The data is sent in messages containing 32 bytes.  count
    must always equal 32.

    Other memory: Any number of bytes up to the maximum (32) may be sent.
    
  */

  struct t_arg {
    __u8 address[3];
    __u8 count;
    __u8 data[32];
  } arg;

  if (count > 32) count = 32;             // 32 byte max 
  memcpy(&arg.address[0], &address, 3);   // 24 bit address
  arg.count = count;                      // the number of byes of data (max 32)
  memcpy(&arg.data[0], data, count);      // the program data
  PMD_SendOutputReport(fd, WRITE_CODE, (__u8 *) &arg, count+4, FS_DELAY);
}

void usbWriteSerial_USB4303(int fd, __u8 serial[8])
{
  /*
    This command sends a new serial number to the device.  The serial number consists of 8 bytes,
    typically ASCII numeric or hexadecimal digits (i.e. "00000001").  The new serial number will
    be programmed but not used until hardware reset.
  */

  PMD_SendOutputReport(fd, WRITE_SERIAL, serial, 8, FS_DELAY);
}

int usbReadCode_USB4303(int fd, __u32 address, __u8 count, __u8 data[])
{
  /*
    This command reads from the program memory.
 
    The address ranges are:

    0x000000 - 0x007AFF:  Microcontroller FLASH program memory
    0x200000 - 0x200007:  ID memory (serial number is stored here on main micro)
    0x300000 - 0x30000F:  CONFIG memory (processor configuration data)

    Note: The EEPROM memory can only be read using the MemRead command.
  */

  struct t_arg {
    __u8 address[3];    // 24 bit start address for the read
    __u8 count;         // the number of bytes to read (62 byte max)
  } arg;

  int bRead;

  if ( count > 62 ) count = 62;  

  memcpy(&arg.address[0], &address, 3);   // 24 bit address
  arg.count = count;
  PMD_SendOutputReport(fd, READ_CODE, (__u8 *) &arg, sizeof(arg), FS_DELAY);
  bRead = PMD_GetInputReport(fd, READ_CODE, data, count, FS_DELAY);
  return bRead;
}

void usbWrite9513Command_USB4303(int fd, __u8 chip, __u8 command)
{
  /*
    This command writes the specified command directly to the selected 9513 chip's command port.
  
    Note: Direct port access API commands should be used with caution; there are no safeguards to
    prevent configuration of the 9513 in such a way as to make it unusable.  (For instance, changing
    the data bus mode from 8-bit to 16-bit).  If this occurs, a device power-reset will always return
    the device to a working condition.
  */

  __u8 cmd[2];

  cmd[0] = chip;      // 1 = chip 1,  2 = chip 2
  cmd[1] = command;   // the byte to write to the 9513 command port.
  PMD_SendOutputReport(fd, WRITE_COMMAND, cmd, sizeof(cmd), FS_DELAY);
}

__u8 usbRead9513Command_USB4303(int fd, __u8 chip)
{
  /* 
     This command reads the selected 9513 chip's command port, which returns the current value of the 9513
     status register.
  */

  __u8 value;

  PMD_SendOutputReport(fd, READ_COMMAND, (__u8 *) &chip, sizeof(chip), FS_DELAY);
  PMD_GetInputReport(fd, READ_COMMAND, (__u8 *) &value, sizeof(value), FS_DELAY);
  return value;
}

void usbWrite9513Data_USB4303(int fd, __u8 chip, __u8 data)
{
  /*
    This command writes directly to the selected 9513 chip's data port.  A write to one of the data
    registers will typically involve first issuing a command to the command port to set the value of 
    the data pointer register, followed by two 8-bit writes to the data port to set the value of the
    desired 16-bit data register, LSB first.
  */

  __u8 cmd[2];

  cmd[0] = chip;     // 1 = chip 1,  2 = chip 2
  cmd[1] = data;     // the 8-bit value to write to the data port
  PMD_SendOutputReport(fd, WRITE_DATA, cmd, sizeof(cmd), FS_DELAY);
}

__u8 usbRead9513Data_USB4303(int fd, __u8 chip)
{
  /*
    This command reads directly to the selected 9513 chip's data port.  A read to one of the data
    registers will typically involve first issuing a command to the command port to set the value of 
    the data pointer register, followed by two 8-bit reads to the data port to retrieve the value of the
    desired 16-bit data register, LSB first.
  */

  __u8 value;

  PMD_SendOutputReport(fd, READ_DATA, (__u8 *) &chip, sizeof(chip), FS_DELAY);
  PMD_GetInputReport(fd, READ_DATA, (__u8 *) &value, sizeof(value), FS_DELAY);
  return value;
}
