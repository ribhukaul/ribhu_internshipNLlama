import re
from .json_config import (
    renaming,
    field_names,
    prepare_json,
    data_array,
    model_of,
    type_of,
    range_of,
    decimals_of,
    allow_null,
    names_of_fields_to_clean_dot
)
import json
from .cost_config import available_costs
import locale
import datetime


class Field:
    def __init__(self, doc_type, key, results):
        self.name = renaming[doc_type].get(key, "Unknown Field")
        self.value = results.get(key, "ERROR")
        self.metric = model_of[doc_type].get(key, "N/A")
        self.data_type = type_of[doc_type].get(key, "N/A")
        self.range = range_of[doc_type].get(key)
        self.coord = {}  # Placeholder for future implementation
        self.decimals = decimals_of[doc_type].get(key, "N/A")
        self.allownull = allow_null[doc_type].get(key, False)

    def check_validity(self):
        """clean the value"""
        if self.name in names_of_fields_to_clean_dot:
            self.value = str(self.value).replace(".", "")
        if self.data_type == "Float":
            if isinstance(self.value, str):
                self.value = str(self.value).replace(",", ".")
            if isinstance(self.value, list):
                self.value = [str(value).replace(",", ".") for value in self.value]
        if self.data_type == "Date":
            if isinstance(self.value, str):
                self.value = self.transform_date(self.value)
            if isinstance(self.value, list):
                self.value = [self.transform_date(value) for value in self.value]
 
   
    def transform_date(self, date_str):
        # Supported date formats
        english_formats = ["%m/%d/%Y", "%B %d, %Y", "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"]  
        italian_formats = ["%d/%m/%Y", "%d %B %Y", "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"]
 
        # Attempt parsing in both English and Italian
        locale.setlocale(locale.LC_TIME, 'it_IT')
        for fmt in italian_formats :
            try:
                date_object = datetime.datetime.strptime(date_str, fmt)
                return date_object.strftime("%Y-%m-%d")  # Output in YYYY-MM-DD
            except ValueError:
                pass  # Try the next format if it doesn't match
           
        locale.setlocale(locale.LC_TIME, 'en_US')
        for fmt in english_formats :
            try:
                date_object = datetime.datetime.strptime(date_str, fmt)
                return date_object.strftime("%Y-%m-%d")  # Output in YYYY-MM-DD
            except ValueError:
                pass  # Try the next format if it doesn't match
 
        # If all parsing attempts fail
        return date_str # Return the original string
    
    
    def to_dict(self):
        """Return the fields as a dictionary

        Returns:
            dict(): Dictionary with the fields
        """
        self.check_validity()
        return {
            "name": self.name,
            "value": self.value,
            "metric": self.metric,
            "data_type": self.data_type,
            "range": self.range,
            "coord": self.coord,
            "decimals": self.decimals,
            "allownull": self.allownull,
        }


class JSONExtraction:
    def __init__(self, doc_type, results, doc_path):
        self.doc_type = doc_type
        self.results = results
        self.doc_path = doc_path
        self.fields = self.build_fields()
        self.basic_info = self.build_basic_info()
        self.sections = self.build_sections()

    def build_fields(self):
        """creates the fields for the JSON

        Returns:
            dict(): fields for the JSON
        """
        fields = {}
        for key in data_array[self.doc_type]:
            fields[field_names[self.doc_type][key]] = Field(
                doc_type=self.doc_type, key=key, results=self.results
            ).to_dict()
        return fields

    def build_basic_info(self):
        """creates the basic info for the JSON

        Returns:
            dict(): basic info for the JSON
        """

        models_cost = {value: self.results[value] for value in available_costs if value in self.results}
        basic_template = prepare_json["basic"]
        basic_info = json.loads(
            basic_template.format(path=self.doc_path, total=self.results.get("total", {}), models=models_cost)
            .replace("'", '"')
            .replace("\\", "\\\\")
        )
        return basic_info

    def build_sections(self):
        """creates the sections for the JSON

        Returns:
            dict(): sections for the JSON
        """
        sections = json.loads(prepare_json["sections"][self.doc_type])
        return sections

    def to_json(self):
        """jsonify

        Returns:
            json: final json
        """
        complete = {**self.basic_info, "sections": self.sections, "extraction": self.fields}
        return json.dumps(complete, indent=4, ensure_ascii=False)
