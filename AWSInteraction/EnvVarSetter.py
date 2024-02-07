import os
import json

from AWSInteraction.AWSSecretsHandler import SecretsManagerExtractionHandler
"""
TOO:
TEST THIS CLASS
"""


class EnvVarSetter():

    def __init__(self, payload) -> None:
        
        self.payload = payload
        self.tenant = payload['TENANT']


    def set_all_env_vars(self) -> None:
        """
        Set all the local and the secret env variables.
        """

        self.set_locally_saved_env_vars()
        self.set_aws_secret_manager_env_vars()


    def set_locally_saved_env_vars(self) -> None:
        """
        Set the environment variables that are saved locally in the config file.
        """

        # load config.json file and transform to dict
        with open('AWSInteraction//config.json') as json_file:
            data = json.load(json_file)
            tenant_variables = data[self.tenant]

            # Create env variables
            for key, value in tenant_variables.items():
                os.environ[key] = value


    def set_aws_secret_manager_env_vars(self) -> None:
        """
        Set the environment variables that are saved in AWS Secrets Manager.
        """

        sm_handler = SecretsManagerExtractionHandler()

        # Create secret name
        secret_suffix = os.environ["SECRET_MANAGER_SUFFIX"]
        secret_prefix = os.environ["SECRET_MANAGER_PREFIX"]
        secret_name = f"{secret_prefix}{self.tenant}{secret_suffix}"

        # Get secret
        secret = sm_handler.get_secret_value(secret_name, as_dict=True)

        # set the API keys
        for key, value in secret.items():
            os.environ[key] = value



if __name__ == "__main__":
    envVarSetter = EnvVarSetter()
    envVarSetter.set_locally_saved_env_vars()
    pass

