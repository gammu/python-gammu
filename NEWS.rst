3.2.3
=====

* Fixed uninitalized memory usage in DeleteSMS.

3.2.2
=====

* Fixed metadata in published wheels.
* Avoid using some of deprecated Python APIs.

3.2.1
=====

* Reintroduced 32-bit wheels for Windows.

3.2
===

* Add support for polling on the async worker
* Utilize CI on GitHub
* Modernize codebase using pyupgrade, isort and black

3.1
===

* Fix an issue where the gammu worker thread could be brought down if a callback throws an exception

3.0
===

* Add support for asyncio in the gammu worker
* Dropped support for Python 2.
* Windows binaries built with Gammu 1.41.0.

2.12
====

* Windows binaries built with Gammu 1.40.0.

2.11
====

* Add support for the USSD in SMSD.
* Python 2.7 binaries available for Windows.

2.10
====

* Testsuite compatibility with Gammu 1.38.5.

2.9
===

* Fixed compilation under Windows.

2.8
===

* Make parameters to CancelCall and AnswerCall optional.
* Added support for UTF-16 Unicode chars (emojis).

2.7
===

* Needs Gammu >= 1.37.90 due to API changes.

2.6
===

* Fixed error when creating new contact.
* Fixed possible testsuite errors.

2.5
===

* Compatibility with Gammu >= 1.36.7

2.4
===

* Fixed possible crash when initializing SMSD with invalid parameters.
* Fixed crash on handling diverts on certain architectures.

2.3
===

* License changed tp GPL version 2 or later.
* Documentation improvements.

2.2
===

* Documentation improvements.
* Code cleanups.

2.1
===

* Include data required for tests in tarball.
* Include NEWS.rst in tarball.
* Fixed possible crash when changing debug file.
* Fixed various errors found by coverity.

2.0
===

* Separate Python module.
* Compiles using distutils.
* Support Python 3.
