from huggingface_hub import InferenceClient

class Definer:
    def __init__(self, hfapi):
        self.hfapi = hfapi

    def defineWord(self, word):
        prompt = f"""Define {word} in dictionary style.
                     Make it clear for non-native English speakers.
                     Output ONLY for this word, not for other words.
                        Format:
                        - Word
                        - Part of speech
                        - Definitions (numbered if more than one)
                        - Two examples
                        - Two synonyms
                    """
        client = InferenceClient(api_key=self.hfapi)
        completion = client.chat.completions.create(
            model="moonshotai/Kimi-K2-Instruct",
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content

    def grammarexplainer(self, topic):
        prompt = f"""Explain the grammar topic: {topic}.
                     Make it simple and clear for non-native English speakers.
                     Include:
                     - What it means
                     - When it is used
                     - Structure
                     - At least 3 clear examples
                     - Common mistakes and corrections"""
        client = InferenceClient(api_key=self.hfapi)
        completion = client.chat.completions.create(
            model="moonshotai/Kimi-K2-Instruct",
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content