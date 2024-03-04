

from extractors.models import Models
from extractors.general_extractors.extractor import Extractor
from llm_applications.Derivati.setting.pydantic_schema import PydanticSchema_unicredit_noLangChain




class WamDerivatiComplexity(Extractor):

    def __init__(self, doc_path, predefined_language=False):
        super().__init__(doc_path, predefined_language)


    
    def process(self):


        system_message = "You are a helpful extractor of data from document"
        human_message =  """At the beginnig I will tell you some information that will be useful to answer the question I will ask on the document.
        Final barrier:
         - Europea if the final redemption amount is calculated on a value measured on a single final valuation date(final observation date) or on a series of final valuation dates on which an average is calculated;
         - Americana if the final redemption amount is calculated on a value measured in a continuous interval between the initial valuation date and the final valuation date;
         - None if the Certificate has a floor level/ protection of 100%
        From the following certificate's document {input_kid}
        recover the following information:
        - Isin, Description or type of product, Issuer, Specified Currency, Listing, Nominal Amount, Floor Amount or Floor Level(if it is not present is not a problem), Protection, Guaranteed level, Barrier Level, strike level,
        - tell me if the final barrier is europea or americana or None, in order to respond use the info in the document and the context provided an the beginnig of my message, give me your response based on your reasoning.
        - Additional Unconditional Amount, Additional Conditional Amount(m), Additional Conditional Amount (it is the number of EUR in the table) , Additional Conditional Amount Payment Level(the percentage level in the table),
        - the Additional Conditional Amount Payment with Memory, memory effect: yes if there s the phrase 'less all additional conditional amounts (m) paid on the preceding additional conditional amount', memory effect: if in the description there is MEMORY,
        - maximum payment, underlyings of the certificate specifying Bloomberg code and Isin code, issue date, final payment date.
        - tell me if there is an Early Redemption event, do not consider MREL Disqualification Event in order to respond to this question.
        - if there is a callability mechanism, if there is a putability mechanism.
        - Tell me if there is an Early Redemption Amount greater than the Final Redempton Amount (so greater than 1000), if yes give me the first Early Redemption Amount greater than the Final Redempton Amount ((so greater than 1000))"""

        response = Models.extract_w_messages(self.doc_path, "gpt-4-turbo", text=self.text, system_message=system_message, human_message=human_message)

        tags  = Models.tag(response, PydanticSchema_unicredit_noLangChain, self.file_id, model="gpt-4-turbo")


        filename = os.path.splitext(os.path.basename(self.doc_path))[0]
        Models.clear_resources_file(filename)
        return super().process()


# import os
# import datetime
# from langchain.chat_models import ChatOpenAI
# import openai

# from complexity_custom.setting.column_config import column_dict, columns_to_clean, columns_to_date_convert
# from complexity_custom.setting.functions import get_new_column_name, truncate, extract_text_from_pdf, clean_value, convert_date
# from complexity_custom.IssuerChain.Unicredit_IssuerChain import Unicredit_IssuerChain_noLangchain
# from complexity_custom.postprocessing.dataintegration import df_dataintegration

# date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")





# def extract_certificate_info_app(kid_path, openai_api_key=''):
#     """Extract information from KID  provided path and openai api key.

#     Args:
#         kid_path (str): path to the document
#         openai_api_key (str, optional): open ai connection key. Defaults to ''.

#     Returns:
#         pandas.DataFrame: datatframe containing the information extracted from the document
#     """

#     input_kid = extract_text_from_pdf(kid_path)

#     # Set openai api key
#     if openai_api_key == '':
#         openai_api_key = os.environ["OPENAI_API_KEY"]
#     openai.api_key = openai_api_key

#     # 1ST CALL - Extract information from KID
#     completion = openai.ChatCompletion.create(
#         model="gpt-4-0613", temperature=0.0,
#         messages=[
#             {"role": "system", "content": "You are a helpful extractor of data from document"},
#             {"role": "user", "content": f"At the beginnig I will tell you some information that will be useful to answer the question I will ask on the document."
#                                         f"Final barrier: "
#                                         f"Europea if the final redemption amount is calculated on a value measured on a single final valuation date(final observation date) or on a series of final valuation dates on which an average is calculated;"
#                                         f"Americana if the final redemption amount is calculated on a value measured in a continuous interval between the initial valuation date and the final valuation date;"
#                                         f"None if the Certificate has a floor level/ protection of 100%"
#                                         f"From the following certificate's document {input_kid} "
#                                         f"recover the following information: "
#                                         f"Isin, Description or type of product, Issuer, Specified Currency, Listing, Nominal Amount, Floor Amount or Floor Level(if it is not present is not a problem), Protection, Guaranteed level, Barrier Level, strike level,"
#                                         f"tell me if the final barrier is europea or americana or None, in order to respond use the info in the document and the context provided an the beginnig of my message, give me your response based on your reasoning."
#                                         f"Additional Unconditional Amount, Additional Conditional Amount(m), Additional Conditional Amount (it is the number of EUR in the table) , Additional Conditional Amount Payment Level(the percentage level in the table),"
#                                         f"the Additional Conditional Amount Payment with Memory, memory effect: yes if there s the phrase 'less all additional conditional amounts (m) paid on the preceding additional conditional amount', memory effect: if in the description there is MEMORY, "
#                                         f"maximum payment, underlyings of the certificate specifying Bloomberg code and Isin code, issue date, final payment date."
#                                         f"tell me if there is an Early Redemption event, do not consider MREL Disqualification Event in order to respond to this question."
#                                         f"if there is a callability mechanism, if there is a putability mechanism."
#                                         f"Tell me if there is an Early Redemption Amount greater than the Final Redempton Amount (so greater than 1000), if yes give me the first Early Redemption Amount greater than the Final Redempton Amount ((so greater than 1000))"}
#         ]
#     )

#     # 2ND CALL - Format information
#     context_kid = completion.choices[0].message.content
#     llm = ChatOpenAI(temperature=0.0, model="gpt-4-0613", openai_api_key=openai_api_key)
#     df_guesses = Unicredit_IssuerChain_noLangchain(context_kid, llm)

#     df_guesses = df_guesses.rename(columns=lambda x: get_new_column_name(column_dict, x))
#     df_guesses = df_guesses.applymap(truncate)
#     df_guesses = df_guesses.replace("'", " ", regex=True)

#     df_guesses[columns_to_clean] = df_guesses[columns_to_clean].applymap(clean_value)
#     df_guesses[columns_to_date_convert] = df_guesses[columns_to_date_convert].applymap(convert_date)

#     df_final = df_dataintegration(df_guesses)
#     #guarda se c'è uno spazio e toglilo!!!

#     return df_final



# if __name__ == "__main__":
#     isin_list = ['DE000HC6V3N1']

#     path = 'FT_DE000VU2EF14.pdf'
#     extractor = WamDerivatiComplexity(path)
#     extraction = extractor.process()

#     print(extraction)



