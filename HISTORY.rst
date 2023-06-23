=======
History
=======

0.5.0 (2023-06-23)
------------------

**Features and Improvements**

* Add option ``use_role`` in ``IAMConfig``, which when enabled will set up
  an IAM Role (with permissions to invoke the API) to be assumed by the IAM User,
  instead of directly attaching an IAM Policy to said User.

0.4.0 (2023-06-22)
------------------

**Features and Improvements**

* Add IAM Authentication via the new ``IAMSecureRestApi`` construct.

0.3.0 (2023-05-17)
------------------

**Features and Improvements**

* Add a helper method ``add_resource_and_lambda_methods``, to set up a new
  API resource, a lambda integration, and setup HTTP method(s) on the
  new resource at the same time.
* Update other helper methods -- such as ``add_lambda_methods`` -- to accept
  an optional ``resource`` parameter, which defaults to the "root" API
  resource (``/``) by default.
* Add ``test`` parameter (boolean) to ``SecureRestApi`` -- if enabled,
  then a live API call to AWS SSM (Parameter Store)
  won't be performed on an initial run, and instead a dummy API key value
  is used.

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
