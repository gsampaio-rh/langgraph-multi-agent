# utils/setup_model.py
from config.model_config import ModelConfig

def setup_ollama_model(model_config: ModelConfig):
    """
    Sets up the Ollama model configuration using a ModelConfig instance.

    Parameters:
    - model_config (ModelConfig): An instance of the ModelConfig class containing the model configuration.

    Returns:
    - dict: Configuration for the Ollama model.
    """
    return {
        "model_endpoint": model_config.model_endpoint,
        "model": model_config.model_name,
        "temperature": model_config.temperature,
        "headers": model_config.headers,
        "stop": model_config.stop,
    }
