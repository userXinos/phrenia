import json
import os
from os import makedirs
from os.path import exists, join, dirname, realpath
from pathlib import Path

from modules.Classifier import Classifier
from modules.Config import Config
from modules.Logger import Logger
from discordParser.main import parse

ROOT = realpath(dirname(__file__))
CONFIG_PATH = f"{ROOT}/config.json"
DATA_DIRECTORY = f"{ROOT}/raw"
FINAL_FILE_PATH = f"{ROOT}/dataset/trainer_data.json"
CHECKPOINT_PATH = f"{ROOT}/dataset/checkpoints"

checkpoint_files = {}

if not exists(dirname(FINAL_FILE_PATH)):
    makedirs(dirname(FINAL_FILE_PATH))

if exists(CHECKPOINT_PATH):
    json_files = [file for file in os.listdir(CHECKPOINT_PATH) if file.endswith('.json')]

    for file in json_files:
        with open(join(CHECKPOINT_PATH, file), 'r', encoding='utf-8') as f:
            data = json.load(f)
            filename = Path(file).stem
            checkpoint_files[filename] = data

def save_checkpoint(checkpoint_data: str, name: str) -> None:
    if not exists(CHECKPOINT_PATH):
        makedirs(CHECKPOINT_PATH)
    with open(join(CHECKPOINT_PATH, f"{name}.json"), 'w', encoding='utf-8') as file:
        json.dump(checkpoint_data, file, ensure_ascii=False, indent=4)

config = Config(Logger("config"), CONFIG_PATH)
classifier = Classifier(config)
data = parse(DATA_DIRECTORY, classifier, checkpoint_files, save_checkpoint)

with open(FINAL_FILE_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"Файл {FINAL_FILE_PATH} успешно создан")

