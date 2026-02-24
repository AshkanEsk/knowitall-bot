from huggingface_hub import InferenceClient

class Definer:
    def __init__(self, hfapi):
        self.hfapi = hfapi

    def defineWord(self, word):
        prompt = f"""Define {word} in dictionary style.
                     Make it clear for non-native English speakers.
                     Format:
                     - Part of speech
                     - Definitions
                     - Two examples
                     - Two synonyms"""
        client = InferenceClient(api_key=self.hfapi)
        completion = client.chat.completions.create(
            model="moonshotai/Kimi-K2-Instruct",
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content