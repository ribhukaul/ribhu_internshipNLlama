import os
from concurrent.futures import ProcessPoolExecutor
from AWSInteraction.EnvVarSetter import EnvVarSetter
from extractors.general_extractors.custom_extractors.certificates.issuers.BNP_extractor import BNPDerivatiKidExtractor
from extractors.general_extractors.custom_extractors.kid.insurance.kid_extractor import InsuranceKidExtractor
from extractors.general_extractors.custom_extractors.kid.insurance.gkid_extractor import InsuranceGKidExtractor
from extractors.general_extractors.custom_extractors.certificates.issuers.Leonteq_extractor import (
    LeonteqDerivatiKidExtractor,
)

# from extractors.Derivati.Spot_KID_extractor import write_info
# from extractors.Derivati.Global_KID_extractor import GlobalExtractor
from extractors.models import Models
import glob
import logging
import asyncio
import pandas as pd
from functools import partial

logging.basicConfig(filename="logging.log", encoding="utf-8", level=logging.DEBUG)


def process_file(file_path, file_type):
    """instanciate a KidExtractor and process the file

    Args:
        file_path (str): path of pdf file to process

    Returns:
        dict(filename,dict()): dictionary containing the results for the file
    """
    try:
        match file_type:
            case "kid":
                kid_extractor = InsuranceKidExtractor(file_path)
                return asyncio.run(kid_extractor.process())
            case "g-kid":
                gkid_extractor = InsuranceGKidExtractor(file_path)
                return asyncio.run(gkid_extractor.process())
            case "leonteq":
                derivati_extraction = LeonteqDerivatiKidExtractor(file_path)
                return asyncio.run(derivati_extraction.process())
            case "bnp":
                derivati_extraction = BNPDerivatiKidExtractor(file_path)
                return asyncio.run(derivati_extraction.process())
            case _:
                raise ValueError("type not supported")
    except Exception as error:
        print("ERROR: {}".format(file_path) + repr(error))
        filename = os.path.splitext(os.path.basename(file_path))[0]
        return [dict((filename, dict()))]


def main(doc_folder):
    """main loop, instanciate 10 async process(more causes errors) for 10 files at the time,
    puts results in an excel file

    Args:
        doc_folder (str): folder containing the pdf files
    """
    try:
        env_setter = EnvVarSetter(tenant="insurance")
        env_setter.set_locally_saved_env_vars()
        # testing
        file_type = "bnp"
        all_files = []
        # list all the pdf files in the folder
        print("START")
        all_files = glob.glob(os.path.join(doc_folder, "**\\*.pdf"), recursive=True)
        results = {}

        partial_process_file = partial(process_file, file_type=file_type)
        # async processing of the files
        with ProcessPoolExecutor(max_workers=1) as executor:
            results = executor.map(partial_process_file, all_files)

        # give request id
        Models.clear_resources_group(str(-1))
        # orders results
        # results = pd.DataFrame(results)
        # ordered = [col for col in column_order[file_type] if col in results.columns]
        # results = results[ordered]
        # excel_path = os.path.join(doc_folder + '.xlsx')
        # saves results
        # results.to_excel(excel_path, header=True, index=False)
        print(results)

    except Exception as error:
        print("top level error:" + repr(error))


if __name__ == "__main__":
    folder = "kid\\documents\\testdoc\\BNP\\bonus cap mini future"

    for root, dirs, files in os.walk(folder):
        # Check if there are PDF files in the current directory
        if any(file.endswith(".pdf") for file in files):
            # Call your existing function to process PDFs in the folder
            main(root)

    # main(folder)
