import json
import asyncio
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
    - "ENV":"local"

For parallel execution:
https://aws.amazon.com/blogs/compute/parallel-processing-in-python-with-aws-lambda/
"""
# TODO: CODE TO ELIMINATE OLDER FILE FROM /TMP
def lambda_handler(event, context):
    print("RICEVUTO RICHIESTA: ", event)
    requestContext = RequestContext(event)

    env_setter = EnvVarSetter(requestContext.payload)
    env_setter.set_all_env_vars()

    try:
        extraction_handler = ExtractionHandler(requestContext)
        # loop = asyncio.get_event_loop()  
        # loop.run_until_complete(extraction_handler.runallfiles())

        # asyncio.run(extraction_handler.runallfiles())#parallel=True, max_workers=8)
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
#    event = {"body": "{\r\n  \"files\": [\"basepfts/workspaces/test severini/BlackRock Global Funds - World Healthscience Fund (LU1960219571).pdf\", \"basepfts/workspaces/test severini/AXA WF Framlington Sustainable Europe (LU0389656389).pdf\" ], \"TENANT\": \"insurance\", \"extractor_type\": \"kid\"\r\n}"}
#    x = lambda_handler(event, None)
#    print(x)

    