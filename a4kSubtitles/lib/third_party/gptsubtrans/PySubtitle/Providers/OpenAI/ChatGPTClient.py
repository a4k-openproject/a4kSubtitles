

from PySubtitle.Providers.OpenAI.OpenAIClient import OpenAIClient
from PySubtitle.SubtitleError import TranslationResponseError

linesep = '\n'

class ChatGPTClient(OpenAIClient):
    """
    Handles chat communication with OpenAI to request translations
    """
    def __init__(self, settings : dict):
        settings['supports_system_messages'] = True
        settings['supports_conversation'] = True
        super().__init__(settings)

    def _send_messages(self, messages : list[str], temperature):
        """
        Make a request to an OpenAI-compatible API to provide a translation
        """
        response = {}


        api_response = self.client.chat_completion(
            model=self.model,
            messages=messages,
            temperature=temperature,
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
        message = choice.get('message', {})
        response['finish_reason'] = choice.get('finish_reason')
        response['text'] = message.get('content')

        # Return the response if the API call succeeds
        return response

