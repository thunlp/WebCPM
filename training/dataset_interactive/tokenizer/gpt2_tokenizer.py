from transformers import GPT2Tokenizer as transformers_GPT2Tokenizer

class BaseTokenizer:
    """
    The current implementation is mainly to adapt the training framework of the Transformers toolkit,
    and replace the original model implementation.
    TODO we will change to our SAM implementation in the future, which will be a more efficient tokenizer
    """
    def __init__(self, tokenizer_type):
        self.tokenizer_type = tokenizer_type

    def from_pretrained(self, pretrained_model_name_or_path, *args, **kwargs):
        return self.tokenizer_type.from_pretrained(pretrained_model_name_or_path, *args, **kwargs)

GPT2Tokenizer = BaseTokenizer(transformers_GPT2Tokenizer)
