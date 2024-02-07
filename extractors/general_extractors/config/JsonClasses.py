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
    position_of,
    allow_null,
)
import json
from .cost_config import available_costs


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
        if self.name in ["SMOR RHP (€)", "SMOR 1Y (€)"]:
            self.value=self.value.replace(".", "")
        if self.data_type=="Float":
            self.value= self.value.replace(",",".")
        if self.data_type == "Date":
            self.value = re.sub(r"(\d{2})/(\d{2})/(\d{4})", r"\3-\2-\1", self.value)
    
    def to_dict(self):
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
        fields = {}
        for key in data_array[self.doc_type]:
            fields[field_names[self.doc_type][key]] = Field(
                doc_type=self.doc_type,
                key=key,
                results=self.results
            ).to_dict()
        return fields

    def build_basic_info(self):
        # Assuming 'prepare_json' contains a template for basic info
        
        models_cost = [self.results[value] for value in available_costs if value in self.results]
        basic_template = prepare_json['basic']
        basic_info = json.loads(basic_template.format(path=self.doc_path, total=self.results.get("total", {}), models=models_cost).replace('\'', '"').replace('\\','\\\\'))
        return basic_info

    def build_sections(self):
        # Assuming 'prepare_json' contains the sections info directly as JSON
        sections = json.loads(prepare_json['sections'][self.doc_type])
        return sections

    def to_json(self):
        complete = {
            **self.basic_info,
            "sections": self.sections,
            "extraction": self.fields
        }
        return json.dumps(complete, indent=4, ensure_ascii=False)
