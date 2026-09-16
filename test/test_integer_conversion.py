# Copyright © 2026 Michal Čihař <michal@cihar.com>
# SPDX-License-Identifier: GPL-2.0-or-later

"""Regression tests for checked integer and boolean conversion."""

import ctypes

import pytest

import gammu

INT_MAX = (1 << (ctypes.sizeof(ctypes.c_int) * 8 - 1)) - 1
INT_MIN = -INT_MAX - 1
OVERFLOW_VALUES = [INT_MIN - 1, INT_MAX, INT_MAX + 1, 2**32, 2**100, -(2**100)]
HUGE_STRING = pytest.param("9" * 10000, id="huge-string")


@pytest.mark.parametrize(
    "value",
    [*OVERFLOW_VALUES, str(INT_MAX), str(INT_MAX + 1), str(2**100), HUGE_STRING],
)
def test_required_integer_overflow(value):
    with pytest.raises(OverflowError):
        gammu.StateMachine().SetSMSC({"Location": value})


@pytest.mark.parametrize(
    "value", [INT_MIN, -1, 0, 1, INT_MAX - 1, False, True, "001", str(INT_MAX - 1)]
)
def test_valid_integer_reaches_next_field(value):
    # The next required field is missing: integer conversion must have succeeded.
    with pytest.raises(ValueError, match="Missing key in dictionary: Number"):
        gammu.StateMachine().SetSMSC({"Location": value})


@pytest.mark.parametrize(
    "value", ["", "1junk", "1.5", "1\x00", "1\x002", "+1", "-1", " 1", "1 "]
)
def test_invalid_integer_string(value):
    with pytest.raises(ValueError, match="doesn't seem to be integer"):
        gammu.StateMachine().SetSMSC({"Location": value})


@pytest.mark.parametrize("value", [*OVERFLOW_VALUES, HUGE_STRING])
def test_optional_integer_uses_default_on_overflow(value):
    sms = {"Text": "ok", "Number": "123", "Folder": 1, "SMSC": {"Location": 1}}
    expected = gammu.EncodePDU(sms)
    assert gammu.EncodePDU({**sms, "MessageReference": value}) == expected


@pytest.mark.parametrize("value", [*OVERFLOW_VALUES, HUGE_STRING, None, "invalid"])
def test_mms_message_size_uses_default(value):
    indicator = {
        "Address": "http://example.com/mms/123",
        "Title": "Photo message",
        "Sender": "+420123456789",
        "Class": "Personal",
    }
    info = {"Entries": [{"ID": "MMSIndicatorLong", "MMSIndicator": indicator}]}
    # Both a missing key and a failed conversion must clear the Python exception.
    for extra in ({}, {"MessageSize": value}):
        indicator.update(extra)
        sms = gammu.EncodeSMS(info)
        assert gammu.DecodeSMS(sms)["Entries"][0]["MMSIndicator"]["MessageSize"] == 0


@pytest.mark.parametrize(
    "value", [None, False, True, 0, 1, -1, 2**32, 2**100, -(2**100)]
)
def test_boolean_integer_truth(value):
    machine = gammu.StateMachine()
    machine.SetConfig(0, {"StartInfo": value})
    assert machine.GetConfig(0)["StartInfo"] == bool(value)


@pytest.mark.parametrize("value", [str(INT_MAX), str(2**100), HUGE_STRING])
def test_boolean_string_overflow(value):
    with pytest.raises(OverflowError):
        gammu.StateMachine().SetConfig(0, {"StartInfo": value})


@pytest.mark.parametrize(
    ("value", "expected"), [("0", False), ("001", True), ("42", True)]
)
def test_boolean_numeric_string(value, expected):
    machine = gammu.StateMachine()
    machine.SetConfig(0, {"StartInfo": value})
    assert machine.GetConfig(0)["StartInfo"] == expected
