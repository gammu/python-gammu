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

/* DateTime conversions */

#include "convertors.h"

/* Import the datetime C API before using its types or constructors. */
#include <datetime.h>

static int ImportDateTime(void)
{
	if (PyDateTimeAPI == NULL) {
		PyDateTime_IMPORT;
	}
	return PyDateTimeAPI != NULL;
}

static PyObject *BuildPythonTimezone(int seconds)
{
	PyObject *offset;
	PyObject *timezone;

	if (!ImportDateTime())
		return NULL;
	offset = PyDelta_FromDSU(0, seconds, 0);
	if (offset == NULL)
		return NULL;
	timezone = PyTimeZone_FromOffset(offset);
	Py_DECREF(offset);
	return timezone;
}

PyObject *BuildPythonDateTime(const GSM_DateTime * dt)
{
	PyObject *timezone;
	PyObject *result;

	if (dt->Year == 0) {
		Py_RETURN_NONE;
	}
	timezone = BuildPythonTimezone(dt->Timezone);
	if (timezone == NULL)
		return NULL;
	result = PyDateTimeAPI->DateTime_FromDateAndTime(
		dt->Year, dt->Month, dt->Day, dt->Hour, dt->Minute, dt->Second,
		0, timezone, PyDateTimeAPI->DateTimeType);
	Py_DECREF(timezone);
	return result;
}

PyObject *BuildPythonTime(const GSM_DateTime * dt)
{
	PyObject *timezone;
	PyObject *result;

	timezone = BuildPythonTimezone(dt->Timezone);
	if (timezone == NULL)
		return NULL;
	result = PyDateTimeAPI->Time_FromTime(
		dt->Hour, dt->Minute, dt->Second, 0, timezone,
		PyDateTimeAPI->TimeType);
	Py_DECREF(timezone);
	return result;
}

static int BuildGSMTimezone(PyObject *value, GSM_DateTime *dt)
{
	PyObject *method;
	PyObject *offset;
	int days, seconds;

	method = PyObject_GetAttrString(value, "utcoffset");
	if (method == NULL) {
		/* Preserve support for datetime-like objects without a timezone. */
		if (PyErr_ExceptionMatches(PyExc_AttributeError)) {
			PyErr_Clear();
			return 1;
		}
		return 0;
	}
	offset = PyObject_CallNoArgs(method);
	Py_DECREF(method);
	if (offset == NULL)
		return 0;
	if (offset == Py_None) {
		Py_DECREF(offset);
		return 1;
	}
	if (!ImportDateTime()) {
		Py_DECREF(offset);
		return 0;
	}
	if (!PyDelta_Check(offset)) {
		Py_DECREF(offset);
		PyErr_SetString(PyExc_TypeError,
			       "utcoffset() must return a timedelta or None");
		return 0;
	}
	days = PyDateTime_DELTA_GET_DAYS(offset);
	seconds = PyDateTime_DELTA_GET_SECONDS(offset);
	/* Check days before multiplication to avoid integer overflow. */
	if (days < -1 || days > 0 || (days == -1 && seconds == 0)) {
		Py_DECREF(offset);
		PyErr_SetString(PyExc_ValueError,
			       "UTC offset must be strictly between -24 and 24 hours");
		return 0;
	}
	if (PyDateTime_DELTA_GET_MICROSECONDS(offset) != 0) {
		Py_DECREF(offset);
		PyErr_SetString(PyExc_ValueError,
			       "UTC offset must be a whole number of seconds");
		return 0;
	}
	dt->Timezone = days * 86400 + seconds;
	Py_DECREF(offset);
	return 1;
}

int BuildGSMDateTime(PyObject * pydt, GSM_DateTime * dt)
{
	PyObject *result;
	static GSM_DateTime nulldt = { 0, 0, 0, 0, 0, 0, 0 };
	*dt = nulldt;

	if (pydt == Py_None)
		return 1;

	result = PyObject_GetAttrString(pydt, "year");
	if (result == NULL) {
		PyErr_Format(PyExc_ValueError, "Attribute year is missing");
		return 0;
	}
	if (!PyLong_Check(result)) {
		PyErr_Format(PyExc_ValueError,
			     "Attribute %s doesn't seem to be integer", "year");
		Py_DECREF(result);
		return 0;
	}
	dt->Year = PyLong_AsLong(result);
	Py_DECREF(result);

	result = PyObject_GetAttrString(pydt, "month");
	if (result == NULL) {
		PyErr_Format(PyExc_ValueError, "Attribute month is missing");
		return 0;
	}
	if (!PyLong_Check(result)) {
		Py_DECREF(result);
		PyErr_Format(PyExc_ValueError,
			     "Attribute %s doesn't seem to be integer",
			     "month");
		return 0;
	}
	dt->Month = PyLong_AsLong(result);
	Py_DECREF(result);

	result = PyObject_GetAttrString(pydt, "day");
	if (result == NULL) {
		PyErr_Format(PyExc_ValueError, "Attribute day is missing");
		return 0;
	}
	if (!PyLong_Check(result)) {
		Py_DECREF(result);
		PyErr_Format(PyExc_ValueError,
			     "Attribute %s doesn't seem to be integer", "day");
		return 0;
	}
	dt->Day = PyLong_AsLong(result);
	Py_DECREF(result);

	result = PyObject_GetAttrString(pydt, "hour");
	if (result == NULL) {
		PyErr_Format(PyExc_ValueError, "Attribute hour is missing");
		return 0;
	}
	if (!PyLong_Check(result)) {
		Py_DECREF(result);
		PyErr_Format(PyExc_ValueError,
			     "Attribute %s doesn't seem to be integer", "hour");
		return 0;
	}
	dt->Hour = PyLong_AsLong(result);
	Py_DECREF(result);

	result = PyObject_GetAttrString(pydt, "minute");
	if (result == NULL) {
		PyErr_Format(PyExc_ValueError, "Attribute minute is missing");
		return 0;
	}
	if (!PyLong_Check(result)) {
		Py_DECREF(result);
		PyErr_Format(PyExc_ValueError,
			     "Attribute %s doesn't seem to be integer",
			     "minute");
		return 0;
	}
	dt->Minute = PyLong_AsLong(result);
	Py_DECREF(result);

	result = PyObject_GetAttrString(pydt, "second");
	if (result == NULL) {
		PyErr_Format(PyExc_ValueError, "Attribute second is missing");
		return 0;
	}
	if (!PyLong_Check(result)) {
		Py_DECREF(result);
		PyErr_Format(PyExc_ValueError,
			     "Attribute %s doesn't seem to be integer",
			     "second");
		return 0;
	}
	dt->Second = PyLong_AsLong(result);
	Py_DECREF(result);

	return BuildGSMTimezone(pydt, dt);
}

int BuildGSMDate(PyObject * pydt, GSM_DateTime * dt)
{
	PyObject *result;
	static GSM_DateTime nulldt = { 0, 0, 0, 0, 0, 0, 0 };
	*dt = nulldt;

	if (pydt == Py_None)
		return 1;

	result = PyObject_GetAttrString(pydt, "year");
	if (result == NULL)
		return 0;
	if (!PyLong_Check(result)) {
		PyErr_Format(PyExc_ValueError,
			     "Attribute %s doesn't seem to be integer", "year");
		return 0;
	}
	dt->Year = PyLong_AsLong(result);

	result = PyObject_GetAttrString(pydt, "month");
	if (result == NULL)
		return 0;
	if (!PyLong_Check(result)) {
		PyErr_Format(PyExc_ValueError,
			     "Attribute %s doesn't seem to be integer",
			     "month");
		return 0;
	}
	dt->Month = PyLong_AsLong(result);

	result = PyObject_GetAttrString(pydt, "day");
	if (result == NULL)
		return 0;
	if (!PyLong_Check(result)) {
		PyErr_Format(PyExc_ValueError,
			     "Attribute %s doesn't seem to be integer", "day");
		return 0;
	}
	dt->Day = PyLong_AsLong(result);
	return 1;
}

int BuildGSMTime(PyObject * pydt, GSM_DateTime * dt)
{
	PyObject *result;
	static GSM_DateTime nulldt = { 0, 0, 0, 0, 0, 0, 0 };
	*dt = nulldt;

	if (pydt == Py_None)
		return 1;

	result = PyObject_GetAttrString(pydt, "hour");
	if (result == NULL)
		return 0;
	if (!PyLong_Check(result)) {
		Py_DECREF(result);
		PyErr_Format(PyExc_ValueError,
			     "Attribute %s doesn't seem to be integer", "hour");
		return 0;
	}
	dt->Hour = PyLong_AsLong(result);
	Py_DECREF(result);

	result = PyObject_GetAttrString(pydt, "minute");
	if (result == NULL)
		return 0;
	if (!PyLong_Check(result)) {
		Py_DECREF(result);
		PyErr_Format(PyExc_ValueError,
			     "Attribute %s doesn't seem to be integer",
			     "minute");
		return 0;
	}
	dt->Minute = PyLong_AsLong(result);
	Py_DECREF(result);

	result = PyObject_GetAttrString(pydt, "second");
	if (result == NULL)
		return 0;
	if (!PyLong_Check(result)) {
		Py_DECREF(result);
		PyErr_Format(PyExc_ValueError,
			     "Attribute %s doesn't seem to be integer",
			     "second");
		return 0;
	}
	dt->Second = PyLong_AsLong(result);
	Py_DECREF(result);

	return BuildGSMTimezone(pydt, dt);
}

/*
 * vim: noexpandtab sw=8 ts=8 sts=8:
 */
