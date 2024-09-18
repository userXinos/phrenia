import json
import os

from modules.Logger import Logger

class Config:
    def __init__(self, logger: Logger, path: str) -> None:
        self.logger = logger

        if not os.path.isfile(path):
            logger.error(f"{path} не найден")
            exit(1)
        else:
            with open(path) as file:
                self._config = json.load(file)

    @property
    def token(self) -> str:
        return self._config["token"]

    @property
    def model(self) -> str:
        return self._config["model"]

    @property
    def peft_model(self) -> str|None:
        return self._config["peftModel"]

    @property
    def load_in_4bit(self) -> bool:
        return self._config["load4bit"]

    @property
    def system_message(self) -> str:
        return self._config["systemPrompt"]

    @property
    def context_max_len(self) -> int:
        return self._config["contextMaxLen"]

    @property
    def temperature(self) -> float:
        return self._config["temperature"]

    @temperature.setter
    def temperature(self, value: float) -> None:
        self._config["temperature"] = value

    @system_message.setter
    def system_message(self, value: str) -> None:
        self._config["systemPrompt"] = value