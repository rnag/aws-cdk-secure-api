from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from aws_cdk import aws_apigateway as apigateway


@dataclass
class Config:
    # AWS Region Name, ex. `us-east-1`
    region: str | None = None

    # AWS Profile Name, ex. `my-aws-profile`
    profile: str | None = None

    # `key_id` - The Key Management Service (KMS) ID that you want to
    # use to encrypt a parameter. Either the default KMS key automatically
    # assigned to your AWS account or a custom key. Required for parameters
    # that use the `SecureString` data type.
    #
    # If you don't specify a key ID, the system uses the default key
    # associated with your AWS account.
    key_id: str | None = None

    # Whether to override the CDK stack output name for the API endpoint.
    # Defaults to `True` if not specified.
    override_endpoint_name = True

    # Throttle settings to associate with the Usage Plan for the REST API
    throttle: apigateway.ThrottleSettings = field(
        default_factory=lambda: apigateway.ThrottleSettings(
            burst_limit=500,
            rate_limit=1000,
        ),
    )

    # Quota settings to associate with the Usage Plan for the REST API
    quota: apigateway.QuotaSettings = field(
        default_factory=lambda: apigateway.QuotaSettings(
            limit=10000000,
            period=apigateway.Period.MONTH,
        ),
    )


@dataclass
class IAMConfig(Config):
    # secret name to hold the IAM User Credentials (Access Keys) for
    # invoking the Rest API.
    secret_name: str | None = None

    # set up an IAM Role that can be assumed by the IAM User via
    # the `sts:AssumeRole` API, instead of attaching an IAM Policy
    # to the User
    use_role: bool = False


# noinspection PyArgumentList
class Http(Enum):
    """Enum class to represent an HTTP method."""
    OPTIONS = auto()
    GET = auto()
    HEAD = auto()
    PUT = auto()
    POST = auto()
    DELETE = auto()
    PATCH = auto()
