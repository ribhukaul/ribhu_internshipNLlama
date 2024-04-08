
from extractors.custom_extractors.waminsurance.kid_governance import WamInsuranceKidGovernanceExtractor
from extractors.custom_extractors.waminsurance.gkid_governance import WamInsuranceGKidGovernanceExtractor
from extractors.custom_extractors.waminsurance.kid_credem import WamInsuranceKidCredemExtractor
from extractors.custom_extractors.waminsurance.kid_module import WamInsuranceKidModuleExtractor
from AWSInteraction.EnvVarSetter import EnvVarSetter

env_setter = EnvVarSetter()
env_setter.configure_local_env_vars()


file_path = 'path of the kid here'

extractor = WamInsuranceKidCredemExtractor(file_path)
extraction = extractor.process()


print(extraction)





