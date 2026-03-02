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
