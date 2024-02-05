from .azure.openai import azure_openai_model
import threading
import random
from langchain.chains.openai_functions.tagging import create_tagging_chain_pydantic
import tiktoken
from .general_extractors.config.cost_config import cost_per_token
from langchain.chains import LLMChain


class Models:
    """create an instance for each model to avoid loading it multiple times
    was a singleton but not variegated enough
    now holds static vars
    cant instantiate, will return the instance of a model if it exists, otherwise create it
    Args:
        model_name (str): name of the model to load
        group_id (int, optional): id of the group to which the request belongs. Defaults to -1.
        temperature (int, optional): temperature of the model. Defaults to 0.
    Returns:
        Model : instance of the model
    """

    _costs = {}
    _models = {}
    _file_locks = {}
    _lock = threading.Lock()
    # randomint=None

    def __new__(cls, model_name, group_id=-1, temperature=0):
        """return the instance of the model if it exists, otherwise create it

        Args:
            model_name (str): name of the model to load
            group_id (int or str, optional): request id, id of group of files to use the models on. Defaults to -1.
            temperature (int or str, optional): temperature for the model. Defaults to 0.

        Returns:
            Azure model: model to use for the extraction
        """
        # thread safe singleton
        group_id = str(group_id)
        temperature = str(temperature)
        with cls._lock:
            if (
                not cls._models.get(group_id, {})
                .get(model_name, {})
                .get(temperature, None)
            ):
                cls._models.setdefault(group_id, {}).setdefault(model_name, {})[
                    temperature
                ] = azure_openai_model(model=model_name, temperature=temperature)
                # for testing
                # cls.randomint=random.randint(0, 1000)
                
            return cls._models[group_id][model_name][temperature]

    @classmethod
    def tag(cls, text, schema, file_id, model="gpt-3.5-turbo"):
        """Extract tags from text using a schema and a language model.
        It uses the function create_tagging_chain_pydantic from langchain.

        Args:
            text (str): document to extract information from
            schema (pydantic object): Pydantic schema with fieds to extract
            file_id (str): file_id for costs
            model (str, optional): name of the model to use for the extractio. Defaults to 'gpt-3.5-turbo'.

        Returns:
            Schema: schema with the extracted information
        """
        llm_tag = Models(model)
        chain = create_tagging_chain_pydantic(schema, llm_tag)
        output = chain(text)
        cls.calc_costs(file_id, model, inputs=[text], outputs=[output["text"]])
        return output["text"]

    @classmethod
    def extract(cls, file_id, model, prompt, pages, rhp=None):
        """
        extracts information from pages using a language model

        Args:
            file_id (str): file_id for costs
            model (str): type of model to use
            prompt (PromptTemplate Object): prompt to ask
            pages ([str]): pages to search
            rhp (str, optional): rhp to insert. Defaults to None.

        Returns:
            str: response from the model
        """
        llm = Models(model)
        chain = LLMChain(llm=llm, prompt=prompt)
        response = chain.run(context=pages, rhp=rhp)
        if not isinstance(pages, str):
            if isinstance(pages, list):
                page_content = "".join(
                    getattr(page, "page_content", "") for page in pages
                )
            elif isinstance(pages, dict):
                pass
        cls.calc_costs(
            file_id, model, inputs=[page_content, prompt], outputs=[response]
        )
        return response

    @classmethod
    def calc_costs(cls, file_id, model, inputs=[], outputs=[]):
        """
        calculates and modifies the costs of the chain for that file

        Args:
            model (str): model you are using
            file_id (str): id of the file you are processing for threading and saving costs
            inputs (list, optional): input strings. Defaults to [].
            outputs (list, optional): output strings. Defaults to [].
        """
        try:
            if file_id not in cls._costs:
                cls._costs.update({file_id: {}})
            if file_id not in cls._file_locks:
                cls._file_locks.update({file_id: threading.Lock()})
            lock = cls._file_locks[file_id]
            encoding = tiktoken.encoding_for_model(model)
            for i in inputs:
                with lock:
                    cls._costs[file_id][model]["tokens"] = cls._costs[file_id].setdefault(model, {}).get("tokens", 0) + (
                        len(encoding.encode(str(i))) 
                    )
                    cls._costs[file_id][model]["cost"] = cls._costs[file_id][model].get("tokens", 0)* cost_per_token["input"][model]
            for o in outputs:
                with lock:
                    cls._costs[file_id][model]["tokens"] = cls._costs[file_id].setdefault(model, {}).get("tokens", 0) + (
                        len(encoding.encode(str(o))) 
                    )
                    cls._costs[file_id][model]["cost"] = cls._costs[file_id][model].get("tokens", 0)* cost_per_token["output"][model]
        except Exception as error:
            print("ERROR in costs calc: {}".format(file_id) + repr(error))

    @classmethod
    def get_costs(cls, file_id):
        """returns the costs of the file

        Args:
            file_id (str): id of the file to get the cost from

        Returns:
            dict: API costs
        """
        ret = cls._costs.get(file_id, {})
        return ret

    @classmethod
    def clear_resources_group(cls, group_id):
        """clears the static resources of the object associated with the file_id

        Args:
            file_id (str): id of the file to clear the resources from
        """
        if group_id in cls._models:
            del cls._models[group_id]

    @classmethod
    def clear_resources_file(cls, file_id):
        """clears the static resources of the object associated with the file_id

        Args:
            file_id (str): id of the file to clear the resources from
        """
        if file_id in cls._file_locks:
            del cls._file_locks[file_id]
        if file_id in cls._costs:
            del cls._costs[file_id]