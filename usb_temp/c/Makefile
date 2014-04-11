#############################################################################
#	
#	Makefile for building:
#
#		libmccusb.so:      Library for MCC USB series
#		test-usb1208LS:    Program to test -1208LS module
#		test-usb1024LS:    Program to test USB-1024LS module
#		test-usb1208FS:    Program to test USB-1208FS module
#		test-usb1408FS:    Program to test USB-1408FS module
#		test-usb1608FS:    Program to test USB-1608FS module
#		test-usb1096HFS:   Program to test USB-1096HFS module
#		test-usb1016FS:    Program to test USB-1616FS module
#               test-usb3100:      Program to test USB-3100 modules
#		test-usb-tc:       Program to test USB-TC module
#		test-usb-tc-ai:    Program to test USB-TC-AI module
#		test-usb-temp-ai:  Program to test USB-TEMP-AI module
#		test-usb-temp:     Program to test USB-TEMP module
#		test-minilab1008:  Program to test minilab 1008
#               test-usb5201:      Program to test USB-5201 module
#               test-usb5203:      Program to test USB-5203 module
#               test-usb-ssr       Program to test USB-SSR24 and USB_SSR08
#               test-usb-pdiso8    Program to test USB-PDISO8
#               test-usb-erb       Program to test USB-ERB08 and USB-ERB24
#               test-usb4300       Program to test USB-430X
#               test-usb-dio24     Program to test USB-DIO24 and USB-DIO24H
#
#               Copyright (C) December 18, 2007
#               Written by:  Warren J. Jasper
#                            North Carolina State Univerisity
#
#
# This program, libmccusb.so, is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version, provided that this
# copyright notice is preserved on all copies.
#
# ANY RIGHTS GRANTED HEREUNDER ARE GRANTED WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE, AND FURTHER,
# THERE SHALL BE NO WARRANTY AS TO CONFORMITY WITH ANY USER MANUALS OR
# OTHER LITERATURE PROVIDED WITH SOFTWARE OR THAM MY BE ISSUED FROM TIME
# TO TIME. IT IS PROVIDED SOLELY "AS IS".
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
###########################################################################

#  Current Version of the driver
VERSION=1.36

SRCS    = pmd.c usb-1208LS.c usb-1024LS.c usb-1208FS.c usb-1408FS.c usb-1608FS.c usb-tc.c usb-tc-ai.c usb-temp.c usb-1096HFS.c usb-1616FS.c minilab-1008.c usb-52XX.c usb-ssr.c usb-3100.c usb-pdiso8.c usb-erb.c usb-4303.c usb-dio24.c
HEADERS = pmd.h usb-1208LS.h usb-1024LS.h usb-1208FS.h usb-1408FS.h usb-1608FS.h usb-tc.h usb-tc-ai.h usb-temp.h usb-1096HFS.h usb-1616FS.h minilab-1008.h usb-52XX.h usb-ssr.h usb-3100.h usb-pdiso8.h usb-erb.h usb-4303.h usb-dio24.h
OBJS = $(SRCS:.c=.o)   # same list as SRCS with extension changed
CC=gcc
CFLAGS= -g -Wall -fPIC
TARGETS=libmccusb.so libmccusb.a test-usb1208LS test-usb1024LS test-usb1208FS test-usb1408FS test-usb1608FS test-usb-tc test-usb-tc-ai test-usb-temp-ai test-usb-temp test-usb1096HFS test-usb1616FS test-minilab1008 test-usb5201 test-usb5203 test-usb-ssr test-usb3100 test-usb-pdiso8 test-usb-erb test-usb4300 test-usb-dio24
ID=MCCUSBHID
DIST_NAME=$(ID).$(VERSION).tgz
DIST_FILES={README,License,Makefile,usb-1208LS.h,usb-1208LS.c,usb-1024LS.h,usb-1024LS.c,usb-1208FS.h,usb-1208FS.c,usb-1408FS.c,usb-1408FS.h,usb-1608FS.h,usb-1608FS.c,usb-tc.h,usb-tc.c,usb-tc-ai.c,usb-tc-ai.h,usb-temp.h,usb-temp.c,usb-1096HFS.h,usb-1096HFS.c,usb-1616FS.h,usb-1616FS.c,usb-3100.h,usb-3100.c,usb-ssr.h,usb-ssr.c,usb-pdiso8.h,usb-pdiso8.c,usb-erb.h,usb-erb.c,usb-4303.h,usb-4303.c,pmd.h,pmd.c,minilab-1008.h,minilab-1008.c,usb-52XX.h,usb-52XX.c,usb-dio24.h,usb-dio24.c,test-usb1208LS.c,test-usb1024LS.c,test-usb1208FS.c,test-usb1408FS.c,test-usb1608FS.c,test-usb-tc.c,test-usb-tc-ai.c,test-usb-temp-ai.c,test-usb-temp.c,test-usb1096HFS.c,test-usb1616FS.c,test-minilab1008.c,test-usb5201.c,test-usb5203.c,test-usb-ssr.c,test-usb3100.c,test-usb-pdiso8.c,test-usb-erb.c,test-usb4300.c,test-usb-dio24.c}

###### RULES
all: $(TARGETS)

%.d: %.c
	set -e; $(CC) -I. -M $(CPPFLAGS) $< \
	| sed 's/\($*\)\.o[ :]*/\1.o $@ : /g' > $@; \
	[ -s $@ ] || rm -f $@
ifneq ($(MAKECMDGOALS),clean)
include $(SRCS:.c=.d)
endif

libmccusb.so: $(OBJS)
	$(CC) -shared -Wall $(OBJS) -o $@

libmccusb.a: $(OBJS)
	ar -r libmccusb.a $(OBJS)
	ranlib libmccusb.a

test-usb1208LS:	test-usb1208LS.c libmccusb.a
	$(CC) -static -g -Wall -I. -o $@  $@.c -lmccusb -L. -lm

test-usb1024LS:	test-usb1024LS.c libmccusb.a
	$(CC) -static -g -Wall -I. -o $@  $@.c -lmccusb -L. -lm

test-usb1208FS:	test-usb1208FS.c libmccusb.a
	$(CC) -static -g -Wall -I. -o $@  $@.c -lmccusb -L. -lm

test-usb1408FS:	test-usb1408FS.c libmccusb.a
	$(CC) -static -g -Wall -I. -o $@  $@.c -lmccusb -L. -lm

test-usb1608FS:	test-usb1608FS.c libmccusb.a
	$(CC) -static -g -Wall -I. -o $@  $@.c -lmccusb -L. -lm

test-usb3100:	test-usb3100.c libmccusb.a
	$(CC) -static -g -Wall -I. -o $@  $@.c -lmccusb -L. -lm

test-usb-tc:	test-usb-tc.c libmccusb.a
	$(CC) -static -g -Wall -I. -o $@  $@.c -lmccusb -L. -lm

test-usb-tc-ai:	test-usb-tc-ai.c libmccusb.a
	$(CC) -static -g -Wall -I. -o $@  $@.c -lmccusb -L. -lm

test-usb-temp-ai: test-usb-temp-ai.c libmccusb.a
	$(CC) -static -g -Wall -I. -o $@  $@.c -lmccusb -L. -lm

test-usb-temp:	test-usb-temp.c libmccusb.a
	$(CC) -static -g -Wall -I. -o $@  $@.c -lmccusb -L. -lm

test-usb1096HFS: test-usb1096HFS.c libmccusb.a
	$(CC) -static -g -Wall -I. -o $@  $@.c -lmccusb -L. -lm

test-usb1616FS: test-usb1616FS.c libmccusb.a
	$(CC) -static -g -Wall -I. -o $@  $@.c -lmccusb -L. -lm

test-minilab1008: test-minilab1008.c libmccusb.a
	$(CC) -static -g -Wall -I. -o $@  $@.c -lmccusb -L. -lm

test-usb5201: test-usb5201.c libmccusb.a
	$(CC) -static -g -Wall -I. -o $@  $@.c -lmccusb -L. -lm

test-usb5203: test-usb5203.c libmccusb.a
	$(CC) -static -g -Wall -I. -o $@  $@.c -lmccusb -L. -lm

test-usb-ssr: test-usb-ssr.c libmccusb.a
	$(CC) -static -g -Wall -I. -o $@  $@.c -lmccusb -L. -lm

test-usb-pdiso8: test-usb-pdiso8.c libmccusb.a
	$(CC) -static -g -Wall -I. -o $@  $@.c -lmccusb -L. -lm

test-usb-erb: test-usb-erb.c libmccusb.a
	$(CC) -static -g -Wall -I. -o $@  $@.c -lmccusb -L. -lm

test-usb4300: test-usb4300.c libmccusb.a
	$(CC) -static -g -Wall -I. -o $@  $@.c -lmccusb -L. -lm

test-usb-dio24: test-usb-dio24.c libmccusb.a
	$(CC) -static -g -Wall -I. -o $@  $@.c -lmccusb -L. -lm

clean:
	rm -rf *.d *.o *~ *.a *.so $(TARGETS) \#*

dist:	
	make clean
	cd ..; tar -zcvf $(DIST_NAME) usbhid/$(DIST_FILES);

install:
	-install -d /usr/local/lib
	-install -c --mode=0755 ./libmccusb.a libmccusb.so /usr/local/lib
	-/bin/ln -s /usr/local/lib/libmccusb.so /usr/lib/libmccusb.so
	-/bin/ln -s /usr/local/lib/libmccusb.a /usr/lib/libmccusb.a
	-install -d /usr/local/include/usbhid
	-install -c --mode=0644 ${HEADERS} /usr/local/include/usbhid/

uninstall:
	-rm -f /usr/local/lib/libmccusb*
	-rm -f /usr/lib/libmccusb*
	-rm -rf /usr/local/include/usbhid
