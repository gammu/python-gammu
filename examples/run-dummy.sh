#!/bin/sh
set -e
set -x
cd $(dirname $0)

TEST_DIR=$(mktemp -d)


CONFIG_DIR="$TEST_DIR/gammu"
CONFIG="$CONFIG_DIR/config"
DUMMY="$TEST_DIR/gammu-dummy"
LOG="$TEST_DIR/gammu.log"

cleanup() {
    if [ -f "$LOG" ] ; then
        cat "$LOG"
    fi
    rm -rf "$TEST_DIR"
}

trap cleanup EXIT INT

mkdir -p "$CONFIG_DIR"
cat > "$CONFIG" << EOT
[gammu]
model = dummy
connection = none
port = $DUMMY
gammuloc = /dev/null
logformat = textall
logfile = $LOG
EOT

cp -r ../test/data/gammu-dummy/ "$DUMMY"
mkdir "$DUMMY/fs/test"
find $TEST_DIR

export XDG_CONFIG_HOME="$TEST_DIR"


./addcontacts.py ME ../test/data/gammu.vcf
./addfile.py ../test/data/gammu.vcf test
./async.py
./backup_convertor.py ../test/data/gammu.vcf "$TEST_DIR/test.backup"
./batteryinfo.py
./debugging.py
./dialvoice.py 1234
./doc-exceptions.py
./dummy_phone.py "$CONFIG"
./filesystem_test.py --config "$CONFIG" --folder "test"
./getallcalendar.py
./getallmemory_nonext.py ME
./getallmemory.py SM
./getallsms_decode.py
./getallsms.py
./getalltodo.py
# This is an infinite loop
# ./incoming.py
./getdiverts.py
./listfilesystem.py
./mass_sms.py "Test message" 123 456
./network_info.py
./pdu_decoder.py "079124602009999002AB098106845688F8907080517375809070805183018000"
#./read_sms_backup.py
./savesmspercontact.py
./sendlongsms.py "$CONFIG" 132
./sendsms.py "$CONFIG" 132
echo "#123" | ./service_numbers.py
./setdiverts.py 123
#./smsbackup.py
# Needs SMSD
#./smsd_inject.py
# Needs SMSD
#./smsd_state.py
# This is an infinite loop
#./sms_replier.py
./vcs.py
./worker.py
