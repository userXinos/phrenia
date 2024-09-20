import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from modules.Config import Config

class Classifier:
    def __init__(self, config: Config) -> None:
        self.model = AutoModelForSequenceClassification.from_pretrained(config.classifier_model)
        self.tokenizer = AutoTokenizer.from_pretrained(config.classifier_model, clean_up_tokenization_spaces=True)

    def process(self, message1: str, message2: str) -> float:
        prompt = '[CLS]' + message1 + '[RESPONSE_TOKEN]' + message2
        inputs = self.tokenizer(prompt, max_length=128, add_special_tokens=False, truncation=True, return_tensors='pt')

        with torch.inference_mode():
            result = torch.sigmoid(self.model(**inputs).logits)[0].cpu().detach().numpy()
        relevance, specificity = result

        return relevance