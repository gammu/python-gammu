#!/bin/sh
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


./filesystem_test.py --config "$CONFIG" --folder "test"

export XDG_CONFIG_HOME="$TEST_DIR"

./network_info.py
