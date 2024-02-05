import boto3
import os

class AWSResourceBuilder:
    
    
    @staticmethod
    def get_s3_client(sessionContext=''):
        #if 'accesskey' in sessionContext: aws sso login --profile jacopo

        is_local = os.getenv('LOCAL')
        if is_local is None:
            session = boto3.Session()
        
        else:
            session = boto3.Session(profile_name='jacopoaws')


        # session = boto3.Session(
        #     profile_name='jacopo',
        #     region_name='eu-south-1',)
            
        # session = boto3.Session(
        #         aws_access_key_id=sessionContext['accesskey'],
        #         aws_secret_access_key=sessionContext['secretkey'],
        #         
        #         aws_session_token=sessionContext.get('sessiontoken')
        #     )
        s3 = session.client('s3')
        return s3
    
    @staticmethod
    def get_secret_manager_client(sessionContext=''):
        lambda_f = True
        if lambda_f:
            session = boto3.Session()
        # session = boto3.Session(
        #     profile_name='jacopo',
        #     region_name='eu-south-1',)
            
        # session = boto3.Session(
        #         aws_access_key_id=sessionContext['accesskey'],
        #         aws_secret_access_key=sessionContext['secretkey'],
        #         
        #         aws_session_token=sessionContext.get('sessiontoken')
        #     )
        sm = session.client('secretsmanager')
        return sm
    
    