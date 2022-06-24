from __future__ import annotations

import logging

from .client_cache import ClientCache


LOG = logging.getLogger('ssm')
LOG.setLevel('DEBUG')


class SSM(ClientCache):
    """
    Provides an interface to access AWS SSM Parameter Store
    """

    SERVICE_NAME = 'ssm'

    def get_param(self, name: str, with_decryption=True) -> str | None:
        """
        Get a parameter from SSM Parameter Store. Returns `None` if the
        parameter does not exist.

        Example::

        >>> from aws_cdk_secure_api.aws import SSM
        >>> ssm = SSM()
        >>> ssm.get_param('/Prod/Db/Password')

        :param name: The SSM parameter name to retrieve.
        :param with_decryption: True to decrypt a (secure string) parameter.
        :return: The decrypted parameter value, as a string.

        """
        try:
            parameter = self.client.get_parameter(
                Name=name,
                WithDecryption=with_decryption,
            )['Parameter']

            value = parameter['Value']

            if parameter['Type'] == 'StringList':
                value = value.split(',')

            return value

        except self.client.exceptions.ParameterNotFound:
            LOG.warning('Parameter `%s` does not exist in the AWS account.', name)
            return None

    def put_param(self, name: str,
                  value: str,
                  description: str | None = None,
                  type='SecureString',
                  key_id: str | None = None,
                  tier='Standard',
                  data_type='text',
                  overwrite=False) -> str:
        """
        Create/update a parameter in SSM Parameter Store.

        Example::

        >>> from aws_cdk_secure_api.aws import SSM
        >>> ssm = SSM()
        >>> ssm.put_param('/Prod/Db/Password', 'my-value')

        :param name: The fully qualified name of the parameter to store. The
          fully qualified name usually includes the complete hierarchy of the
          parameter path and name.
        :param value: specifies the parameter value. Standard parameters have
          a value limit of 4 KB, whereas Advanced parameters have a value
          limit of 8 KB.
        :param description: Specifies additional information about the
          parameter.
        :param type: The Parameter type. Must be one of
          [String, StringList, SecureString]. Defaults to `SecureString` if
          not specified.
        :param key_id: The Key Management Service (KMS) ID that you want to
          use to encrypt a parameter. Either the default KMS key automatically
          assigned to your AWS account or a custom key. Required for parameters
          that use the `SecureString` data type. If you don't specify a key ID,
          the system uses the default key associated with your AWS account.
        :param tier: Must be one of [Standard, Advanced, Intelligent-Tiering].
          Defaults to `Standard` if not specified.
        :param data_type: The data type for a String parameter. Must be one of
          [text, aws:ec2:image]. Defaults to `text` if not specified.
        :param overwrite: Used to overwrite a current parameter value. The
          default value is `False`.

        """
        kwargs = {}
        if description:
            kwargs['Description'] = description
        if key_id:
            kwargs['KeyId'] = key_id

        new_string_parameter = self.client.put_parameter(
            Name=name,
            Value=value,
            Type=type,
            Overwrite=overwrite,
            Tier=tier,
            DataType=data_type,
            **kwargs,
        )

        LOG.debug(
            'String Parameter created with version %s and Tier %s',
            new_string_parameter['Version'],
            new_string_parameter['Tier'],
        )

        return new_string_parameter
