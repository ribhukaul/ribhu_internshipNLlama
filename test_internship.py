
from extractors.custom_extractors.waminsurance.kid_governance import WamInsuranceKidGovernanceExtractor
from extractors.custom_extractors.waminsurance.gkid_governance import WamInsuranceGKidGovernanceExtractor
from extractors.custom_extractors.waminsurance.kid_credem import WamInsuranceKidCredemExtractor
from extractors.custom_extractors.waminsurance.kid_module import WamInsuranceKidModuleExtractor
from AWSInteraction.EnvVarSetter import EnvVarSetter
from extractors.custom_extractors.wamasset.fullkid import WamAssetKidExtractor
from extractors.custom_extractors.wamasset.kidtable import WamassetKidTableextractor

env_setter = EnvVarSetter()
env_setter.configure_local_env_vars()


file_path = 'data_test\priipkid_IT0001033502_PIC_removed.pdf'

extractor =  WamassetKidTableextractor(file_path)
extraction = extractor.process()

print(extraction)
# print("Costi:")
# for key, value in cost_dict.items():
#     print(f"{key}: {value}")
# print("\nGestione:")
# for key, value in gestione_dict.items():
#     print(f"{key}: {value}")





