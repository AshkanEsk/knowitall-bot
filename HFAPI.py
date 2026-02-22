from gradio_client import Client
# No need to import 'configs' here if values are passed during instantiation

class Definer:
    # Removed default arguments from __init__ as they are passed explicitly from bot.py
    def __init__(self, hfapi, owner, llm):
        self.owner = owner
        self.llm = llm
        self.hfapi = hfapi # This is the actual HF token string

    def defineWord(self, word):
        prompt = f"""Define {word}, in dictionary style. Do not define in short form.
                     return your answer in this form:
                     part of speech
                     definitions
                     examples(2 examples)
                     synonyms(2 synonyms)."""
        client = Client(self.owner + '/' + self.llm, hf_token=self.hfapi)
        result = client.predict(
                message=prompt,
                system_message="You are a friendly Chatbot, mostly used to define words.",
                max_tokens=512,
                temperature=0.7,
                top_p=0.95,
                api_name="/chat"
        )
        return result

    def grammarexplainer(self, grammar):
        prompt = f"""Explain {grammar} grammar.
                     Your explanation must include enough examples to clarify."""
        client = Client(self.owner + '/' + self.llm, hf_token=self.hfapi)
        result = client.predict(
                message=prompt,
                system_message="You are a friendly Chatbot, mostly used to clarify Grammars.",
                max_tokens=512,
                temperature=0.7,
                top_p=0.95,
                api_name="/chat"
        )
        return result