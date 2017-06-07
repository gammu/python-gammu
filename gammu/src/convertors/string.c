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

/* Unicode strings conversion between Gammu and Python */

#include "convertors.h"

unsigned char *StringPythonToGammu(PyObject * o)
{
	PyObject *u;
	Py_UNICODE *ps;
	unsigned char *gs;

#if PY_MAJOR_VERSION >= 3
	u = PyObject_Str(o);
#else
	u = PyObject_Unicode(o);
#endif

	if (u == NULL) {
		PyErr_Format(PyExc_ValueError,
			     "Value can not be converted to unicode object");
		return NULL;
	}

	ps = PyUnicode_AsUnicode(u);
	if (ps == NULL) {
		PyErr_Format(PyExc_ValueError, "Can not get unicode value");
		return NULL;
	}
	gs = strPythonToGammu(ps, PyUnicode_GetSize(u));
	Py_DECREF(u);
	return gs;
}

unsigned char *strPythonToGammu(const Py_UNICODE * src, const size_t len)
{
	unsigned char *dest;
	Py_UNICODE wc, tmp;
	size_t i, j;

	/* Allocate memory */
	dest = malloc((len + 1) * 2 * 2 * sizeof(unsigned char));
	if (dest == NULL) {
		PyErr_SetString(PyExc_MemoryError,
				"Not enough memory to allocate string");
		return NULL;
	}

	/* Convert and copy string. */
	for (i = 0, j = 0; i < len; i++) {
		if (src[i] > 0xffff) {
			wc = src[i] - 0x10000;
			tmp = 0xD800 | (wc >> 10);
			dest[(j * 2)] = (tmp >> 8) & 0xff;
			dest[(j * 2) + 1] = tmp & 0xff;
			j++;

			tmp = 0xDC00 | (wc & 0x3ff);

			dest[(j * 2)] = (tmp >> 8) & 0xff;
			dest[(j * 2) + 1] = tmp & 0xff;
			j++;
		} else {
			dest[(j * 2)] = (src[i] >> 8) & 0xff;
			dest[(j * 2) + 1] = src[i] & 0xff;
			j++;
		}
	}

	/* Zero terminate string. */
	dest[(j * 2)] = 0;
	dest[(j * 2) + 1] = 0;

	return dest;
}

Py_UNICODE *strGammuToPython(const unsigned char *src)
{
	int len = 0;
	size_t out_len = 0;

	/* Get string length */
	len = UnicodeLength(src);

	return strGammuToPythonL(src, len, &out_len);
}

Py_UNICODE *strGammuToPythonL(const unsigned char *src, const int len, size_t *out_len)
{
	Py_UNICODE *dest;
	Py_UNICODE value, second;
	int i;

	/* Allocate memory */
	dest = malloc((len + 1) * sizeof(Py_UNICODE));
	if (dest == NULL) {
		PyErr_SetString(PyExc_MemoryError,
				"Not enough memory to allocate string");
		return NULL;
	}

	/* Convert string without zero at the end. */
	*out_len = 0;
	for (i = 0; i < len; i++) {
		value = (src[2 * i] << 8) + src[(2 * i) + 1];
		if (value >= 0xD800 && value <= 0xDBFF) {
			second = src[(i + 1) * 2] * 256 + src[(i + 1) * 2 + 1];
			if (second >= 0xDC00 && second <= 0xDFFF) {
				value = ((value - 0xD800) << 10) + (second - 0xDC00) + 0x010000;
				i++;
			} else if (second == 0) {
				/* Surrogate at the end of string */
				value = 0xFFFD; /* REPLACEMENT CHARACTER */
			}
		}
		dest[(*out_len)++] = value;
	}
	/* Add trailing zero */
	dest[*out_len] = 0;

	return dest;
}

PyObject *UnicodeStringToPython(const unsigned char *src)
{
	Py_ssize_t len;

	len = UnicodeLength(src);
	return UnicodeStringToPythonL(src, len);
}

PyObject *UnicodeStringToPythonL(const unsigned char *src, const Py_ssize_t len)
{
	Py_UNICODE *val;
	PyObject *res;
	size_t out_len = 0;

	val = strGammuToPythonL(src, len, &out_len);
	if (val == NULL)
		return NULL;
	res = PyUnicode_FromUnicode(val, out_len);
	free(val);
	return res;
}

PyObject *LocaleStringToPython(const char *src)
{
	unsigned char *w;
	size_t len;
	PyObject *ret;

	/* Length of input */
	len = strlen(src);

	/* Allocate it */
	w = malloc(2 * (len + 5));
	if (w == NULL) {
		PyErr_SetString(PyExc_MemoryError,
				"Not enough memory to allocate string");
		return NULL;
	}

	EncodeUnicode(w, src, len);

	ret = UnicodeStringToPython(w);
	free(w);
	return ret;
}

/*
 * vim: noexpandtab sw=8 ts=8 sts=8:
 */
