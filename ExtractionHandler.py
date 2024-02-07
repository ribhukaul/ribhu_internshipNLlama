import asyncio
import os
import time
from functools import partial
from concurrent.futures import ProcessPoolExecutor

from AWSInteraction.S3Handler import S3ExtractionHandler
from extractors.general_extractors.custom_extractors.kid.insurance.kid_extractor import InsuranceKidExtractor
from extractors.general_extractors.custom_extractors.kid.insurance.gkid_extractor import InsuranceGKidExtractor
# TODO: 
# - multiple files in one folder

class ExtractionHandler:

    # Switch case to select correct custom extraction based on:
    # - tenant
    # - extraction type
    custom_extractors = {
        'insurance': {
            'kid': InsuranceKidExtractor,
            'gkid': InsuranceGKidExtractor
        },
        'certifictes': {'certificates': ''},
        'funds': {'peergroup': ''},
        'bonds': {'bloombergss': '',
                  'prospetti': ''}
    }

    def __init__(self, requestContext) -> None:
        self.requestContext = requestContext
        self.tenant = requestContext.payload['TENANT']
        self.extractor_type = requestContext.payload['extractor_type']
        self.extactor = self.custom_extractors[self.tenant][self.extractor_type]
        self.extractions = {}
        self.local_saved_files = {}


    def run(self, parallel=False, max_workers=7):

        files_list = self.requestContext.payload['files']

        for file_key in files_list:
            s3handler = S3ExtractionHandler(self.requestContext, file_key)
            file = s3handler.route(download=True)
            if file['statusCode'] == 200:
                file_path = file['body']
                self.local_saved_files[file_path] = file_path
                print(file_path)
                if not parallel:
                    # Run extraction
                    self.extractions[file_path] = self.run_async_function(file_path, self.extactor)
            else:
                self.extractions[file_path]= {'error': 'file not found'}
        if parallel:
            # async processing of the files
            partial_run_async_func = partial(self.run_async_function, function=self.extactor)

            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                results = executor.map(partial_run_async_func, self.local_saved_files.values())
        

            # NEED TO CHANGE THE OUTPUT
            # # # # # # to review
            # # # # # for file, result in zip(self.local_saved_files.values(), results):
            # # # # #     self.extractions[file]= result

        self.delete_local_files()
        
        return self.extractions
                
    def run_async_function(self, file, function, *args):
        doc_extractor = function(file, *args)
        return asyncio.run(doc_extractor.process())
    
    def delete_local_files(self):
        """
        Delete all the files that have been downloaded locally. The files are
        deleter after 30 minutes from the download or if they have been already
        processed in the current run.
        """
        # current_time = time.time()

        # # lis
        # refernece_folder = "/tmp"
        # if os.getenv('ENV') == 'local':
        #     refernece_folder = "tmp"

        # list_all_files = os.listdir(refernece_folder)
        
        for file in self.local_saved_files:
            try:
                os.remove(file)
            except Exception as error:
                print("Could not delete file{} for error:{}".format(file, repr(error)))
                continue
    
