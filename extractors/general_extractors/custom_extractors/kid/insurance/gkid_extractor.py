from extractors.general_extractors.custom_extractors.kid.gkid_extractor import GKidExtractor
import asyncio
import os


class InsuranceGKidExtractor(GKidExtractor):

    def __init__(self, doc_path) -> None:
        self.doc_path = doc_path
        super().__init__(doc_path, "it")

    async def process(self):
        """main processor in different phases

        Returns:
            dict(filename,dict()): dictionary containing the results for the file
        """
        # first phase for essenctial data for second phase and general information
        try:
            tasks = []
            # Extraction of tables
            tasks.append(asyncio.create_task(self.get_tables()))
            # Extraction general information
            tasks.append(asyncio.create_task(self.extract_general_data()))
            # Extraction of market
            tasks.append(asyncio.create_task(self.extract_market("market_gkid")))

            await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

            
            tables,basic_information,market = [task.result() for task in tasks]

        except Exception as error:
            print("first stage error" + repr(error))
        # second phase for all the rest
        try:
            tasks = []
            # extraction of riy
            tasks.append(asyncio.create_task(self.extract_riy(tables["riy_table"])))
            # extraction of costs and commissions
            tasks.append(
                asyncio.create_task(self.extract_cost_commissions(tables["costi_ingresso"], tables["costi_gestione"]))
            )

            await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

            
            riy, costs = [task.result() for task in tasks]

        except Exception as error:
            print("second stage error" + repr(error))

        try:
            # Merge and orders all the results


            filename = os.path.splitext(os.path.basename(self.doc_path))[0]

            api_costs = self._process_costs()

            # raccordo
            complete = self.create_json(
                {
                    "file_name": filename,
                    **dict(basic_information),
                    **dict(riy),
                    **dict(costs),
                    **dict(market),
                    **dict(api_costs),
                },
                "gkid",
            )

        except Exception as error:
            print("dictionary error" + repr(error))
            filename = os.path.splitext(os.path.basename(self.doc_path))[0]
            complete = dict([(filename), dict()])
        print(complete)
        return complete
