

from PySubtitle.Providers.OpenAI.OpenAIClient import OpenAIClient
from PySubtitle.SubtitleError import TranslationResponseError

linesep = '\n'

class InstructGPTClient(OpenAIClient):
    """
    Handles communication with GPT instruct models to request translations
    """
    def __init__(self, settings : dict):
        settings['supports_conversation'] = False
        settings['supports_system_messages'] = False
        super().__init__(settings)

    @property
    def max_instruct_tokens(self):
        return self.settings.get('max_instruct_tokens', 2048)

    def _send_messages(self, prompt : str, temperature):
        """
        Make a request to the OpenAI API to provide a translation
        """
        response = {}


        api_response = self.client.instruct_completion(
            model=self.model,
            prompt=prompt,
            temperature=temperature,
            n=1,
            max_tokens=self.max_instruct_tokens
        )
        result = api_response

        if self.aborted:
            return None


        if not result or 'choices' not in result or not result['choices']:
            raise TranslationResponseError("No choices returned in the response", response=result)


        response['response_time'] = result.get('response_ms', 0)

        usage = result.get('usage', {})
        response['prompt_tokens'] = usage.get('prompt_tokens')
        response['output_tokens'] = usage.get('completion_tokens')
        response['total_tokens'] = usage.get('total_tokens')

        choice = result['choices'][0]
        text = choice.get('text')
        if not isinstance(text, str):
            raise TranslationResponseError("Instruct model completion text is not a string", response=result)
        response['finish_reason'] = choice.get('finish_reason')
        response['text'] = text

        # Return the response content if the API call succeeds
        return response

