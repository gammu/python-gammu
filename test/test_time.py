# vim: expandtab sw=4 ts=4 sts=4:
#
# Copyright © 2003 - 2018 Michal Čihař <michal@cihar.com>
#
# This file is part of python-gammu <https://wammu.eu/python-gammu/>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""Timezone conversion regression tests."""

import datetime
from types import SimpleNamespace

import pytest

import gammu

WALL_TIME = datetime.datetime(2026, 9, 16, 12, 34, 56)


def link_datetime(value):
    sms = gammu.EncodeSMS(
        {"Entries": [{"ID": "ConcatenatedTextLong", "Buffer": "timezone"}]}
    )[0]
    sms["DateTime"] = value
    sms["SMSCDateTime"] = value
    return gammu.LinkSMS([[sms]])[0][0]


@pytest.mark.parametrize(
    "seconds", [0, 7200, -18000, 19800, -12600, 20700, 1, -1, 86399, -86399]
)
def test_datetime_offset_roundtrip(seconds):
    offset = datetime.timedelta(seconds=seconds)
    value = WALL_TIME.replace(tzinfo=datetime.timezone(offset))
    result = link_datetime(value)
    for field in ("DateTime", "SMSCDateTime"):
        assert result[field].replace(tzinfo=None) == WALL_TIME
        assert result[field].utcoffset() == offset


class NoOffset(datetime.tzinfo):
    def utcoffset(self, dt):
        return None


@pytest.mark.parametrize(
    "value",
    [
        WALL_TIME,
        WALL_TIME.replace(tzinfo=NoOffset()),
        SimpleNamespace(year=2026, month=9, day=16, hour=12, minute=34, second=56),
    ],
)
def test_naive_datetime(value):
    result = link_datetime(value)["DateTime"]
    assert result.replace(tzinfo=None) == WALL_TIME
    assert result.tzinfo == datetime.timezone.utc


def test_missing_datetime():
    result = link_datetime(None)
    assert result["DateTime"] is None
    assert result["SMSCDateTime"] is None


@pytest.mark.parametrize(
    ("encoded_offset", "seconds"),
    [(0x00, 0), (0x80, 7200), (0x22, 19800), (0x32, 20700), (0x49, -12600)],
)
def test_decode_pdu_offset(encoded_offset, seconds):
    # SMS-DELIVER: no SMSC, +1234 sender, GSM text "A", 2026-09-16 12:34:56.
    pdu = bytearray.fromhex("0000049121430000629061214365000141")
    pdu[14] = encoded_offset
    value = gammu.DecodePDU(bytes(pdu))["DateTime"]
    assert value.replace(tzinfo=None) == WALL_TIME
    assert value.utcoffset() == datetime.timedelta(seconds=seconds)


@pytest.mark.parametrize(
    ("offset", "error", "message"),
    [
        (42, TypeError, "timedelta"),
        (datetime.timedelta(days=1), ValueError, "24"),
        (datetime.timedelta(days=-1), ValueError, "24"),
        (datetime.timedelta(days=999999999), ValueError, "24"),
        (datetime.timedelta(microseconds=1), ValueError, "whole number"),
        (datetime.timedelta(microseconds=-1), ValueError, "whole number"),
    ],
)
@pytest.mark.parametrize("time_only", [False, True])
def test_invalid_offset(offset, error, message, time_only):
    value = SimpleNamespace(
        year=2026,
        month=9,
        day=16,
        hour=12,
        minute=34,
        second=56,
        utcoffset=lambda: offset,
    )
    state_machine = gammu.StateMachine()
    # Conversion fails before connecting to a phone.
    if time_only:
        with pytest.raises(error, match=message):
            state_machine.SetAlarm(value, Repeating=False)
    else:
        with pytest.raises(error, match=message):
            state_machine.SetDateTime(value)


class BrokenTimezone(datetime.tzinfo):
    def utcoffset(self, dt):
        message = "offset failed"
        raise RuntimeError(message)


@pytest.mark.parametrize("time_only", [False, True])
def test_offset_exception(time_only):
    state_machine = gammu.StateMachine()
    if time_only:
        value = datetime.time(12, 34, tzinfo=BrokenTimezone())
        with pytest.raises(RuntimeError, match="offset failed"):
            state_machine.SetAlarm(value, Repeating=False)
    else:
        value = WALL_TIME.replace(tzinfo=BrokenTimezone())
        with pytest.raises(RuntimeError, match="offset failed"):
            state_machine.SetDateTime(value)
