"""Tests for `aws_cdk_secure_api` package."""

import pytest


from aws_cdk_secure_api import SecureRestApi


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_create_api(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # TODO
    SecureRestApi
