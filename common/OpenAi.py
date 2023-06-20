import openai

class OpenAi:

    engine = None
    chat_gpt3_model_engine = "text-davinci-003"
    chat_gpt4_model_engine = "gpt-4"

    #generate dalle image
    def get_dalle_image_url(self, prompt:str):
        print("start dalle generation")
        response = openai.Image.create(
                prompt=prompt,
                n=3,
                size="1024x1024"
            )
        result = []
        for data in response['data']:
            result.append(data['url'])
        return result

    #get chatGpt answer
    def get_chat_gpt_answer(self, prompt:str):
        completion = openai.Completion.create(engine=self.engine,
                                            prompt=prompt,
                                            max_tokens=3900,
                                            temperature=0.5)
        result=completion.choices[0].text
        return result

    def __init__(self, token, engine=chat_gpt3_model_engine):
        openai.api_key = token
        self.engine=engine