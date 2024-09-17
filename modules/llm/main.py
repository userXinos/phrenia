import re
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from modules.Logger import Logger
from modules.Config import Config

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def clean_message(content):
    cleaned_text = re.sub(r'<@&?\d+>', '', content)
    return cleaned_text


class LLM:
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger

        model_name = config.model
        adapters_name = config.peft_model
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            load_in_4bit=config.load_in_4bit,
            torch_dtype=torch.bfloat16,
        )
        model.to(device)
        if self.config.peft_model:
            model = PeftModel.from_pretrained(model, adapters_name)
            model = model.merge_and_unload()

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.bos_token_id = 1

        self.model = model
        self.tokenizer = tokenizer

    def generate(self, messages: [], me) -> str:
        messages = [
            {
                "role": message.author.id == me.id and "assistant" or "user",
                "content": clean_message(message.content),
            }
            for message in messages
        ]

        messages.insert(0, {
            "role": "system",
            "content": self.config.system_message,
        })

        input_ids = self._input_as_chat(messages)
        output_ids = self._generate_output(input_ids)
        result = self.tokenizer.decode(output_ids, skip_special_tokens=True)

        return re.sub(r'assistant\n', '', result)

    def _input_as_chat(self, messages):
        return self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(device)

    def _generate_output(self, input_ids):
        outputs = self.model.generate(
            input_ids=input_ids,
            max_new_tokens=1024,
            do_sample=True,
            temperature=self.config.temperature,
            top_p=0.95,
            # top_k=50,
        )
        return outputs[0][input_ids.shape[-1]:]