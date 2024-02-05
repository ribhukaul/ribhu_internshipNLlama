import json
import os
import traceback
import uuid

from AWSInteraction.AWSResourceBuilder import AWSResourceBuilder

BODY_KEY = 'body'
STATUS_CODE_KEY = 'statusCode'


class S3ExtractionHandler:

    download_folder = '/tmp'

    def __init__(self, requestContext, file_key, bucket=None) -> None:
        self.requestContext = requestContext
        self.file_key = file_key
        if bucket is None:
            self.bucket = os.getenv('S3_BUCKET')
        else:
            self.bucket = bucket
        self.s3 = AWSResourceBuilder.get_s3_client()
    
    def route(self, download=False):
        
        if download:
            file_name = str(uuid.uuid4()) +'.pdf'
            download_path = os.path.join(self.download_folder, file_name)
            download_response = self.download(self.file_key, download_path)
            return download_response

        #if True:#requestContext.path == DWM_CONFIGURATIONS_BLOB_READ_PATH:
        return self.read()
        
    def read(self):
        s3_object = self.s3.Object(
            bucket_name=self.bucket,
            key=self.file_key)
        
        try:
            return {STATUS_CODE_KEY: 200, BODY_KEY: s3_object.get()['Body'].read()}#.decode('UTF-8')}
        except Exception as error:
            print(error)
            traceback.print_exc()
            return {STATUS_CODE_KEY: 404, BODY_KEY: json.dumps({'message': 'file not found'})}
    
    def download(self, file_key, download_path):
        
        try:
            self.s3.download_file(self.bucket, file_key, download_path)
            return {STATUS_CODE_KEY: 200, BODY_KEY: download_path}
        except Exception as error:
            print(error)
            traceback.print_exc()
            return {STATUS_CODE_KEY: 404, BODY_KEY: json.dumps({'message': 'file not found'})}

    # def write(self, requestContext):
    #     s3_object = self.s3.Object(
    #         bucket_name=self.bucket,
    #         key='{0}/{1}'.format(requestContext.tenant, requestContext.payload['key'])
    #     )
    #     s3_object.put(Body=json.dumps(requestContext.payload["data"]))
    #     return {STATUS_CODE_KEY: 200, BODY_KEY: "{}"}
    
