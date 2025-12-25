from openai import OpenAI
from .base import LLMProvider

class GenericProvider(LLMProvider):
    def __init__(self, base_url:str, api_key:str, model: str) -> None:
        self.model = model
        self.client = OpenAI(
                base_url=base_url,
                api_key=api_key
            )

    def ask(self, system_prompt: str ,query: str) -> str:
        try:
            response = self.client.chat.completions.create(
                    model = self.model,
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.7,
                    stream=False
            )

            return response.choices[0].message.content
        except Exception as e:
            return f"Error from Provider: {str(e)}"
