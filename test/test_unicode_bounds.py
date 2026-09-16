# Copyright © 2026 Michal Čihař <michal@cihar.com>
# SPDX-License-Identifier: GPL-2.0-or-later

"""Regression tests for fixed-size Unicode fields and photo conversion."""

import re

import pytest

import gammu


@pytest.mark.parametrize("text", ["", "plain", "😀", "😀middle𐀀end", "x" * 58 + "😀"])
def test_unicode_roundtrip_preserves_wide_characters(text):
    sms = {
        "Text": text,
        "Number": "123",
        "Folder": 1,
        "SMSC": {"Location": 1},
        "Coding": "Unicode_No_Compression",
    }
    assert gammu.DecodePDU(gammu.EncodePDU(sms))["Text"] == text


@pytest.mark.parametrize(
    ("method", "arguments", "index", "field"),
    [
        ("SetAlarm", ["", 1, True, ""], 3, "Text"),
        ("AddCategory", ["Phonebook", ""], 1, "Name"),
        ("SetCallDivert", ["AllTypes", "All", ""], 2, "Number"),
        ("GetFolderListing", [""], 0, "Folder"),
        ("GetNextRootFolder", [""], 0, "Folder"),
        ("SetFileAttributes", [""], 0, "Folder"),
        ("AddFolder", ["", ""], 0, "FolderID"),
        ("AddFolder", ["", ""], 1, "Name"),
    ],
)
def test_statemachine_unicode_capacity(method, arguments, index, field):
    machine = gammu.StateMachine()
    call = getattr(machine, method)
    arguments = arguments.copy()
    arguments[index] = "x" * 100000
    with pytest.raises(ValueError, match=rf"{field} is too long") as error:
        call(*arguments)
    capacity = int(re.search(r"maximum is (\d+)", str(error.value))[1])
    for value in ["x" * (capacity + 1), "x" * (capacity - 1) + "😀"]:
        arguments[index] = value
        with pytest.raises(ValueError, match=rf"{field} is too long"):
            call(*arguments)
    # Without a connection, fitting values reach phone communication. SetAlarm
    # currently requires a string DateTime argument and fails date conversion.
    for value in ["", "x" * capacity, "x" * (capacity - 2) + "😀"]:
        if method == "SetCallDivert" and "😀" in value:
            continue  # This API uses Gammu's locale encoding.
        arguments[index] = value
        with pytest.raises((gammu.GSMError, ValueError)) as error:
            call(*arguments)
        assert "is too long" not in str(error.value)


@pytest.mark.parametrize("field", ["Name", "ID_FullName"])
@pytest.mark.parametrize("strict", [False, True])
def test_file_unicode_capacity(field, strict):
    def convert(value):
        file = {
            "Name": "file",
            "ID_FullName": "file",
            "Folder": False,
            "Level": 0,
            "Type": "Other",
            "Buffer": b"",
            "Protected": False,
            "ReadOnly": False,
            "Hidden": False,
            "System": False,
            field: value,
        }
        if strict:
            return gammu.StateMachine().SendFilePart(file)
        return gammu.EncodeSMS(
            {"Entries": [{"ID": "ConcatenatedTextLong", "Buffer": "ok", "File": file}]}
        )

    with pytest.raises(ValueError, match=rf"{field} is too long") as error:
        convert("x" * 100000)
    capacity = int(re.search(r"maximum is (\d+)", str(error.value))[1])
    if field == "Name":
        assert capacity == 256
    for value in ["x" * (capacity + 1), "x" * (capacity - 1) + "😀"]:
        with pytest.raises(ValueError, match=rf"{field} is too long"):
            convert(value)
    for value in ["", "x" * capacity, "x" * (capacity - 2) + "😀"]:
        if strict:
            with pytest.raises(gammu.GSMError):
                convert(value)
        else:
            assert convert(value)[0]["Text"] == "ok"


@pytest.mark.parametrize(
    "field", ["Number", "Name", "SMSC.Number", "SMSC.Name", "SMSC.DefaultNumber"]
)
def test_optional_sms_fields_reject_overflow(field):
    sms = {"Text": "ok", "SMSC": {"Location": 1}}
    target = sms
    if field.startswith("SMSC."):
        target = sms["SMSC"]
        field = field.split(".")[1]
    target[field] = "x" * 100000
    with pytest.raises(ValueError, match=rf"{field} is too long"):
        gammu.EncodePDU(sms)


@pytest.mark.parametrize("api", ["SetMemory", "AddMemory", "EncodeVCARD", "EncodeSMS"])
@pytest.mark.parametrize(
    "photo", [{}, {"Value": None}, {"Value": "text"}, {"Value": 123}]
)
@pytest.mark.parametrize("earlier_photo", [False, True])
def test_invalid_photo(api, photo, earlier_photo):
    entries = [{"Type": "Photo", "PictureType": "PNG", **photo}]
    if earlier_photo:
        entries.insert(0, {"Type": "Photo", "PictureType": "PNG", "Value": b"photo"})
    entry = {"MemoryType": "ME", "Location": 1, "Entries": entries}
    message = (
        "Not a bytes string: Value"
        if "Value" in photo
        else "Missing key in dictionary: Value"
    )
    if api == "EncodeSMS":
        call = gammu.EncodeSMS
        argument = {"Entries": [{"ID": "ConcatenatedTextLong", "Phonebook": entry}]}
    elif api == "EncodeVCARD":
        call = gammu.EncodeVCARD
        argument = entry
    else:
        call = getattr(gammu.StateMachine(), api)
        argument = entry
    with pytest.raises(ValueError, match=message):
        call(argument)


@pytest.mark.parametrize("value", [b"", b"photo\x00data"])
def test_valid_photo(value):
    entry = {
        "MemoryType": "ME",
        "Location": 1,
        "Entries": [{"Type": "Photo", "PictureType": "PNG", "Value": value}],
    }
    for method in ["SetMemory", "AddMemory"]:
        with pytest.raises(gammu.GSMError):
            getattr(gammu.StateMachine(), method)(entry)
    assert "BEGIN:VCARD" in gammu.EncodeVCARD(entry)
    assert (
        gammu.EncodeSMS(
            {
                "Entries": [
                    {"ID": "ConcatenatedTextLong", "Buffer": "ok", "Phonebook": entry}
                ]
            }
        )[0]["Text"]
        == "ok"
    )


@pytest.mark.parametrize(
    ("kind", "field"),
    [
        ("Ringtone", "Name"),
        ("Bitmap", "Text"),
        ("Bitmap", "Sender"),
        ("Bookmark", "Address"),
        ("Bookmark", "Title"),
        ("Phonebook", "Value"),
        ("Calendar", "Value"),
        ("ToDo", "Value"),
    ],
)
def test_nested_unicode_fields_reject_overflow(kind, field):
    value = "x" * 100000
    data = {
        "Ringtone": {"Name": value, "Notes": []},
        "Bitmap": [{"Type": "PictureImage", field: value}],
        "Bookmark": {"Location": 1, "Address": "url", "Title": "title", field: value},
        "Phonebook": {"Entries": [{"Type": "Text_Name", "Value": value}]},
        "Calendar": {"Type": "MEETING", "Entries": [{"Type": "TEXT", "Value": value}]},
        "ToDo": {
            "Type": "MEETING",
            "Priority": "High",
            "Entries": [{"Type": "TEXT", "Value": value}],
        },
    }[kind]
    with pytest.raises(ValueError, match=rf"{field} is too long"):
        gammu.EncodeSMS({"Entries": [{"ID": "ConcatenatedTextLong", kind: data}]})
