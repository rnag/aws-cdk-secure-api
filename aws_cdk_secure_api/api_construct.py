"""AWS CDK Construct module."""
from __future__ import annotations

import os

from aws_cdk import (
    CfnResource,
    CfnOutput,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
)
from constructs import Construct

from .aws import SecretsManager, SSM
from .cache import APIKeyCache
from .models import Config, Http


class SecureRestApi(apigateway.RestApi):
    """Represents a Secure REST API in Amazon API Gateway.

    By default, methods in the REST API requires an ``x-api-key`` header in
    the request.

    The API key value is also populated in the CFn *stack outputs* by default,
    and shows up under the ``APIKey`` name.

    Use ``add_resource``, ``add_lambda_methods``, and ``add_methods`` to
    configure the API model.

    By default, the API will automatically be deployed and accessible from a
    public endpoint.

    Example::

        >>> state_machine = stepfunctions.StateMachine(self, "MyStateMachine",
        ...     state_machine_type=stepfunctions.StateMachineType.EXPRESS,
        ...     definition=stepfunctions.Chain.start(stepfunctions.Pass(self, "Pass"))
        >>> )

        >>> api = aws_cdk_secure_api.SecureRestApi(self, "Api",
        ...           rest_api_name="MyApi"
        ...       )
        >>> api.add_methods(apigateway.StepFunctionsIntegration.start_execution(state_machine),
        ...                 "GET", "PUT")

    """

    def __init__(self, scope: Construct, construct_id: str,
                 config: Config | None = None, **kwargs) -> None:

        super().__init__(scope, construct_id, **kwargs)

        if config is None:
            config = Config(region=self.env.region)

        elif config.region is None:
            config.region = self.env.region

        stack_name = self.stack.stack_name

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
                apigateway.UsagePlanPerApiStage(
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

    def add_lambda_methods(self, handler: lambda_.IFunction,
                           *methods: Http | str):
        """
        Adds a lambda function the API Gateway, and associates it with one or
        more HTTP method(s).

        Example::

            >>> from aws_cdk_secure_api import SecureRestApi
            >>> from aws_cdk import (aws_apigateway as apigw, aws_lambda as lambda_)
            >>> api = SecureRestApi(self, 'api', rest_api_name='My Secure Service')
            >>> handler1 = lambda_.Function(self, 'lambda1', runtime=lambda_.Runtime.PYTHON_3_9, ...)
            >>> handler2 = lambda_.Function(self, 'lambda2', runtime=lambda_.Runtime.PYTHON_3_9, ...)
            >>> api.add_lambda_methods(handler1, 'GET')
            >>> api.add_lambda_methods(handler2, 'PUT', 'POST')

        """
        lambda_integration = apigateway.LambdaIntegration(
            handler,
            request_templates={'application/json': '{ "statusCode": "200" }'}
        )

        self.add_methods(lambda_integration, *methods)

    def add_methods(self, target: apigateway.Integration,
                    *methods: Http | str):
        """
        Adds one or more HTTP method(s) and a target (typically a
        `LambdaIntegration`) to the API root resource.

        By default, an API key is required for the new method(s).

        Example::

            >>> from aws_cdk_secure_api import SecureRestApi
            >>> from aws_cdk import (aws_apigateway as apigw, aws_lambda as lambda_)
            >>> api = SecureRestApi(self, 'api', rest_api_name='My Secure Service')
            >>> handler = lambda_.Function(self, 'my-function', runtime=lambda_.Runtime.PYTHON_3_9, ...)
            >>> integration = apigw.LambdaIntegration(
            ...   handler, request_templates={'application/json': '{ "statusCode": "200" }'}
            ... )
            >>> api.add_methods(integration, 'GET', 'POST')

        """
        if not methods:
            raise Exception('At least one HTTP method is required.')

        for method in methods:
            http_meth: str = getattr(method, 'name', method)

            self.root.add_method(
                http_meth, target,
                api_key_required=True
            )
