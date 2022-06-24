from .client_cache import ClientCache


class SecretsManager(ClientCache):
    """
    Provides an interface to access AWS Secrets Manager
    """

    SERVICE_NAME = 'secretsmanager'

    def generate_api_key(self, length: int = 32,
                         exclude_chars=' ^,%+~`#$&*()|[]{}:;<>?!\'/@"\\'):
        """
        Generates a random API key value of a specified length.

        :param length: The length of the API key. If you don't
          include this parameter, the default length is 32 characters.
        :param exclude_chars: The characters to exclude in the generated
          password.

        """
        res = self.client.get_random_password(
            PasswordLength=length,
            ExcludeCharacters=exclude_chars,
        )

        return res['RandomPassword']
