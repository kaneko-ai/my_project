from transformers import MarianMTModel, MarianTokenizer

model_name = "staka/fugumt-en-ja"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

def translate_to_japanese(text):
    batch = tokenizer.prepare_seq2seq_batch([text], return_tensors="pt")
    gen = model.generate(**batch)
    return tokenizer.decode(gen[0], skip_special_tokens=True)
