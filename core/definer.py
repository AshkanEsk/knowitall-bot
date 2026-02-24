"""Definer class for word definitions and grammar explanations."""

from huggingface_hub import InferenceClient
from gradio_client import Client


class Definer:
    """Provides word definitions and grammar explanations using HuggingFace models."""
    
    def __init__(self, hfapi: str, owner: str, llm: str):
        self.owner = owner
        self.llm = llm
        self.hfapi = hfapi

    def define_word(self, word: str) -> str:
        """
        Define a word in dictionary style.
        
        Args:
            word: The word to define
            
        Returns:
            Formatted definition string
        """
        prompt = f"""Define {word}, in dictionary style. Do not define in short form.
                     It should be understandable for non-native English person.
                     Return your answer in this form:
                     part of speech
                     definitions
                     examples (2 examples)
                     synonyms (2 synonyms)."""
        
        client = InferenceClient(api_key=self.hfapi)
        completion = client.chat.completions.create(
            model="moonshotai/Kimi-K2-Instruct",
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content

    def explain_grammar(self, grammar: str) -> str:
        """
        Explain a grammar concept.
        
        Args:
            grammar: The grammar topic to explain
            
        Returns:
            Grammar explanation with examples
        """
        prompt = f"""Explain {grammar} grammar.
                     Your explanation must include enough examples to clarify."""
        
        client = Client(f"{self.owner}/{self.llm}", hf_token=self.hfapi)
        result = client.predict(
            message=prompt,
            system_message="You are a friendly Chatbot, mostly used to clarify Grammars.",
            max_tokens=512,
            temperature=0.7,
            top_p=0.95,
            api_name="/chat"
        )
        return result