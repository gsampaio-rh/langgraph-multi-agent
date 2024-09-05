from dataclasses import dataclass
import os


@dataclass
class LoggingConfig:
    verbose: bool = bool(int(os.getenv("LOGGING_VERBOSE", "1")))
