                                           
#include "../../gsmstate.h"

#ifdef GSM_ENABLE_ATGEN

#include <string.h>
#include <time.h>
#include <ctype.h>

#include "../../gsmcomon.h"
#include "../../misc/coding.h"
#include "../../service/gsmsms.h"
#include "../pfunc.h"

extern GSM_Error ATGEN_HandleCMSError(GSM_StateMachine *s);

GSM_Error ATGEN_CMS35ReplySetFunction (GSM_Protocol_Message msg, GSM_StateMachine *s,char *function)
{
	if (s->Protocol.Data.AT.EditMode)
	{
	    s->Protocol.Data.AT.EditMode = false;
	    return GE_NONE;
	}
	dprintf ("Written %s",function);
  	if (s->Phone.Data.Priv.ATGEN.ReplyState == AT_Reply_OK){
  		dprintf (" - OK\n");
  		return GE_NONE;
	} else {
  		dprintf (" - error\n");
  		return GE_UNKNOWN;
	}
}

GSM_Error GetSiemensFrame(GSM_Protocol_Message msg, GSM_StateMachine *s, char *templ,
			    unsigned char *buffer, int *len)
{
	GSM_Phone_ATGENData 	*Priv = &s->Phone.Data.Priv.ATGEN;
	int			i=2, pos=0, length=0;
	unsigned char 		buf[512];

	if (strstr(GetLineString(msg.Buffer,Priv->Lines,2),"OK")) return GE_EMPTY;
        if (!strstr(GetLineString(msg.Buffer,Priv->Lines,2),templ)) return GE_UNKNOWN;

	while (1) {
		if (Priv->Lines.numbers[i*2+1]==0) break;
		if ((!strstr(GetLineString(msg.Buffer,Priv->Lines,i+1),templ)) && 
	            (strstr(GetLineString(msg.Buffer,Priv->Lines,i),templ))){
			length = strlen(GetLineString(msg.Buffer,Priv->Lines,i+1));
			DecodeHexBin(buf, GetLineString(msg.Buffer,Priv->Lines,i+1),length);
			length = length/2;
			memcpy (buffer+pos,buf,length);
			pos+=length;
		} 
		i++;
	}
	*len = pos;
       return GE_NONE;	
}

GSM_Error SetSiemensFrame (GSM_StateMachine *s, unsigned char *buff, char *templ,
			    int Location, GSM_Phone_RequestID RequestID, int len)
{
	GSM_Phone_Data		*Phone = &s->Phone.Data;
	GSM_Error		error;
	unsigned char 		req[20],req1[512],hexreq[2096];
	int			MaxFrame,CurrentFrame,size,sz,pos=0;

	EncodeHexBin(hexreq,buff,len);
	size	 = len * 2;
	MaxFrame = size / 352;
	if (size % 352) MaxFrame++;

	for (CurrentFrame=0;CurrentFrame<MaxFrame;CurrentFrame++)
	{
		pos=CurrentFrame*352;
	 	if (pos+352 < size) sz = 352; else sz = size - pos;
		sprintf(req, "AT^SBNW=\"%s\",%i,%i,%i\r",templ,Location,CurrentFrame+1,MaxFrame);
		s->Protocol.Data.AT.EditMode = true;
		error = GSM_WaitFor (s, req, strlen(req), 0x00, 3, RequestID);
		s->Phone.Data.DispatchError=GE_TIMEOUT;
		s->Phone.Data.RequestID=RequestID;
	     	if (error!=GE_NONE) return error;
	 	memcpy (req1,hexreq+pos,sz);
	 	error = s->Protocol.Functions->WriteMessage(s, req1, sz, 0x00);
	 	if (error!=GE_NONE) return error;
		error = s->Protocol.Functions->WriteMessage(s,"\x1A", 1, 0x00);
	 	if (error!=GE_NONE) return error;
		error = GSM_WaitForOnce(s, NULL, 0x00, 0x00, 4);
	 	if (error == GE_TIMEOUT) return error;
	 }
	 return Phone->DispatchError;
}

GSM_Error ATGEN_CMS35ReplyGetBitmap(GSM_Protocol_Message msg, GSM_StateMachine *s)
{
	unsigned char 		buffer[4096];
	int			length;
	GSM_Error		error;
	
	error = GetSiemensFrame(msg,s,"bmp",buffer,&length);
	if (error!=GE_NONE) return error;
	dprintf ("Operator logo received lenght=%i\n",length);
	error = BMP2Bitmap (buffer,NULL,s->Phone.Data.Bitmap);
	if (error==GE_NONE) return error;
	else return GE_UNKNOWN;
}

GSM_Error ATGEN_CMS35ReplySetBitmap(GSM_Protocol_Message msg, GSM_StateMachine *s)
{
    return ATGEN_CMS35ReplySetFunction (msg, s, "Operator Logo");
}

GSM_Error ATGEN_GetBitmap(GSM_StateMachine *s, GSM_Bitmap *Bitmap)
{
	unsigned char req[32];

	if (s->Phone.Data.Priv.ATGEN.Manufacturer!=AT_Siemens) return GE_NOTSUPPORTED;
	if (Bitmap->Type!=GSM_OperatorLogo) return GE_NOTSUPPORTED;
	if (Bitmap->Location-1 < 0) Bitmap->Location++;
	s->Phone.Data.Bitmap=Bitmap;
	sprintf(req, "AT^SBNR=\"bmp\",%i\r", Bitmap->Location-1);
	smprintf(s, "Getting Bitmap\n");
	return GSM_WaitFor (s, req, strlen(req), 0x00, 4, ID_GetBitmap);
}

GSM_Error ATGEN_SetBitmap(GSM_StateMachine *s, GSM_Bitmap *Bitmap)
{
	unsigned char 	buffer[4096];
	int 		length;
	GSM_Error		error;
	
	if (s->Phone.Data.Priv.ATGEN.Manufacturer!=AT_Siemens) return GE_NOTSUPPORTED;
	if (Bitmap->Type!=GSM_OperatorLogo) return GE_NOTSUPPORTED;

	error = Bitmap2BMP (buffer,NULL,Bitmap);
	if (error!=GE_NONE) return error;
	length = 0x100 * buffer[3] + buffer[2];
	buffer[58]=0xff; buffer[59]=0xff; buffer[60]=0xff;
	if (Bitmap->Location-1 < 0) Bitmap->Location++;
	s->Phone.Data.Bitmap=Bitmap;
	return SetSiemensFrame(s, buffer,"bmp",Bitmap->Location-1,
				ID_SetBitmap,length);

}

GSM_Error ATGEN_CMS35ReplyGetRingtone(GSM_Protocol_Message msg, GSM_StateMachine *s)
{
	unsigned char 		buffer[32];
	int			length;
	GSM_Error		error;

        error = GetSiemensFrame(msg,s,"mid",s->Phone.Data.Ringtone->NokiaBinary.Frame,&length);
	if (error!=GE_NONE) return error;
	dprintf ("Midi ringtone received\n");
	
	s->Phone.Data.Ringtone->Format			= RING_MIDI;
	s->Phone.Data.Ringtone->NokiaBinary.Length	= length;
	sprintf(buffer,"Individual");
	EncodeUnicode (s->Phone.Data.Ringtone->Name,buffer,strlen(buffer));
	return GE_NONE;
}

GSM_Error ATGEN_GetRingtone(GSM_StateMachine *s, GSM_Ringtone *Ringtone, bool PhoneRingtone)
{
	unsigned char req[32];

	if (s->Phone.Data.Priv.ATGEN.Manufacturer!=AT_Siemens) return GE_NOTSUPPORTED;
	
	s->Phone.Data.Ringtone=Ringtone;
	sprintf(req, "AT^SBNR=\"mid\",%i\r", Ringtone->Location-1);
	smprintf(s, "Getting RingTone\n");
	return GSM_WaitFor (s, req, strlen(req), 0x00, 4, ID_GetRingtone);
}

GSM_Error ATGEN_CMS35ReplySetRingtone(GSM_Protocol_Message msg, GSM_StateMachine *s)
{
    return ATGEN_CMS35ReplySetFunction (msg, s, "Ringtone");
}
  
GSM_Error ATGEN_SetRingtone(GSM_StateMachine *s, GSM_Ringtone *Ringtone, int *maxlength)
{
	GSM_Phone_Data *Phone = &s->Phone.Data;
	 
	if (s->Phone.Data.Priv.ATGEN.Manufacturer!=AT_Siemens) return GE_NOTSUPPORTED;

	if (Ringtone->Location==255) Ringtone->Location=1; 
	if (Ringtone->Location-1 > 1) return GE_INVALIDLOCATION;

	s->Phone.Data.Ringtone	= Ringtone;
 	Phone->Ringtone		= Ringtone;
	return SetSiemensFrame(s, Ringtone->NokiaBinary.Frame,"mid",Ringtone->Location-1,
				ID_SetRingtone,Ringtone->NokiaBinary.Length);
}

GSM_Error ATGEN_CMS35ReplyGetNextCal(GSM_Protocol_Message msg, GSM_StateMachine *s)
{
	GSM_Phone_Data		*Data = &s->Phone.Data;
	GSM_CalendarEntry	*Calendar = Data->Cal;
	GSM_ToDoEntry		ToDo;
	GSM_Error		error;
	unsigned char 		buffer[354];
	int			len, pos=0;

	if (Data->Priv.ATGEN.ReplyState != AT_Reply_OK) return GE_UNKNOWN;

	error = GetSiemensFrame(msg,s,"vcs",buffer,&len);
	if (error!=GE_NONE) return error;
	error=GSM_DecodeVCALENDAR_VTODO(buffer,&pos,Calendar,&ToDo,Siemens_VCalendar,0);
	
 	return error;
}

GSM_Error ATGEN_GetNextCalendar(GSM_StateMachine *s, GSM_CalendarEntry *Note, bool start)
{
	GSM_Phone_ATGENData	*Priv = &s->Phone.Data.Priv.ATGEN;
	GSM_Error		error;
	unsigned char 		req[32];
	int			Location;

	if (Priv->Manufacturer!=AT_Siemens) return GE_NOTSUPPORTED;
	
	if (start) Note->Location=Priv->FirstCalendarPos;
	s->Phone.Data.Cal 	= Note;
	Note->EntriesNum 	= 0;
	smprintf(s, "Getting VCALENDAR\n");
	Location = Note->Location;
	while (1){
	    Location++;
	    sprintf(req, "AT^SBNR=\"vcs\",%i\r",Location);  
	    error = GSM_WaitFor (s, req, strlen(req), 0x00, 4, ID_GetCalendarNote);
	    if ((error!=GE_NONE) && (error!=GE_EMPTY)) return GE_INVALIDLOCATION;
	    Note->Location 		= Location;
	    Priv->FirstCalendarPos 	= Location;
	    if (Location > MAX_VCALENDAR_LOCATION) return GE_EMPTY;
	    if (error==GE_NONE) return error;
	}
	return error;
}

GSM_Error ATGEN_CMS35ReplySetCalendar(GSM_Protocol_Message msg, GSM_StateMachine *s)
{
    return ATGEN_CMS35ReplySetFunction (msg, s, "Calendar Note");
}

GSM_Error ATGEN_CMS35ReplyDeleteCalendar(GSM_Protocol_Message msg, GSM_StateMachine *s)
{
	GSM_Phone_Data *Data = &s->Phone.Data;
	
	if (Data->Cal->Location > MAX_VCALENDAR_LOCATION) return GE_UNKNOWN;
	
	if (Data->Priv.ATGEN.ReplyState== AT_Reply_OK) {
		smprintf(s, "Calendar note deleted\n");
		return GE_NONE;
	} else {
		smprintf(s, "Can't delete calendar note\n");
		return GE_UNKNOWN;
	}
}

GSM_Error ATGEN_DelCalendarNote(GSM_StateMachine *s, GSM_CalendarEntry *Note)
{
	unsigned char req[32];

	if (s->Phone.Data.Priv.ATGEN.Manufacturer!=AT_Siemens) return GE_NOTSUPPORTED;
	s->Phone.Data.Cal = Note;
	sprintf(req, "AT^SBNW=\"vcs\",%i,0\r",Note->Location);
	smprintf(s, "Deleting calendar note\n");
	return GSM_WaitFor (s, req, strlen(req), 0x00, 4, ID_DeleteCalendarNote);
}

GSM_Error ATGEN_AddCalendarNote(GSM_StateMachine *s, GSM_CalendarEntry *Note, bool Past)
{
	GSM_Phone_ATGENData	*Priv = &s->Phone.Data.Priv.ATGEN;
	GSM_Error		error;
	unsigned char 		req[500];
	int			size=0;

	if (Priv->Manufacturer!=AT_Siemens) return GE_NOTSUPPORTED;
	if (Note->Location==0x00) return GE_INVALIDLOCATION;	

	if (!Past && IsCalendarNoteFromThePast(Note)) return GE_NONE;

	s->Phone.Data.Cal = Note;
	error=GSM_EncodeVCALENDAR(req,&size,Note,true,Siemens_VCalendar);
		
	return SetSiemensFrame (s,req,"vcs",Note->Location,ID_SetCalendarNote,size);
}

GSM_Error ATGEN_SL45ReplyGetMemory(GSM_Protocol_Message msg, GSM_StateMachine *s)
{
 	GSM_Phone_ATGENData 	*Priv = &s->Phone.Data.Priv.ATGEN;
 	GSM_PhonebookEntry	*Memory = s->Phone.Data.Memory;
	unsigned char		buffer[500],buffer2[500];

	switch (Priv->ReplyState) {
	case AT_Reply_OK:
 		smprintf(s, "Phonebook entry received\n");
		CopyLineString(buffer, msg.Buffer, Priv->Lines, 3);
		DecodeHexBin(buffer2,buffer,strlen(buffer));
 		Memory->EntriesNum = 0;
		Memory->PreferUnicode = false;
                DecodeVCARD21Text(buffer2, Memory);
		return GE_NONE;
	case AT_Reply_Error:
                smprintf(s, "Error - too high location ?\n");
                return GE_INVALIDLOCATION;
	case AT_Reply_CMSError:
 	        return ATGEN_HandleCMSError(s);
	default:
		break;
	}
	return GE_UNKNOWNRESPONSE;
}

#endif

/* How should editor hadle tabs in this file? Add editor commands here.
 * vim: noexpandtab sw=8 ts=8 sts=8:
 */