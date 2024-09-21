import re
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline, GenerationConfig

from modules.Logger import Logger
from modules.Config import Config

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
device_map = "auto" if device == "cuda" else {"": device}

class LLM:
    def __init__(self, logger: Logger, config: Config):
        self.config = config
        self.logger = logger

        model_name = config.model
        adapters_name = config.peft_model

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        ) if config.load_in_4bit else None

        self.logger.info(f"Загрузка модели {model_name}")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            torch_dtype=torch.float16,
            device_map=device_map,
        )


        if self.config.peft_model:
            self.logger.info(f"Загрузка LoRA модели {adapters_name}")
            model = PeftModel.from_pretrained(model, adapters_name,  torch_dtype=torch.float16)
            model = model.merge_and_unload()

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model.config.pad_token_id = tokenizer.pad_token_id = 0  # unk
        model.config.bos_token_id = 1
        model.config.eos_token_id = 2

        model.eval()

        config = GenerationConfig(
            do_sample=True,
            temperature=self.config.temperature,
            max_new_tokens=1024,
            top_p=0.95
        )
        pipe = pipeline(
            task="text-generation",
            model=model,
            tokenizer=tokenizer,
            batch_size=16,
            generation_config=config,
            framework="pt",
        )

        self.model = model
        self.tokenizer = tokenizer
        self.pipe = pipe

    def generate(self, messages: [], me) -> str:
        generated_text = self.pipe(messages, temperature=self.config.temperature)[0]["generated_text"]

        return re.sub(r'^(\w+\n)?', '', generated_text[-1]["content"])

    def generate_legacy(self, messages: [], me) -> str:
        input_ids = self._input_as_chat(messages)
        output_ids = self._generate_output(input_ids)
        result = self.tokenizer.decode(output_ids, skip_special_tokens=True)

        return re.sub(r'^(\w+\n)?', '', result)

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