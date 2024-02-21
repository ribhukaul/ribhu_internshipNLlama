import os
import time
import json
import threading

from AWSInteraction.S3Handler import S3ExtractionHandler
from extractors.general_extractors.custom_extractors.kid.insurance.kid_extractor import InsuranceKidExtractor
from extractors.general_extractors.custom_extractors.kid.insurance.gkid_extractor import InsuranceGKidExtractor
# TODO: 
# - multiple files in one folder
# - DOCSTRING
# - LIST OF OBJECT INSTEAD OF list of files
# - change parallel to parallelize the download of the files
class ThreadedFunction(threading.Thread):
    """
    Create a thread to run a function in parallel with other threads.
    """
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

    def __init__(self, request_context) -> None:
        self.request_context = request_context
        self.tenant = request_context.payload['TENANT']
        self.extractor_type = request_context.payload['extractor_type']
        self.extactor = self.custom_extractors[self.tenant][self.extractor_type]
        self.extractions = {}
        self.local_saved_files = {} # filekey: local_path


    def runallfiles(self, parallel=True):

        files_list = self.request_context.payload['files']
        print("working_files:", files_list)
        for file_key in files_list:
            s3handler = S3ExtractionHandler(self.request_context, file_key)
            file = s3handler.route(download=True)
            if file['statusCode'] == 200:
                file_path = file['body']
                self.local_saved_files[file_key] = file_path
                print(file_path)
                #@ELIA TO ASK
                if not parallel:
                    # Run extraction
                    self.extractions[file_key] = self.extactor(file_path).process()

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
                dict_result = json.loads(thread.result)
                dict_result['extraction_time'] = thread.total_runtime
                self.extractions[file_key] = json.dumps(thread.result)
        
        self.delete_local_files()
        
        return self.extractions
    
    def delete_local_files(self):
        """ 
        Delete all the files that have been downloaded locally.
        """
        for file in self.local_saved_files.values():
            try:
                os.remove(file)
            except Exception as error:
                print("Could not delete file{} for error:{}".format(file, repr(error)))
                continue
    
