
#ifndef PHONET_h
#define PHONET_h

#include "../protocol.h"

#define PHONET_FRAME_ID      	0x14
#define PHONET_BLUE_FRAME_ID	0x19
#define PHONET_DEVICE_PHONE   	0x00 /* Nokia mobile phone */
#define PHONET_DEVICE_PC      	0x0c /* Our PC */
#define PHONET_BLUE_DEVICE_PC   0x10 /* Our PC */

typedef struct {
	int			MsgRXState;
	GSM_Protocol_Message	Msg;
} GSM_Protocol_PHONETData;

#if defined(GSM_ENABLE_IRDAPHONET)
#  ifndef GSM_USED_IRDADEVICE
#    define GSM_USED_IRDADEVICE
#  endif
#endif
#if defined(GSM_ENABLE_BLUEPHONET)
#  ifndef GSM_USED_BLUETOOTHDEVICE
#    define GSM_USED_BLUETOOTHDEVICE
#  endif
#endif

#endif

/* How should editor hadle tabs in this file? Add editor commands here.
 * vim: noexpandtab sw=8 ts=8 sts=8:
 */