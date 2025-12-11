from openai import OpenAI

class APIClient:
    def __init__(self, api_key: str | None = None):
        self.client = OpenAI(api_key=api_key)

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
