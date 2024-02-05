from extractors.general_extractors.custom_extractors.kid.kid_extractor import KidExtractor
import asyncio
import os

from extractors.models import Models    

class InsuranceKidExtractor(KidExtractor):


    def __init__(self, doc_path) -> None:
        self.doc_path = doc_path
        super().__init__(doc_path, "it")

        
    async def process(self):
        """main processor in different phases, first phases extracts the tables and general information,
        and target market, second phase extracts the rest of the fields.

        Returns:
            dict(filename,dict()): dictionary containing the results for the file
        """
        # FIRST STAGE: get tables and general information
        try:
            tasks = []
            tasks.append(asyncio.create_task(self.get_tables()))
            tasks.append(asyncio.create_task(self.extract_general_data()))
            tasks.append(asyncio.create_task(self.extract_market()))

            await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

            tables = tasks[0].result()
            basic_information = tasks[1].result()
            market = tasks[2].result()
        except Exception as error:
            print("first stage error" + repr(error))
        
        # SECOND STAGE: extract RIY, costs, commissions and performances
        try:
            tasks = []
            tasks.append(asyncio.create_task(self.extract_riy()))
            tasks.append(asyncio.create_task(self.extract_entryexit_costs(tables["costi_ingresso"])))
            tasks.append(asyncio.create_task(self.extract_management_costs(tables["costi_gestione"])))
            tasks.append(asyncio.create_task(self.extract_performances(tables["performance"])))

            await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

            riy = tasks[0].result()
            exit_entry_costs = tasks[1].result()
            management_costs = tasks[2].result()
            performance = tasks[3].result()

        except Exception as error:
            print("second stage error" + repr(error))

        try:
            # Format results
            riy = dict(riy)
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
                    **basic_information,
                    **performance,
                    **riy,
                    **exit_entry_costs,
                    **management_costs,
                    **market,
                    **api_costs,
                },
                "kid"
            )

            complete = self.create_json(
                {
                    "file_name": filename,
                    **basic_information,
                    **performance,
                    **riy,
                    **exit_entry_costs,
                    **management_costs,
                    **market,
                    **api_costs
                },
                "kid"
            )

        except Exception as error:
            print("dictionary error" + repr(error))
            filename = os.path.splitext(os.path.basename(self.doc_path))[0]
            complete = dict([(filename), dict()])

        
        print(complete)
        Models.clear_resources_file(filename)

        return complete





    
