"""
AWS CDK Secure API
~~~~~~~~~~~~~~~~~~

A CDK (v2) Construct Library for Secure Rest APIs

Sample Usage:

    >>> import aws_cdk_secure_api

For full documentation and more advanced usage, please see
<https://aws-cdk-secure-api.readthedocs.io>.

:copyright: (c) 2022 by Ritvik Nag.
:license:MIT, see LICENSE for more details.
"""

__all__ = [
    'Config',
    'Http',
    'IAMConfig',
    'IAMSecureRestApi',
    'SecureRestApi',
]

import logging

from .api_construct import IAMSecureRestApi, SecureRestApi
from .models import Config, Http, IAMConfig

# Set up logging to ``/dev/null`` like a library is supposed to.
# http://docs.python.org/3.3/howto/logging.html#configuring-logging-for-a-library
logging.getLogger('aws_cdk_secure_api').addHandler(logging.NullHandler())
