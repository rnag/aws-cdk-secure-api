=======
History
=======

0.2.0 (2023-05-17)
------------------

**Bugfixes**

* Make code compatible with *Python 3.11*.

**Features and Improvements**

* Add *3.11* to the list of supported Python versions.

0.1.1 (2022-06-24)
------------------

**Bugfixes**

* Remove ``typing.Literal`` usage, so code is compatible with Python 3.7
* Add an import ``from __future__ import annotations`` to modules where it was missing.

**Features and Improvements**

* Update to use the string value of the ``name`` attribute for a ``Http`` Enum member,
  instead of the ``value`` attribute.

0.1.0 (2022-06-24)
------------------

* First release on PyPI.
