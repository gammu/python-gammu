/*
 * python-gammu - Phone communication libary
 * Copyright (C) 2003 - 2017 Michal Čihař
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
			i = PyLong_AsLong(o);
			if (i == 0)
				return FALSE;
			else
				return TRUE;
		}
#if PY_MAJOR_VERSION < 3
		if (PyInt_Check(o)) {
			i = PyInt_AsLong(o);
			if (i == 0)
				return FALSE;
			else
				return TRUE;
		}
		if (PyString_Check(o)) {
			s = PyString_AsString(o);
			if (isdigit((int)s[0])) {
				i = atoi(s);
				if (i == 0)
					return FALSE;
				else
					return TRUE;
			} else if (strcasecmp(s, "yes") == 0) {
				return TRUE;
			} else if (strcasecmp(s, "true") == 0) {
				return TRUE;
			} else if (strcasecmp(s, "no") == 0) {
				return FALSE;
			} else if (strcasecmp(s, "false") == 0) {
				return FALSE;
			} else {
				PyErr_Format(PyExc_ValueError,
					     "String value of '%s' doesn't seem to be boolean",
					     key);
				return BOOL_INVALID;
			}
		}
#endif
		if (PyUnicode_Check(o)) {
			o2 = PyUnicode_AsASCIIString(o);
			if (o2 == NULL) {
				return BOOL_INVALID;
			}
			s = PyBytes_AsString(o2);
			if (isdigit((int)s[0])) {
				i = atoi(s);
				Py_DECREF(o2);
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
	char *s;
	int i;

	o = PyDict_GetItemString(dict, key);
	if (o == NULL) {
		PyErr_Format(PyExc_ValueError, "Missing key in dictionary: %s",
			     key);
		return INT_INVALID;
	}

	if (PyLong_Check(o)) {
		/* Well we loose here something, but it is intentional :-) */
		return (int)PyLong_AsLongLong(o);
	}

#if PY_MAJOR_VERSION < 3
	if (PyInt_Check(o)) {
		return PyInt_AsLong(o);
	}

	if (PyString_Check(o)) {
		s = PyString_AsString(o);
		if (isdigit((int)s[0])) {
			i = atoi(s);
			return i;
		} else {
			PyErr_Format(PyExc_ValueError,
				     "Value of '%s' doesn't seem to be integer",
				     key);
			return INT_INVALID;
		}
	}
#endif

	if (PyUnicode_Check(o)) {
		o2 = PyUnicode_AsASCIIString(o);
		if (o2 == NULL) {
			return INT_INVALID;
		}
		s = PyBytes_AsString(o2);
		if (isdigit((int)s[0])) {
			i = atoi(s);
			Py_DECREF(o2);
			return i;
		} else {
			Py_DECREF(o2);
			PyErr_Format(PyExc_ValueError,
				     "Value of '%s' doesn't seem to be integer",
				     key);
			return INT_INVALID;
		}
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

int CopyStringFromDict(PyObject * dict, const char *key, size_t len,
		       unsigned char *dest)
{
	unsigned char *s;

	s = GetStringFromDict(dict, key);
	if (s == NULL)
		return 0;
	if (UnicodeLength(s) > len) {
		pyg_warning("Truncating text %s to %ld chars!\n", key,
			    (long)len);
		s[2 * len] = 0;
		s[(2 * len) + 1] = 0;
	}
	CopyUnicodeString(dest, s);
	free(s);
	return 1;
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
#if PY_MAJOR_VERSION < 3
	else if (PyString_Check(o)) {
		ps = PyString_AsString(o);
	}
#endif


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

	data = GetDataFromDict(dict, key, length);

	result = (char *)malloc(*length);
	if (result == NULL) {
		PyErr_Format(PyExc_ValueError, "Failed to allocate memory!");
		return NULL;
	}
	memcpy(result, data, *length);

	return result;
}


/*
 * vim: noexpandtab sw=8 ts=8 sts=8:
 */
