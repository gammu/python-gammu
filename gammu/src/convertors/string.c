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

/* Unicode strings conversion between Gammu and Python */

#include "convertors.h"

unsigned char *StringPythonToGammu(PyObject * o)
{
	PyObject *u;
	wchar_t *ps;
	unsigned char *gs;
	Py_ssize_t len;

	u = PyObject_Str(o);

	if (u == NULL) {
		PyErr_Format(PyExc_ValueError,
			     "Value can not be converted to unicode object");
		return NULL;
	}

	/* On Windows, supplementary characters use two wchar_t code units. */
	ps = PyUnicode_AsWideCharString(u, &len);
	if (ps == NULL) {
		Py_DECREF(u);
		return NULL;
	}

	gs = strPythonToGammu(ps, len);
	PyMem_Free(ps);
	Py_DECREF(u);
	return gs;
}

unsigned char *strPythonToGammu(const wchar_t * src, const size_t len)
{
	unsigned char *dest;
	wchar_t wc, tmp;
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

wchar_t *strGammuToPython(const unsigned char *src)
{
	int len = 0;
	size_t out_len = 0;

	/* Get string length */
	len = UnicodeLength(src);

	return strGammuToPythonL(src, len, &out_len);
}

wchar_t *strGammuToPythonL(const unsigned char *src, const int len, size_t *out_len)
{
	wchar_t *dest;
	wchar_t value, second;
	int i;

	/* Allocate memory */
	dest = malloc((len + 1) * sizeof(wchar_t));
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
			/* High surrogate */
			if (i + 1 < len) {
				second = src[(i + 1) * 2] * 256 + src[(i + 1) * 2 + 1];
				if (second >= 0xDC00 && second <= 0xDFFF) {
					/* Valid surrogate pair */
					if (sizeof(wchar_t) == 4) {
						/* wchar_t is 4 bytes (UTF-32): convert to codepoint */
						value = ((value - 0xD800) << 10) + (second - 0xDC00) + 0x010000;
						i++;
					} else {
						/* wchar_t is 2 bytes (UTF-16): keep surrogates */
						dest[(*out_len)++] = value;
						value = second;
						i++;
					}
				} else {
					/* Invalid surrogate pair */
					value = 0xFFFD; /* REPLACEMENT CHARACTER */
				}
			} else {
				/* Surrogate at end of string */
				value = 0xFFFD; /* REPLACEMENT CHARACTER */
			}
		} else if (value >= 0xDC00 && value <= 0xDFFF) {
			/* Standalone low surrogate (not preceded by high surrogate) */
			value = 0xFFFD; /* REPLACEMENT CHARACTER */
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
	wchar_t *val;
	PyObject *res;
	size_t out_len = 0;

	val = strGammuToPythonL(src, len, &out_len);
	if (val == NULL)
		return NULL;
	res = PyUnicode_FromWideChar(val, out_len);
	free(val);
	return res;
}

/* Capacity is in bytes, including the two-byte Unicode terminator. */
int CopyUnicodeStringSized(unsigned char *dest, size_t capacity,
                           const unsigned char *src, const char *field)
{
	size_t length = UnicodeLength(src);

	if (capacity < 2 || length > capacity / 2 - 1) {
		PyErr_Format(PyExc_ValueError,
			     "%s is too long (maximum is %zu UTF-16 code units)",
			     field, capacity < 2 ? 0 : capacity / 2 - 1);
		return 0;
	}
	memcpy(dest, src, (length + 1) * 2);
	return 1;
}

int EncodeUnicodeSized(unsigned char *dest, size_t capacity,
                       const char *src, size_t length, const char *field)
{
	unsigned char *encoded;
	int result;

	/* Each input byte can produce at most a surrogate pair. */
	if (length > (SIZE_MAX - 2) / 4) {
		PyErr_NoMemory();
		return 0;
	}
	encoded = malloc(length * 4 + 2);
	if (encoded == NULL) {
		PyErr_NoMemory();
		return 0;
	}
	EncodeUnicode(encoded, src, length);
	result = CopyUnicodeStringSized(dest, capacity, encoded, field);
	free(encoded);
	return result;
}

PyObject *LocaleStringToPython(const char *src)
{
	unsigned char *w;
	size_t len, capacity;
	PyObject *ret;

	/* Length of input */
	len = strlen(src);

	/* Allocate it */
	if (len > (SIZE_MAX - 2) / 4) {
		return PyErr_NoMemory();
	}
	capacity = len * 4 + 2;
	w = malloc(capacity);
	if (w == NULL) {
		PyErr_SetString(PyExc_MemoryError,
				"Not enough memory to allocate string");
		return NULL;
	}

	if (!EncodeUnicodeSized(w, capacity, src, len, "Locale string")) {
		free(w);
		return NULL;
	}

	ret = UnicodeStringToPython(w);
	free(w);
	return ret;
}

/*
 * vim: noexpandtab sw=8 ts=8 sts=8:
 */
