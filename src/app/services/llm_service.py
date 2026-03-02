"""
llm singleton handler to be used to query the LLM model from Mistral
and get the appropriate response in the correct format.
"""

from mistral import Mistral


# from https://refactoring.guru/fr/design-patterns/singleton/python/example
class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


PROMPT_TEMPLATE = {
    "analyse_logs": """
    Vous êtes un expert en analyse de logs réseau et en sécurité informatique. 
    Votre tâche est d'analyser les données de logs fournies et de fournir des insights pertinents sur les activités réseau, les anomalies potentielles, et les recommandations de sécurité.
    
    Voici les données de logs à analyser :
    {query_data}
    
    Veuillez fournir une analyse détaillée des activités réseau, identifier les anomalies potentielles, et proposer des recommandations de sécurité basées sur les données fournies.
    Veuillez ne fournir qu'une analyse de 10 lignes maximum.
    """,
    "analyse_graph": """
    Vous êtes un expert en analyse de logs réseau et en sécurité informatique, ainsi qu'en data-science.
    Analysez les données de logs fournies formatées pour être représentés en graph.

    Voici les données de logs à analyser :
    {query_data}

    Veuillez fournir une analyse courte mais qui permet à une personne connaissant un peu le domaine de comprendre ces données et donc le graph créé par ces données.
    """,
    "choose_between_models": """
    Vous êtes un expert en analyse de logs réseau et en sécurité informatique, ainsi qu'en data-science.
    Vous avez à votre disposition plusieurs modèles de Machine Learning pour analyser les données de logs fournies.
    Selon vos connaissance et selon ces informations :
    {query_data}
    Quel modèle de Machine Learning choisiriez-vous pour analyser ces données et pourquoi ?
    Renvoyez la réponse sous la forme d'un JSON sous cette forme : "model_choisi": "nom_du_modèle", "raison": "raison du choix du modèle"
    """,
}


class llm_service(metaclass=SingletonMeta):
    """
    LLM service class to handle the singleton instance of the LLM model.
    """

    def __init__(self, model_name: str = "mistral-7b-instruct-v0.1.Q4_0.gguf"):
        self.model = Mistral(model_name)

    def query(self, which_preprompt: str, data: str) -> str:
        """
        Query the LLM model with the given prompt and return the response.
        """
        if which_preprompt not in PROMPT_TEMPLATE:
            raise ValueError(f"Invalid preprompt key: {which_preprompt}")
        full_prompt = PROMPT_TEMPLATE[which_preprompt].format(query_data=data)
        response = self.model.generate(full_prompt)
        return response.text

    def ask_for_model_choice(self, data: str) -> dict:
        """
        Ask the LLM model to choose between different models for analyzing the logs.
        """
        response = self.query("choose_between_models", data)
        # Assuming the response is a JSON string, we can parse it
        import json

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON response from LLM: {response}")
