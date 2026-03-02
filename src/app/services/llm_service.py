"""
llm singleton handler to be used to query the LLM model from Mistral
and get the appropriate response in the correct format.
"""

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Generator, List, Optional

from mistralai import Mistral

from .config import DEFAULT_MODEL, get_api_key
from .llm_options import PROMPT_TEMPLATE

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Classe pour structurer les réponses du LLM."""

    content: str
    model: str
    timestamp: datetime
    tokens_used: Optional[int] = None
    processing_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


class LLMCache:
    """Cache simple pour les réponses LLM."""

    def __init__(self, max_size: int = 100, ttl_minutes: int = 60):
        self.cache: Dict[str, tuple] = {}  # key -> (response, timestamp)
        self.max_size = max_size
        self.ttl = timedelta(minutes=ttl_minutes)

    def get(self, key: str) -> Optional[str]:
        if key in self.cache:
            response, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return response
            else:
                del self.cache[key]
        return None

    def set(self, key: str, value: str) -> None:
        if len(self.cache) >= self.max_size:
            # Supprimer le plus ancien
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]

        self.cache[key] = (value, datetime.now())


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


class llm_service(metaclass=SingletonMeta):
    """
    Enhanced LLM service class to handle the singleton instance of the LLM model.
    """

    def __init__(self, model_name: str = "", enable_cache: bool = True):
        try:
            self.model_name = model_name or DEFAULT_MODEL
            self.client = Mistral(api_key=get_api_key())
            self.cache = LLMCache() if enable_cache else None
            self.conversation_history: List[Dict[str, str]] = []
            self.total_tokens_used = 0

            logger.info(f"LLM Service initialisé avec le modèle: {self.model_name}")

        except Exception as e:
            logger.error(f"Erreur initialisation LLM service: {e}")
            raise

    def query(self, which_preprompt: str, data: str, **kwargs) -> LLMResponse:
        """
        Query the LLM model with enhanced error handling and caching.

        Args:
            which_preprompt: Clé du template de prompt
            data: Données à analyser
            **kwargs: Arguments supplémentaires (temperature, max_tokens, etc.)
        """
        start_time = time.time()

        try:
            # Validation
            if which_preprompt not in PROMPT_TEMPLATE:
                raise ValueError(f"Invalid preprompt key: {which_preprompt}")

            # Construction du prompt
            full_prompt = PROMPT_TEMPLATE[which_preprompt].format(query_data=data)

            # Vérification du cache
            cache_key = f"{which_preprompt}:{hash(data)}"
            if self.cache:
                cached_response = self.cache.get(cache_key)
                if cached_response:
                    logger.info("Réponse récupérée depuis le cache")
                    return LLMResponse(
                        content=cached_response,
                        model=self.model_name,
                        timestamp=datetime.now(),
                        processing_time=time.time() - start_time,
                    )

            # Appel API
            messages = [{"role": "user", "content": full_prompt}]
            response = self.client.chat.complete(
                model=self.model_name,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2000),
            )

            content = response.choices[0].message.content
            tokens_used = (
                response.usage.total_tokens if hasattr(response, "usage") else None
            )

            # Mise en cache
            if self.cache:
                self.cache.set(cache_key, content)

            # Mise à jour des statistiques
            if tokens_used:
                self.total_tokens_used += tokens_used

            processing_time = time.time() - start_time

            logger.info(
                f"Requête LLM réussie en {processing_time:.2f}s, {tokens_used} tokens"
            )

            return LLMResponse(
                content=content,
                model=self.model_name,
                timestamp=datetime.now(),
                tokens_used=tokens_used,
                processing_time=processing_time,
            )

        except Exception as e:
            logger.error(f"Erreur lors de la requête LLM: {e}")
            return LLMResponse(
                content="",
                model=self.model_name,
                timestamp=datetime.now(),
                processing_time=time.time() - start_time,
                success=False,
                error_message=str(e),
            )

    def ask_for_model_choice(self, data: str) -> Dict[str, Any]:
        """
        Ask the LLM model to choose between different models for analyzing the logs.
        """
        response = self.query("choose_between_models", data)

        if not response.success:
            return {"error": response.error_message}

        try:
            result = json.loads(response.content)
            result["_metadata"] = {
                "processing_time": response.processing_time,
                "tokens_used": response.tokens_used,
            }
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing JSON: {e}")
            return {"error": f"Invalid JSON response: {response.content[:200]}..."}

    def analyze_security_logs(self, log_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse spécialisée pour les logs de sécurité.
        """
        data_str = json.dumps(log_summary, default=str)
        response = self.query("analyse_logs", data_str)

        return {
            "analysis": response.content if response.success else "Erreur d'analyse",
            "success": response.success,
            "error": response.error_message,
            "metadata": {
                "processing_time": response.processing_time,
                "tokens_used": response.tokens_used,
                "model": response.model,
            },
        }

    def explain_graph_data(self, graph_data: Dict[str, Any]) -> str:
        """
        Explique les données d'un graphique.
        """
        data_str = json.dumps(graph_data, default=str)
        response = self.query("analyse_graph", data_str)
        return (
            response.content
            if response.success
            else "Impossible d'analyser le graphique"
        )

    def chat_with_context(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Discussion contextuelle avec le LLM.
        """
        try:
            if context:
                context_str = f"Contexte: {json.dumps(context, default=str)}\n\n"
                full_message = context_str + message
            else:
                full_message = message

            self.conversation_history.append({"role": "user", "content": full_message})

            messages = self.conversation_history[
                -10:
            ]  # Garder les 10 derniers messages

            response = self.client.chat.complete(
                model=self.model_name, messages=messages, temperature=0.7
            )

            assistant_response = response.choices[0].message.content
            self.conversation_history.append(
                {"role": "assistant", "content": assistant_response}
            )

            return assistant_response

        except Exception as e:
            logger.error(f"Erreur chat contextuel: {e}")
            return f"Erreur lors de la conversation: {e}"

    def stream_analysis(
        self, data: str, preprompt: str = "analyse_logs"
    ) -> Generator[str, None, None]:
        """
        Stream de l'analyse pour les gros volumes.
        """
        try:
            full_prompt = PROMPT_TEMPLATE[preprompt].format(query_data=data)

            messages = [{"role": "user", "content": full_prompt}]

            stream = self.client.chat.stream(
                model=self.model_name, messages=messages, temperature=0.7
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Erreur streaming: {e}")
            yield f"Erreur: {e}"

    def get_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques d'utilisation.
        """
        return {
            "model": self.model_name,
            "total_tokens_used": self.total_tokens_used,
            "conversation_length": len(self.conversation_history),
            "cache_size": len(self.cache.cache) if self.cache else 0,
            "cache_enabled": self.cache is not None,
        }

    def clear_cache(self) -> None:
        """Vide le cache."""
        if self.cache:
            self.cache.cache.clear()
            logger.info("Cache LLM vidé")

    def clear_conversation(self) -> None:
        """Remet à zéro la conversation."""
        self.conversation_history.clear()
        logger.info("Historique de conversation vidé")

    def validate_response_format(self, response: str, expected_format: str) -> bool:
        """
        Valide le format de la réponse.

        Args:
            response: Réponse du LLM
            expected_format: Format attendu ('json', 'text', 'list')
        """
        try:
            if expected_format == "json":
                json.loads(response)
                return True
            elif expected_format == "list":
                return isinstance(response.split("\n"), list)
            else:  # text
                return len(response.strip()) > 0
        except:
            return False
