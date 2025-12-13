from openai import OpenAI
import os

class APIClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "OPENAI_API_KEY not set. Set it in your .env or environment variables."
            )
        self.client = OpenAI(api_key=self.api_key)

    def get_completion(self, prompt: str) -> str:
        response = self.client.responses.create(
            model="gpt-5-nano",
            input=prompt,
            #max_output_tokens=200,
            reasoning={"effort": "low"},
            store = True
        )
        print("Raw response:", response)
        return response.output_text
