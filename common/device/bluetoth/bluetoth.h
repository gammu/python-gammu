
#ifndef DJGPP
#ifndef unixbluetooth_h
#define unixbluetooth_h

#ifdef WIN32
#  include "blue_w32.h"
#endif

typedef struct {
    int hPhone;
} GSM_Device_BlueToothData;

#endif
#endif

/* How should editor hadle tabs in this file? Add editor commands here.
 * vim: noexpandtab sw=8 ts=8 sts=8:
 */