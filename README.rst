==================
AWS CDK Secure API
==================


.. image:: https://img.shields.io/pypi/v/aws-cdk-secure-api.svg
        :target: https://pypi.org/project/aws-cdk-secure-api

.. image:: https://img.shields.io/pypi/pyversions/aws-cdk-secure-api.svg
        :target: https://pypi.org/project/aws-cdk-secure-api

.. image:: https://github.com/rnag/aws-cdk-secure-api/actions/workflows/dev.yml/badge.svg
        :target: https://github.com/rnag/aws-cdk-secure-api/actions/workflows/dev.yml

.. image:: https://readthedocs.org/projects/aws-cdk-secure-api/badge/?version=latest
        :target: https://aws-cdk-secure-api.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/rnag/aws-cdk-secure-api/shield.svg
     :target: https://pyup.io/repos/github/rnag/aws-cdk-secure-api/
     :alt: Updates



A CDK (v2) Construct Library for Secure REST APIs


* Free software: MIT license
* Documentation: https://aws-cdk-secure-api.readthedocs.io.


Features
--------

* TODO

Usage
-----

Represents a Secure REST API in Amazon API Gateway.

By default, methods in the REST API requires an ``x-api-key`` header in
the request. The API key value is also populated in the CFn *Stack Outputs* by default,
and shows up under the ``APIKey`` name.

Use ``add_resource``, ``add_lambda_methods``, and ``add_methods`` to
configure the API model.

By default, the API will automatically be deployed and accessible from a
public endpoint.

Example:

.. code:: python3

    from aws_cdk_secure_api import SecureRestApi
    from aws_cdk import (aws_apigateway as apigw, aws_lambda as lambda_)

    get_handler = lambda_.Function(self, 'lambda1', runtime=lambda_.Runtime.PYTHON_3_9, ...)
    put_handler = lambda_.Function(self, 'lambda2', runtime=lambda_.Runtime.PYTHON_3_9, ...)

    api = SecureRestApi(self, 'api', rest_api_name='My Secure Service')

    api.add_lambda_methods(get_handler, 'GET')
    api.add_lambda_methods(put_handler, 'PUT', 'POST')


Credits
-------

This package was created with Cookiecutter_ and the `rnag/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/cookiecutter/cookiecutter
.. _`rnag/cookiecutter-pypackage`: https://github.com/rnag/cookiecutter-pypackage
