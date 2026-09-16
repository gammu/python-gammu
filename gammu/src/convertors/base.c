/*
 * python-gammu - Phone communication library
 * Copyright (C) 2003 - 2018 Michal Čihař
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 *
 * vim: expandtab sw=4 ts=4 sts=4:
 */

/* Basic getters from Python objects */
#include "convertors.h"
#include "misc.h"

/* Strings */
#ifdef HAVE_STRING_H
#include <string.h>
#endif
#ifdef HAVE_STRINGS_H
#include <strings.h>
#endif
#include <bytesobject.h>
#include <errno.h>

/* Parse the complete ASCII decimal string, without atoi's undefined overflow. */
static int IntFromString(PyObject *bytes, const char *key)
{
	char *s = PyBytes_AS_STRING(bytes);
	Py_ssize_t length = PyBytes_GET_SIZE(bytes);
	Py_ssize_t index;
	long value;

	for (index = 0; index < length; index++) {
		if (s[index] < '0' || s[index] > '9')
			break;
	}
	if (length == 0 || index != length) {
		PyErr_Format(PyExc_ValueError,
			     "Value of '%s' doesn't seem to be integer", key);
		return INT_INVALID;
	}

	errno = 0;
	value = strtol(s, NULL, 10);
	/* INT_MAX is reserved for the error sentinel. */
	if (errno == ERANGE || value >= INT_MAX) {
		PyErr_Format(PyExc_OverflowError,
			     "Value of '%s' is out of range for an integer", key);
		return INT_INVALID;
	}
	return (int)value;
}

gboolean BoolFromPython(PyObject * o, const char *key)
{
	char *s;
	int i;
	PyObject *o2;

	if (o == Py_None) {
		return FALSE;
	}

	if (!PyBool_Check(o)) {
		if (PyLong_Check(o)) {
			i = PyObject_IsTrue(o);
			return i < 0 ? BOOL_INVALID : (gboolean)i;
		}
		if (PyUnicode_Check(o)) {
			o2 = PyUnicode_AsASCIIString(o);
			if (o2 == NULL) {
				return BOOL_INVALID;
			}
			s = PyBytes_AsString(o2);
			if (isdigit((int)s[0])) {
				i = IntFromString(o2, key);
				Py_DECREF(o2);
				if (i == INT_INVALID)
					return BOOL_INVALID;
				if (i == 0)
					return FALSE;
				else
					return TRUE;
			} else if (strcasecmp(s, "yes") == 0) {
				Py_DECREF(o2);
				return TRUE;
			} else if (strcasecmp(s, "true") == 0) {
				Py_DECREF(o2);
				return TRUE;
			} else if (strcasecmp(s, "no") == 0) {
				Py_DECREF(o2);
				return FALSE;
			} else if (strcasecmp(s, "false") == 0) {
				Py_DECREF(o2);
				return FALSE;
			} else {
				Py_DECREF(o2);
				PyErr_Format(PyExc_ValueError,
					     "String value of '%s' doesn't seem to be boolean",
					     key);
				return BOOL_INVALID;
			}
		}

		PyErr_Format(PyExc_ValueError,
			     "Value of '%s' doesn't seem to be boolean", key);
		return BOOL_INVALID;
	}

	if (Py_False == o)
		return FALSE;
	else if (Py_True == o)
		return TRUE;

	PyErr_Format(PyExc_ValueError,
		     "Bool value of '%s' doesn't seem to be boolean", key);
	return BOOL_INVALID;
}

gboolean GetBoolFromDict(PyObject * dict, const char *key)
{
	PyObject *o;

	o = PyDict_GetItemString(dict, key);
	if (o == NULL) {
		PyErr_Format(PyExc_ValueError, "Missing key in dictionary: %s",
			     key);
		return BOOL_INVALID;
	}

	return BoolFromPython(o, key);
}

int GetIntFromDict(PyObject * dict, const char *key)
{
	PyObject *o;
	PyObject *o2;
	int i;
	long value;

	o = PyDict_GetItemString(dict, key);
	if (o == NULL) {
		PyErr_Format(PyExc_ValueError, "Missing key in dictionary: %s",
			     key);
		return INT_INVALID;
	}

	if (PyLong_Check(o)) {
		value = PyLong_AsLong(o);
		if (value == -1 && PyErr_Occurred())
			return INT_INVALID;
		/* INT_MAX is reserved for the error sentinel. */
		if (value < INT_MIN || value >= INT_MAX) {
			PyErr_Format(PyExc_OverflowError,
				     "Value of '%s' is out of range for an integer", key);
			return INT_INVALID;
		}
		return (int)value;
	}

	if (PyUnicode_Check(o)) {
		o2 = PyUnicode_AsASCIIString(o);
		if (o2 == NULL) {
			return INT_INVALID;
		}
		i = IntFromString(o2, key);
		Py_DECREF(o2);
		return i;
	}

	PyErr_Format(PyExc_ValueError,
		     "Value of '%s' doesn't seem to be integer", key);
	return INT_INVALID;
}

unsigned char *GetStringFromDict(PyObject * dict, const char *key)
{
	PyObject *o;

	o = PyDict_GetItemString(dict, key);
	if (o == NULL) {
		PyErr_Format(PyExc_ValueError, "Missing key in dictionary: %s",
			     key);
		return NULL;
	}

	return StringPythonToGammu(o);
}

int CopyStringFromDict(PyObject * dict, const char *key, size_t capacity,
		       unsigned char *dest)
{
	unsigned char *s;
	int result;

	s = GetStringFromDict(dict, key);
	if (s == NULL)
		return 0;
	result = CopyUnicodeStringSized(dest, capacity, s, key);
	free(s);
	return result;
}

GSM_DateTime GetDateTimeFromDict(PyObject * dict, const char *key)
{
	PyObject *o;
	GSM_DateTime dt;

	memset(&dt, 0, sizeof(GSM_DateTime));

	o = PyDict_GetItemString(dict, key);
	if (o == NULL) {
		PyErr_Format(PyExc_ValueError, "Missing key in dictionary: %s",
			     key);
		dt.Year = -1;
		return dt;
	}

	if (!BuildGSMDateTime(o, &dt)) {
		dt.Year = -1;
	} else {
		/* We use this as an error value */
		if (dt.Year == -1) {
			dt.Year = 0;
		}
	}
	return dt;
}

GSM_DateTime GetDateFromDict(PyObject * dict, const char *key)
{
	PyObject *o;
	GSM_DateTime dt;

	memset(&dt, 0, sizeof(GSM_DateTime));

	o = PyDict_GetItemString(dict, key);
	if (o == NULL) {
		PyErr_Format(PyExc_ValueError, "Missing key in dictionary: %s",
			     key);
		dt.Year = -1;
		return dt;
	}

	if (!BuildGSMDate(o, &dt)) {
		dt.Year = -1;
	}
	return dt;
}

char *GetCharFromDict(PyObject * dict, const char *key)
{
	PyObject *o, *o2 = NULL;
	char *ps = NULL, *result = NULL;
	size_t length;

	o = PyDict_GetItemString(dict, key);
	if (o == NULL) {
		PyErr_Format(PyExc_ValueError, "Missing key in dictionary: %s",
			     key);
		return NULL;
	}

	if (PyUnicode_Check(o)) {
		o2 = PyUnicode_AsASCIIString(o);
		if (o2 == NULL) {
			return NULL;
		}
		ps = PyBytes_AsString(o2);
	}

	if (ps == NULL) {
		PyErr_Format(PyExc_ValueError,
			     "Can not get string value for key %s", key);
		goto out;
	}
	length = strlen(ps) + 1;
	result = (char *)malloc(length);
	if (result == NULL) {
		PyErr_Format(PyExc_ValueError, "Failed to allocate memory!");
		goto out;
	}
	memcpy(result, ps, length);

out:
	if (o2 != NULL) {
		Py_DECREF(o2);
	}
	return result;
}

char *GetDataFromDict(PyObject * dict, const char *key, Py_ssize_t * len)
{
	PyObject *o;
	char *ps;

	o = PyDict_GetItemString(dict, key);
	if (o == NULL) {
		PyErr_Format(PyExc_ValueError, "Missing key in dictionary: %s",
			     key);
		return NULL;
	}
	if (!PyBytes_Check(o)) {
		PyErr_Format(PyExc_ValueError, "Not a bytes string: %s",
			     key);
		return NULL;
	}
	if (PyBytes_AsStringAndSize(o, &ps, len) != 0) {
		PyErr_Format(PyExc_ValueError,
			     "Can not get string value for key %s", key);
		return NULL;
	}
	return ps;
}

char *GetCStringLengthFromDict(PyObject * dict, const char *key,
			       Py_ssize_t * length)
{
	char *result, *data;

	*length = 0;
	data = GetDataFromDict(dict, key, length);
	if (data == NULL)
		return NULL;

	result = (char *)malloc(*length ? (size_t)*length : 1);
	if (result == NULL) {
		PyErr_NoMemory();
		return NULL;
	}
	memcpy(result, data, *length);

	return result;
}


/*
 * vim: noexpandtab sw=8 ts=8 sts=8:
 */
