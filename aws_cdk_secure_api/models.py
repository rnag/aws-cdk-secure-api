from dataclasses import dataclass
from enum import Enum

from aws_cdk import aws_apigateway as apigateway


@dataclass
class Config:
    region: str | None = None
    profile: str | None = None
    """
    `key_id` - The Key Management Service (KMS) ID that you want to
    use to encrypt a parameter. Either the default KMS key automatically
    assigned to your AWS account or a custom key. Required for parameters
    that use the `SecureString` data type. If you don't specify a key ID,
    the system uses the default key associated with your AWS account.
    """
    key_id: str | None = None

    throttle: apigateway.ThrottleSettings = apigateway.ThrottleSettings(
        burst_limit=500,
        rate_limit=1000
    )

    quota: apigateway.QuotaSettings = apigateway.QuotaSettings(
        limit=10000000,
        period=apigateway.Period.MONTH
    )


class Http(Enum):
    """Enum class to represent an HTTP method."""
    OPTIONS = 'options'
    GET = 'get'
    HEAD = 'head'
    PUT = 'put'
    POST = 'post'
    DELETE = 'delete'
    PATCH = 'patch'
