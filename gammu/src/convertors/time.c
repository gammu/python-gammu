/*
 * python-gammu - Phone communication libary
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

PyObject *BuildPythonDateTime(const GSM_DateTime * dt)
{
	PyObject *pModule;
	PyObject *result;

	if (dt->Year == 0) {
		Py_RETURN_NONE;
	}

	/* import datetime */
	pModule = PyImport_ImportModule("datetime");
	if (pModule == NULL)
		return NULL;

	/* create datetime object */
	result = PyObject_CallMethod(pModule,
				     "datetime",
				     "iiiiii",
				     dt->Year,
				     dt->Month,
				     dt->Day, dt->Hour, dt->Minute, dt->Second);

	Py_DECREF(pModule);

	return result;
}

PyObject *BuildPythonTime(const GSM_DateTime * dt)
{
	PyObject *pModule;
	PyObject *result;

	/* import datetime */
	pModule = PyImport_ImportModule("datetime");
	if (pModule == NULL)
		return NULL;

	/* create datetime object */
	result = PyObject_CallMethod(pModule,
				     "time",
				     "iii", dt->Hour, dt->Minute, dt->Second);

	Py_DECREF(pModule);

	return result;
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

	return 1;
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
		PyErr_Format(PyExc_ValueError,
			     "Attribute %s doesn't seem to be integer", "hour");
		return 0;
	}
	dt->Hour = PyLong_AsLong(result);

	result = PyObject_GetAttrString(pydt, "minute");
	if (result == NULL)
		return 0;
	if (!PyLong_Check(result)) {
		PyErr_Format(PyExc_ValueError,
			     "Attribute %s doesn't seem to be integer",
			     "minute");
		return 0;
	}
	dt->Minute = PyLong_AsLong(result);

	result = PyObject_GetAttrString(pydt, "second");
	if (result == NULL)
		return 0;
	if (!PyLong_Check(result)) {
		PyErr_Format(PyExc_ValueError,
			     "Attribute %s doesn't seem to be integer",
			     "second");
		return 0;
	}
	dt->Second = PyLong_AsLong(result);

	return 1;
}

/*
 * vim: noexpandtab sw=8 ts=8 sts=8:
 */
