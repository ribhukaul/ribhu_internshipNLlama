from extractors.custom_extractors.waminsurance.kid_governance import WamInsuranceKidGovernanceExtractor
from extractors.custom_extractors.waminsurance.gkid_governance import WamInsuranceGKidGovernanceExtractor
from extractors.custom_extractors.waminsurance.kid_credem import WamInsuranceKidCredemExtractor
from extractors.custom_extractors.waminsurance.kid_module import WamInsuranceKidModuleExtractor
from AWSInteraction.EnvVarSetter import EnvVarSetter
from extractors.custom_extractors.wamasset.fullkid import WamAssetKidExtractor
from extractors.custom_extractors.wamasset.kidtable import WamassetKidTableextractor
from extractors.custom_extractors.waminsurance.ribhu_credim import WamInsuranceRibhuExtractor # a copy of kid_credim, eliminate before commiting
import json   # can be removed from the original code
import os
import pandas as pd

env_setter = EnvVarSetter()
env_setter.configure_local_env_vars()

file_path1 = 'C:/Users/ribhu.kaul//RibhuLLM//Data//MultipleExecTest//priipkid_IT0000380029_PAC.pdf'


# The below code extracts info from file_path and file_path and saves to excel in the format we want
extractor1 =  WamInsuranceRibhuExtractor(file_path1)
extraction1 = extractor1.process1()

print(extraction1)