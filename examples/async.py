import gammu
import gammu.async
import asyncio
import logging

import sys
import pprint
pp = pprint.PrettyPrinter(indent=4)

def sms_callback(messages):
    pp.pprint(messages)

async def send_sms(state_machine, number, message):
    smsinfo = {
        'Class': -1,
        'Unicode': False,
        'Entries':  [
            {
                'ID': 'ConcatenatedTextLong',
                'Buffer': message
            }
        ]}
    # Encode messages
    encoded = gammu.EncodeSMS(smsinfo)
    # Send messages
    for message in encoded:
        # Fill in numbers
        message['SMSC'] = {'Location': 1}
        message['Number'] = number
        # Actually send the message
        await state_machine.SendSMSAsync(message)

async def get_network_info(worker):
    info = await worker.GetNetworkInfoAsync()
    print('NetworkName:',info['NetworkName'])
    print('  State:',info['State'])
    print('  NetworkCode:',info['NetworkCode'])
    print('  CID:',info['CID'])
    print('  LAC:',info['LAC'])

async def get_info(state_machine):
    print('Phone infomation:')
    manufacturer = await state_machine.GetManufacturer()
    print(('{0:<15}: {1}'.format('Manufacturer', manufacturer)))
    model = await state_machine.GetModel()
    print(('{0:<15}: {1} ({2})'.format('Model', model[0], model[1])))
    imei = await state_machine.GetIMEI()
    print(('{0:<15}: {1}'.format('IMEI', imei)))
    firmware = await state_machine.GetFirmware()
    print(('{0:<15}: {1}'.format('Firmware', firmware[0])))

async def main():

    # Get the current event loop.
    loop = asyncio.get_running_loop()

    gammu.SetDebugFile(sys.stderr)
    gammu.SetDebugLevel('textall')

    #config = dict(Device="/dev/ttyS7", Connection="at")
    config = dict(Device="/dev/ttyS16", Connection="at")
    worker = sms_async.GammuAsyncWorker(loop)
    worker.configure(config)

    try:
        await worker.InitAsync()

        print("Create receiver")
        receiver = await sms_receiver.create_sms_receiver(worker, loop, sms_callback)
        print("Create receiver done")

        print(await worker.GetSignalQualityAsync())

        await send_sms(worker, '6700', 'BAL')

        # Just a busy waiting for event
        # We need to keep communication with phone to get notifications
        print('Press Ctrl+C to interrupt')
        while 1:
            try:
                signal = await worker.GetSignalQualityAsync()
                print('Signal is at {0:d}%'.format(signal['SignalPercent']))
            except Exception as e:
                print('Exception reading signal: {0}'.format(e))

            await asyncio.sleep(30)

    except Exception as e:
        print('Exception:')
        print(e)

    print("Terminate Start")
    await worker.TerminateAsync()
    print("Terminate Done")

if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(main())
    finally:
        event_loop.close()

