==================
aws-cdk-secure-api
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


An unofficial `AWS CDK v2`_ Construct Library for Secure REST APIs.

* Documentation: https://aws-cdk-secure-api.readthedocs.io.

.. _`AWS CDK v2`: https://aws.amazon.com/about-aws/whats-new/2021/12/aws-cloud-development-kit-cdk-generally-available/

Install
-------

.. code-block:: console

    pip install aws-cdk-secure-api

Constructs
----------

* ``SecureRestApi`` - A construct to create a (public) REST API secured behind an API key, which needs to be
  specified in the ``x-api-key`` header for all requests.

* ``IAMSecureRestApi`` - A construct to create a (public) REST API secured behind `AWS IAM authentication`_, which
  requires IAM credentials `to be signed`_ and included in all requests.

.. _to be signed: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-access-control-iam.html

Features
--------

* A CDK Construct which sets up a `RestApi`_ secured behind (one of):

  * API key

    * An API key is `auto-generated`_ and stored in SSM Parameter Store (which is
      a free service) as needed.

    * Local cache for the API key, so that API calls are not needed in future
      CDK deployments.

  * `AWS IAM authentication`_

    * An IAM User (and Policy/Role) is created with minimal permissions to call / invoke the API.

    * The IAM User Credentials (Access Keys) are stored in AWS Secrets Manager.

* Helper methods for all constructs, such as ``add_resource_and_lambda_methods``, to make it easier to
  integrate a method for an AWS Lambda function for example.

.. _`RestApi`: https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_apigateway.RestApi.html
.. _`auto-generated`: https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetRandomPassword.html

Usage
-----

The ``SecureRestApi`` construct represents a Secure REST API in Amazon API Gateway.

    Use ``add_resource``, ``add_lambda_methods``, and ``add_methods`` to
    configure the API model, as shown below.

**Using a root resource**:

.. code:: python3

    from aws_cdk.aws_apigateway import StageOptions
    from aws_cdk.aws_lambda import Function, Runtime

    from aws_cdk_secure_api import Http, SecureRestApi

    # noinspection PyTypeChecker
    py_runtime: Runtime = Runtime.PYTHON_3_10

    get_handler = Function(self, 'lambda1', runtime=py_runtime, ...)
    put_handler = Function(self, 'lambda2', runtime=py_runtime, ...)

    api = SecureRestApi(
        self, 'api',
        rest_api_name='My Secure Service',
        # optional: specify a deployment stage
        deploy_options=StageOptions(stage_name='dev')
    )

    api.add_lambda_methods(get_handler, 'GET')  # GET /
    api.add_lambda_methods(put_handler, Http.PUT, Http.POST)  # PUT /, POST /

**Using a custom-named resource**:

    Replace above usage of ``add_lambda_methods`` with
    ``add_resource_and_lambda_methods``, as shown below.

.. code:: python3

    # GET /path1
    api.add_resource_and_lambda_methods(get_handler, '/path1', 'GET')
    # PUT /path2, POST /path2
    api.add_resource_and_lambda_methods(put_handler, '/path2', Http.PUT, Http.POST)

The ``IAMSecureRestApi`` construct represents a Secure REST API in Amazon API Gateway,
which requires IAM Authorization.

**Using a custom-named resource**:

.. code:: python3

    from aws_cdk.aws_apigateway import StageOptions
    from aws_cdk.aws_lambda import Function, Runtime

    from aws_cdk_secure_api import Http, IAMConfig, IAMSecureRestApi

    # noinspection PyTypeChecker
    py_runtime: Runtime = Runtime.PYTHON_3_10

    get_handler = Function(self, 'lambda1', runtime=py_runtime, ...)
    put_handler = Function(self, 'lambda2', runtime=py_runtime, ...)

    api = IAMSecureRestApi(
        self, 'api',
        rest_api_name='My IAM Secure Service',
        # optional: specify the name of secret to store IAM User Credentials
        config=IAMConfig(secret_name='my-stack/iam-user-access-keys'),
        # optional: specify a deployment stage
        deploy_options=StageOptions(stage_name='dev')
    )

    # GET /path1
    api.add_resource_and_lambda_methods(get_handler, '/path1', 'GET')
    # PUT /path2, POST /path2
    api.add_resource_and_lambda_methods(put_handler, '/path2', Http.PUT, Http.POST)

To use an IAM Role instead of attaching a Policy directly to User:

.. code:: python3

    IAMConfig(use_role=True)

AWS Profile
-----------

Note that if you normally pass the ``--profile`` to the ``cdk`` tool, for example such as::

    cdk deploy --profile my-aws-profile

The CDK construct won't be able to detect the AWS profile in this particular case.
A few workarounds can be used for this:

1. The environment variable ``AWS_PROFILE`` can be set before calling the ``cdk`` tool.
2. The ``profile`` attribute can be passed in to the ``config`` parameter for ``SecureRestApi``.
3. The ``profile`` context variable can be passed in to the ``cdk`` tool,
   as shown below::

       cdk deploy --profile my-profile -c profile=my-profile

API Keys
--------

Here is the process that the CDK construct uses for generating
or using an API key for a REST API.

1. First, it tries to read the API key from local cache, which is located in your
   home directory, under ``~/.cdk/cache/apigw_api_keys.json``.
2. If an API key is found, then it proceeds to use the cached key value, and *does not*
   perform the following steps.
3. An API call is made to read the key from AWS SSM Parameter Store. The param
   name is ``/{STACK NAME}/api-key``, where ``{STACK NAME}`` is the name of the CDK stack.
4. If the parameter does not exist, an random API key value is auto-generated, and a new
   SSM Parameter is created in the same AWS account and region that the CDK stack is deployed to.
5. The API key value is then cached on the local drive, under the ``~/.cdk/cache`` folder.

Stack Outputs
-------------

The following *stack outputs* will additionally be added to the CDK stack:

* ``APIEndpoint`` - The base endpoint of the Secure REST API.

  * *Note:* this output will not show up if ``override_endpoint_name`` is disabled
    in the ``config`` parameter.

* ``APIKey`` - The API key for the endpoint, which needs to be specified
  as a value in an HTTP request's ``x-api-key`` header.

* ``APIIAMUserCredentials`` - The URL link (to input in a browser) for the Secret
  stored in AWS Secrets Manager containing the AWS IAM Credentials for invoking the REST API.

* ``APIIAMRoleARN`` - The ARN of the IAM Role, used in an `AssumeRole`_ API call with the IAM User credentials.

.. _`AssumeRole`: https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html

Credits
-------

This package was created with Cookiecutter_ and the `rnag/cookiecutter-pypackage`_ project template.

.. _AWS IAM authentication: https://repost.aws/knowledge-center/iam-authentication-api-gateway
.. _Cookiecutter: https://github.com/cookiecutter/cookiecutter
.. _`rnag/cookiecutter-pypackage`: https://github.com/rnag/cookiecutter-pypackage
