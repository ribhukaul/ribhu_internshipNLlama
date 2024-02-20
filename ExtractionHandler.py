import os
import time
import json
import threading

from AWSInteraction.S3Handler import S3ExtractionHandler
from extractors.general_extractors.custom_extractors.kid.insurance.kid_extractor import InsuranceKidExtractor
from extractors.general_extractors.custom_extractors.kid.insurance.gkid_extractor import InsuranceGKidExtractor
# TODO: 
# - multiple files in one folder

# TODO: DOCSTRING
class ThreadedFunction(threading.Thread):
    def __init__(self, function, *args):
        threading.Thread.__init__(self)
        self.function = function
        self.args = args
        self.result = None
        self.total_runtime= None
        

    def run(self):
        # time counter
        start_time = time.time()
        extractor = self.function(*self.args)
        self.result = extractor.process()
        self.total_runtime = time.time() - start_time


class ExtractionHandler:

    # Switch case for custom extraction based on: -tenant -extraction type
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
        self.local_saved_files = {} # filekey: local_path


    def runallfiles(self, parallel=True):

        files_list = self.requestContext.payload['files']
        print("working_files:", files_list)
        for file_key in files_list:
            s3handler = S3ExtractionHandler(self.requestContext, file_key)
            file = s3handler.route(download=True)
            if file['statusCode'] == 200:
                file_path = file['body']
                self.local_saved_files[file_key] = file_path
                print(file_path)
                #@ELIA TO ASK
                if not parallel:
                    # Run extraction
                    self.extractions[file_key] = self.run_async_function(file_path, self.extactor)

            else:
                self.extractions[file_path]= {'error': 'file not found'}
        if parallel:

            threads = {}
            for file_key, file_path in self.local_saved_files.items():
                thread = ThreadedFunction(self.extactor, file_path)
                threads[file_key] = thread
                thread.start()
            
            for _, thread in threads.items():
                thread.join()
            
            for file_key, thread in threads.items():
                # result to dict
                dict_result = json.loads(thread.result)
                dict_result['extraction_time'] = thread.total_runtime
                self.extractions[file_key] = json.dumps(thread.result)

        
        self.delete_local_files()
        
        return self.extractions
                
    def run_piped_function(self, conn, file, function, *args):
        doc_extractor = function(file, *args)
        conn.send(doc_extractor.process())
        conn.close()

        #return await doc_extractor.process()
    
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
        
        for file in self.local_saved_files.values():
            try:
                os.remove(file)
            except Exception as error:
                print("Could not delete file{} for error:{}".format(file, repr(error)))
                continue
    
