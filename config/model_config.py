from dataclasses import dataclass, field
from typing import Optional, Dict
import os


@dataclass
class ModelConfig:
    model_endpoint: str = os.getenv(
        "MODEL_ENDPOINT", "http://localhost:11434/api/generate"
    )
    model_name: str = os.getenv("MODEL_NAME", "llama3:instruct")
    temperature: float = float(os.getenv("MODEL_TEMPERATURE", 0.0))
    top_p: float = float(os.getenv("MODEL_TOP_P", 1.0))
    top_k: int = int(os.getenv("MODEL_TOP_K", 0))
    repetition_penalty: float = float(os.getenv("MODEL_REPEATITION_PENALTY", 1.0))
    headers: Dict[str, str] = field(
        default_factory=lambda: {"Content-Type": "application/json"}
    )
    stop: Optional[str] = os.getenv("MODEL_STOP", None)
