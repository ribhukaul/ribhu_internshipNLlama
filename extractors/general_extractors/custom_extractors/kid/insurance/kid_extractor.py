from extractors.general_extractors.custom_extractors.kid.kid_extractor import KidExtractor
import os

from extractors.models import Models


class InsuranceKidExtractor(KidExtractor):

    def __init__(self, doc_path) -> None:
        self.doc_path = doc_path
        super().__init__(doc_path, "it")

        
    def process(self):
        """main processor in different phases, first phases extracts the tables and general information,
        and target market, second phase extracts the rest of the fields.

        Returns:
            dict(filename,dict()): dictionary containing the results for the file
        """
        # FIRST STAGE: get tables and general information
        try:
      
            functions_parameters = {
                "tables": {"function":self.get_tables}, 
                "basic_information": {"function":self.extract_general_data},
                "market": {"function":self.extract_market}
                }
            results = self.threader(functions_parameters)

            tables = results["tables"]
            basic_information = results["basic_information"]
            market = results["market"]
            print("Tables and basic information:")
            print(type(tables))
            print(tables.keys())
            print(basic_information)
            print(basic_information['isin'])


        except Exception as error:
            print("first stage error" + repr(error))

        # SECOND STAGE: extract RIY, costs, commissions and performances
        try:
            functions_parameters = {
                "riy": {"function":self.extract_riy}, 
                "costs": {"function":self.extract_entryexit_costs, "args":{"table":tables["costi_ingresso"]}},
                "management_costs": {"function":self.extract_management_costs, "args": {"table":tables["costi_gestione"]}},
                "performance": {"function":self.extract_performances, "args":{"table":tables["performance"]}}
                }
            results = self.threader(functions_parameters)
            riy = results["riy"]
            exit_entry_costs = results["costs"]
            management_costs = results["management_costs"]
            performance = results["performance"]

            # riy = self.extract_riy()
            # exit_entry_costs = self.extract_entryexit_costs(tables["costi_ingresso"])
            # management_costs = self.extract_management_costs(tables["costi_gestione"])
            # performance = self.extract_performances(tables["performance"])
        

        except Exception as error:
            print("second stage error" + repr(error))

        try:
            # Format results
            riy = dict(riy)
            print("This is the RIY: ", riy)
            performance = dict(performance)
            exit_entry_costs = dict(exit_entry_costs)
            management_costs = dict(management_costs)

            # REVIEW: what name do they need?
            filename = os.path.splitext(os.path.basename(self.doc_path))[0]

            api_costs = self._process_costs()

            # raccordo
            complete = self.raccorda(
                {
                    "file_name": filename,
                    **dict(basic_information),
                    **dict(performance),
                    **dict(riy),
                    **dict(exit_entry_costs),
                    **dict(management_costs),
                    **dict(market),
                    **dict(api_costs),
                },
                "kid",
            )

            complete = self.create_json(
                {
                    "file_name": filename,
                    **dict(basic_information),
                    **dict(performance),
                    **dict(riy),
                    **dict(exit_entry_costs),
                    **dict(management_costs),
                    **dict(market),
                    **dict(api_costs),
                },
                "kid",
            )

        except Exception as error:
            print("dictionary error" + repr(error))
            filename = os.path.splitext(os.path.basename(self.doc_path))[0]
            complete = dict([(filename), dict()])

        print(complete)
        Models.clear_resources_file(filename)

        return complete


