"""AWS CDK Construct module."""
from __future__ import annotations

import os

from aws_cdk import (
    CfnResource,
    CfnOutput,
)
from aws_cdk.aws_apigateway import (
    IResource,
    Integration,
    LambdaIntegration,
    RestApi,
    UsagePlanPerApiStage,
)
from aws_cdk.aws_lambda import IFunction
from constructs import Construct

from .aws import SecretsManager, SSM
from .cache import APIKeyCache
from .models import Config, Http


class SecureRestApi(RestApi):
    """Represents a Secure REST API in Amazon API Gateway.

    By default, methods in the REST API requires an ``x-api-key`` header in
    the request.

    The API key value is also populated in the CFn *stack outputs* by default,
    and shows up under the ``APIKey`` name.

    Use ``add_resource``, ``add_lambda_methods``, and ``add_methods`` to
    configure the API model.

    By default, the API will automatically be deployed and accessible from a
    public endpoint.

    If ``test`` is enabled, then a live API call to AWS SSM (Parameter Store)
    won't be performed on an initial run, and instead a dummy API key value
    is used.

    Example::

        >>> from aws_cdk_secure_api import SecureRestApi
        >>> from aws_cdk.aws_apigateway import StepFunctionsIntegration
        >>> from aws_cdk.aws_stepfunctions import Chain, Pass, StateMachine, StateMachineType

        >>> state_machine = StateMachine(self, "MyStateMachine",
        ...     state_machine_type=StateMachineType.EXPRESS,
        ...     definition=Chain.start(Pass(self, "Pass"))
        >>> )
        >>> api = SecureRestApi(self, "Api",
        ...           rest_api_name="MyApi"
        ...       )
        >>> api.add_methods(StepFunctionsIntegration.start_execution(state_machine),
        ...                 "GET", "PUT")

    """

    def __init__(self, scope: Construct, construct_id: str,
                 config: Config | None = None,
                 test: bool = False,
                 **kwargs) -> None:

        super().__init__(scope, construct_id, **kwargs)

        if config is None:
            config = Config(region=self.env.region)

        elif config.region is None:
            config.region = self.env.region

        stack_name = self.stack.stack_name

        # True if a CDK stack is created for a local test case, for example
        if test:
            api_key_value: str = 'test123'

        else:  # else, continue as normal
            cache = APIKeyCache(self)
            api_key_value: str = cache.get_api_key()

            if api_key_value is None:
                aws_profile = (config.profile
                               or os.getenv('AWS_PROFILE')
                               or self.node.try_get_context('profile'))

                # Use SSM Parameter Store to store / retrieve the API Key, which will need
                # to be included in the 'x-api-key' header in requests to our endpoint.
                #
                # Refs:
                #   - https://docs.aws.amazon.com/cdk/latest/guide/get_ssm_value.html
                #   - https://bobbyhadz.com/blog/aws-cdk-ssm-parameters
                ssm = SSM(config.region, aws_profile)
                param_name = f'/{stack_name}/api-key'

                api_key_value: str = ssm.get_param(param_name)

                if api_key_value is None:
                    # Create the SSM Parameter, as it does not exist

                    # Generate the API key using `secretsmanager:GetRandomPassword`
                    sm = SecretsManager(config.region, aws_profile)
                    api_key_value = sm.generate_api_key(40)
                    # Create the new SSM Parameter (SecureString) with the
                    # auto-generated API key.
                    print(
                        f'[{param_name}] Creating new SSM Parameter...'
                    )
                    ssm.put_param(
                        param_name, api_key_value,
                        key_id=config.key_id,
                    )

                cache.save_api_key(api_key_value)

        # Create API key and add it to usage plan for the API Gateway
        #
        # Ref: https://dev.to/dvddpl/create-and-override-apikey-for-an-aws-gatewayapi-bjg
        api_key_id = f'{stack_name}-api-key'
        api_key = self.add_api_key(
            api_key_id,
            api_key_name=stack_name,
            value=api_key_value
        )
        # Create usage plan for the API
        usage_plan_name = f'{stack_name}-usage-plan'

        usage_plan = self.add_usage_plan(
            usage_plan_name,
            name=usage_plan_name,
            api_stages=[
                UsagePlanPerApiStage(
                    api=self,
                    stage=self.deployment_stage,
                ),
            ],
            throttle=config.throttle,
            quota=config.quota,
        )

        # Add API key to the Usage Plan
        usage_plan.add_api_key(api_key)

        # Stack Outputs #

        # This is needed so the CFN Output name correctly appears for the
        # API Endpoint, as this Output is automatically generated by CDK.
        #
        # Ref: https://github.com/aws/aws-cdk/issues/15664
        if config.override_endpoint_name:
            # noinspection PyTypeChecker
            res: CfnResource = self.node.try_find_child('Endpoint')
            res.override_logical_id('APIEndpoint')

        # Ensure the API Key shows up in the Stack Outputs
        CfnOutput(
            scope, 'APIKey',
            value=api_key_value,
            # Needs to be unique per account + region
            export_name=f'x-api-key:{stack_name}'
        )

    def add_resource_and_lambda_methods(self, handler: IFunction,
                                        resource_name: str,
                                        *methods: Http | str):
        """
        Adds a new resource -- at the `resource_name` path -- to the API Gateway.

        Also adds a lambda function the API Gateway, and associates it with one or
        more HTTP method(s), for the new resource.

        Example::

            >>> from aws_cdk_secure_api import SecureRestApi
            >>> from aws_cdk.aws_lambda import Function, Runtime
            >>> api = SecureRestApi(self, 'api', rest_api_name='My Secure Service')
            >>> handler1 = Function(self, 'lambda1', runtime=Runtime.PYTHON_3_10, ...)
            >>> handler2 = Function(self, 'lambda2', runtime=Runtime.PYTHON_3_10, ...)
            >>> api.add_resource_and_lambda_methods(handler1, '/path1', 'GET')
            >>> api.add_resource_and_lambda_methods(handler2, '/path2', 'PUT', 'POST')

        """
        resource = self.root.add_resource(resource_name.lstrip('/'))
        self.add_lambda_methods(handler, *methods, resource=resource)

    def add_lambda_methods(self, handler: IFunction,
                           *methods: Http | str,
                           resource: IResource | None = None,
                           ):
        """
        Adds a lambda function the API Gateway, and associates it with one or
        more HTTP method(s).

        The `resource` parameter determines which API resources to associate the
        HTTP method(s) with - if not passed, it defaults to the "root" resource
        for the API -- i.e. under the `/` path.

        Example::

            >>> from aws_cdk_secure_api import SecureRestApi
            >>> from aws_cdk.aws_lambda import Function, Runtime
            >>> api = SecureRestApi(self, 'api', rest_api_name='My Secure Service')
            >>> handler1 = Function(self, 'lambda1', runtime=Runtime.PYTHON_3_10, ...)
            >>> handler2 = Function(self, 'lambda2', runtime=Runtime.PYTHON_3_10, ...)
            >>> api.add_lambda_methods(handler1, 'GET')
            >>> api.add_lambda_methods(handler2, 'PUT', 'POST')

        Example with a Resource Path::

            >>> from aws_cdk_secure_api import SecureRestApi
            >>> from aws_cdk.aws_lambda import Function, Runtime
            >>> api = SecureRestApi(self, 'api', rest_api_name='My Secure Service')
            >>> handler1 = Function(self, 'lambda1', runtime=Runtime.PYTHON_3_10, ...)
            >>> handler2 = Function(self, 'lambda2', runtime=Runtime.PYTHON_3_10, ...)
            >>> my_resource = api.root.add_resource('my-path-here')
            >>> api.add_lambda_methods(handler1, 'GET', resource=my_resource)
            >>> api.add_lambda_methods(handler2, 'PUT', 'POST', resource=my_resource)

        """
        lambda_integration = LambdaIntegration(
            handler,
            request_templates={'application/json': '{ "statusCode": "200" }'}
        )

        self.add_methods(lambda_integration, *methods, resource=resource)

    def add_methods(self, target: Integration,
                    *methods: Http | str,
                    resource: IResource | None = None,
                    ):
        """
        Adds one or more HTTP method(s) and a target (typically a
        `LambdaIntegration`) to an API `resource` - which defaults
        to the API "root" resource.

        By default, an API key is required for the new method(s).

        Example::

            >>> from aws_cdk_secure_api import SecureRestApi
            >>> from aws_cdk.aws_apigateway import LambdaIntegration
            >>> from aws_cdk.aws_lambda import Function, Runtime
            >>> api = SecureRestApi(self, 'api', rest_api_name='My Secure Service')
            >>> handler = Function(self, 'my-function', runtime=Runtime.PYTHON_3_10, ...)
            >>> integration = LambdaIntegration(
            ...   handler, request_templates={'application/json': '{ "statusCode": "200" }'}
            ... )
            >>> api.add_methods(integration, 'GET', 'POST')

        Example with a Resource Path::

            >>> from aws_cdk_secure_api import SecureRestApi
            >>> from aws_cdk.aws_apigateway import LambdaIntegration
            >>> from aws_cdk.aws_lambda import Function, Runtime
            >>> api = SecureRestApi(self, 'api', rest_api_name='My Secure Service')
            >>> handler = Function(self, 'my-function', runtime=Runtime.PYTHON_3_10, ...)
            >>> integration = LambdaIntegration(
            ...   handler, request_templates={'application/json': '{ "statusCode": "200" }'}
            ... )
            >>> my_resource = api.root.add_resource('my-path-here')
            >>> api.add_methods(integration, 'GET', 'POST', resource=my_resource)

        """
        if not methods:
            raise Exception('At least one HTTP method is required.')

        for method in methods:
            http_meth: str = getattr(method, 'name', method)

            (resource or self.root).add_method(
                http_meth, target,
                api_key_required=True,
            )
