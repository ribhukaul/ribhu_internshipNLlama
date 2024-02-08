

from extractors.general_extractors.custom_extractors.kid.kid_extractor import KidExtractor
from extractors.general_extractors.extractor import Extractor
from extractors.utils import is_in_text, search_in_pattern_in_text
from .certificates_config.cert_cleaning import header_mappings, regex_callable, check_for


class DerivatiKidExtractor(KidExtractor):
    
    def __init__(self, doc_path) -> None:
        self.doc_path = doc_path
        super().__init__(doc_path, "it")
        



    def extract_regex_text(self, type,page, boolean_to_check={}, str_to_check={}):
        """extracts the callable from the document
        looks if the word is in the document thats it

        Returns:
            dict(): dictionary containing the callable
        """
        try:
            text= getattr(self.text[page],"page_content", "").replace("\n", " ")
            for key in boolean_to_check.keys():
                boolean_to_check[key] = 1 if is_in_text(regex_callable[type][key], text) else 0
                
            for key in str_to_check.keys():
                found=search_in_pattern_in_text(regex_callable[type][key], text, check_for[type][key])
                if found:
                    str_to_check[key] = found 


        except Exception as error:
            print("extract_regex_text error" + repr(error))
            str_to_check = {key: (str_to_check[key] if str_to_check.get(key) is not None else "ERROR") for key in str_to_check.keys()}
            
        return {**boolean_to_check, **str_to_check}