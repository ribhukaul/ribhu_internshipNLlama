import json
from RequestContext import RequestContext
from ExtractionHandler import ExtractionHandler
from AWSInteraction.EnvVarSetter import EnvVarSetter

""" 
aws configure sso
For local testing needs to add the following environment variables to the config file
at AWSInteraction\config.json:
    - "S3_BUCKET": "dde-dev-working-671256662822-eu-south-1"
    - "SECRET_MANAGER_SUFFIX": "-llm-secret
    - "SECRET_MANAGER_PREFIX": "dde/dev/"
    - "REGION": "eu-south-1"
    - "AWS_PROFILE": "appicativo" (yoour profile name, to create your SSO profile follow 
    https://docs.aws.amazon.com/cli/latest/userguide/sso-configure-profile-token.html#sso-configure-profile-token-auto-sso)

For parallel execution:
https://aws.amazon.com/blogs/compute/parallel-processing-in-python-with-aws-lambda/
"""

# TODO: CODE TO ELIMINATE OLDER FILE FROM /TMP
def lambda_handler(event, context):
    print("RICEVUTO RICHIESTA: ", event)
    requestContext = RequestContext(event)

    env_setter = EnvVarSetter(requestContext.payload)
    USE_LOCAL_KEYS = False # True if you want to use local keys
    env_setter.configure_lambda_env_vars(use_local_keys=USE_LOCAL_KEYS)

    try:
        extraction_handler = ExtractionHandler(requestContext)
        extraction_handler.runallfiles()
        extracted_data = extraction_handler.extractions
        extracted_data_json = json.dumps(extracted_data)
    ## MOCKUP OUTPUT
    #     with open('mock_output.json', 'r') as f:
    #         extracted_data_json = f.read()

        return {
            'statusCode': 200,
            'extraction': extracted_data_json
        }
    except Exception as error:
            print(error)
            return {
                'statusCode': 404,
                'extraction': json.dumps({'error': repr(error)})
            }


# if __name__ == '__main__':
#    import os
#    os.environ['ENV'] = 'local'
#    event = {
#        "body": "{\r\n  \"files\": [\"basepfts/workspaces/test severini/AXA WF Global Factors - Sustainable Equity (LU0943665348).pdf\" ], \"TENANT\": \"insurance\", \"extractor_type\": \"kid\"\r\n}"}
#    x = lambda_handler(event, None)
#    print(x)

    