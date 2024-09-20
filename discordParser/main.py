import os
import json
import re
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import itertools
from pathlib import Path
from tqdm import tqdm

from modules.Classifier import Classifier

# UTC-4:00. 6 утра в Москве, все ушли спать
TZ = timezone(timedelta(hours=-4))

REPLACEMENTS = {
    r'<@\!?\d+?>': "_USER_MENTION_",
    r'@.+?#\d{4}': "_USER_MENTION_",
    r'<#\d+?>': "_CHANNEL_MENTION_",
    r'<@&\d+?>': "_ROLE_MENTION_",
    r'<a?:[\w-]+:\d+?>': "_CUSTOM_EMOJI_",
    r'(\b\w+\b)(?:\s+\1){3,}': lambda m: m.group(1),  # удалить слова, которые повторяются более 3 раза
    r'(.{5,})\1{5,}': r"\1", # удалить символы, которые повторяются более 5 раза
    '(@everyone|@here)': '',  # удалить глобальные пинги
    r'http[s]?://\S+': '',  # удалить http ссылки
    r'^\s?(_USER_MENTION_|_CHANNEL_MENTION_|_ROLE_MENTION_)\s?$': '',  # удалить бесполезные пинги
    r'\u00ad': '',  # удалить невидимый символ
    r'^\.$': '',  # удалить сообщения, если это тупо точка
}


def parse(directory: str, classifier: Classifier, checkpoint_files: [object], save_checkpoint_fn: ()) -> object:
    files, checkpoints, save_checkpoints = load_files(directory, checkpoint_files, save_checkpoint_fn)
    data = filter_messages(files)

    return process_data(data, checkpoints, save_checkpoints, classifier)


def load_files(directory: str, checkpoint_files: [object], save_checkpoint_fn: ()) -> [object]:
    files = []
    checkpoints = []
    save_checkpoints = []
    json_files = [file for file in os.listdir(directory) if
                  file.endswith('.json') and (not file.endswith('.schema.json'))]

    for file in json_files:
        with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
            data = json.load(f)
            files.append(data['messages'])
            filename = Path(file).stem

            if filename in checkpoint_files:
                checkpoints.append(checkpoint_files[filename])
            else:
                checkpoints.append({})

            save_checkpoints.append(lambda cd: save_checkpoint_fn(cd, filename))

    return files, checkpoints, save_checkpoints

def clean_content(content: str) -> str:
    for pattern, replacement in REPLACEMENTS.items():
        content = re.sub(pattern, replacement, content)
    return content.strip()


def filter_messages(files: [object]) -> [object]:
    data = []

    for file in files:
        for item in file:
            item['content'] = clean_content(item['content'])

    for index, file in enumerate(files):
      data.append([])

      for item in file:
        if item['type'] in ['Default', 'Reply'] and item['content'] and not item['author'].get('isBot', False):
            data[index].append({
            'content': item['content'],
            'id': item['id'],
            'timestamp': item['timestamp'],
            'author': item['author']['nickname'],
            'reference': item['reference'].get('messageId') if item.get('reference') else None,
        })
    return data


def group_replays(raw_data: [object]) -> [object]:
    raw_data_collection = {item["id"]: item for item in raw_data}
    replays = []

    for item in raw_data:
        if item["reference"] is not None:
            reference = raw_data_collection.get(item["reference"], None)
            if reference:
                replays.append({
                    "instruction": reference["content"],
                    "input": "",
                    "output": item["content"]
                })
                raw_data_collection[item["reference"]] = None
                raw_data_collection[item["id"]] = None
    data = [item for item in raw_data_collection.values() if item is not None]

    return replays, data

def group_by_day(raw_data: [object]) -> defaultdict:
    by_day = defaultdict(list)

    for msg in raw_data:
        date_tz = datetime.fromisoformat(msg["timestamp"])
        date_utc = date_tz.astimezone(TZ)
        date = date_utc.date()
        by_day[date].append(msg)
    for day in by_day:
        by_day[day] = merge_messages_by_author(by_day[day])
    return by_day

def merge_messages_by_author(messages):
    merged_messages = []
    last_msg = messages[0]
    last_content = messages[0]['content']

    for message in messages[1:]:
        if message['author'] == last_msg['author']:
            last_content += ' ' + message['content']
        else:
            last_content = message['content']
            last_msg = message
            merged_messages.append({**message, 'content': last_content})

    merged_messages.append({**last_msg, 'content': last_content})

    return merged_messages

def process_data(datas: [object], checkpoints: [object], save_checkpoints: [()], classifier: Classifier) -> [object]:
    result = []

    for i, data in enumerate(datas):
        save_checkpoint = lambda cd: save_checkpoints[i](cd)
        replays, data = group_replays(data)
        by_day = group_by_day(data)
        checkpoint = checkpoints[i]
        days_len = len(by_day)

        for day, messages in by_day.items():
            key = str(day)
            max_len = len(messages)

            if key in checkpoint:
                continue
            else:
                checkpoint[key] = []

            added_instructions = [] # чтобы не было дубликатов диалогов
            for ii, message in enumerate(tqdm(messages, f"День: {list(by_day).index(day) + 1}/{days_len} ({day})")):
                for iii in range(1, 4):
                    if ii + iii < max_len:
                        content1 = message["content"]
                        content2 = messages[ii + iii]["content"]

                        if content2 not in added_instructions:
                            result = classifier.process(content1, content2)

                            if result > 0.8:
                                added_instructions.append(content1)
                                checkpoint[key].append({
                                    "instruction": content1,
                                    "input": "",
                                    "output": content2
                                })
            save_checkpoint(checkpoint)

        result = result + list(itertools.chain.from_iterable(checkpoint.values())) + replays

    return result