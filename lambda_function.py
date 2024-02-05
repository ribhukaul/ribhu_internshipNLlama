import json

from RequestContext import RequestContext
from ExtractionHandler import ExtractionHandler
from AWSInteraction.EnvVarSetter import EnvVarSetter


def lambda_handler(event, context):
    ####Temporary mockup
    # # # # # Handle context
    # # # requestContext = RequestContext(event)

    # # # env_setter = EnvVarSetter(requestContext.payload)
    # # # env_setter.set_locally_saved_env_vars()
    # # # # tWE CAN ONLY TEST THIS IN DEV ENV CAUS OF THE SECRETS
    # # # # env_setter.set_all_env_vars()

    # # # #try:
    # # # extraction_handler = ExtractionHandler(requestContext)
    # # # extraction_handler.run()
    # # # extracted_data = extraction_handler.extractions
    # # # extracted_data_json = json.dumps(extracted_data)
    # Load mock_output.json
    try:
        with open('mock_output.json', 'r') as f:
            extracted_data_json = f.read()
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


if __name__ == '__main__':
    event = {"body": "{\r\n  \"files\": [\"allianz.pdf\"], \"TENANT\": \"insurance\", \"extractor_type\": \"kid\"\r\n}"}
    x = lambda_handler(event, None)
    
    print(3)
    