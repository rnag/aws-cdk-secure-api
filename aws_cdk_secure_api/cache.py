from __future__ import annotations

import json
from pathlib import Path

from aws_cdk import aws_apigateway as apigateway


_cache_dir = Path('~/.cdk/cache').expanduser()
_cache_dir.mkdir(parents=True, exist_ok=True)

_cache = _cache_dir / 'apigw_api_keys.json'

try:
    with _cache.open() as in_file:
        _keys = json.load(in_file)

except FileNotFoundError:
    _keys = {}


class APIKeyCache:

    __slots__ = (
        '_account',
        '_stack_name',
    )

    def __init__(self, construct: apigateway.IRestApi):
        self._account = construct.env.account
        self._stack_name = construct.stack.stack_name

    def get_api_key(self) -> str | None:
        """Retrieve the cached API key value for the stack's construct."""
        try:
            return _keys[self._account][self._stack_name]
        except KeyError:
            return None

    def save_api_key(self, api_key: str):
        """Store (cache) the API key value for the stack's construct."""
        _keys.setdefault(self._account, {})[self._stack_name] = api_key

        with _cache.open('w') as out_file:
            json.dump(_keys, out_file)
