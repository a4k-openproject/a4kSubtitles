
from PySubtitle.Providers.OpenAI.OpenAIClient import OpenAIClient
from PySubtitle.SubtitleError import TranslationResponseError

linesep = '\n'

class DeepSeekClient(OpenAIClient):
    """
    Handles chat communication with DeepSeek to request translations
    """
    def __init__(self, settings : dict):
        settings['supports_system_messages'] = True
        settings['supports_conversation'] = True
        settings['supports_reasoning'] = True
        super().__init__(settings)

    @property
    def max_tokens(self):
        return self.settings.get('max_tokens', None)

    def _send_messages(self, messages : list[str], temperature):
        """
        Make a request to DeepSeek's OpenAI-compatible API to provide a translation
        """
        result = self.client.chat_completion(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=self.max_tokens
        )
        if self.aborted:
            return None
        if not result or 'choices' not in result or not result['choices']:
            raise TranslationResponseError("No choices returned in the response", response=result)
        response = {
            'response_time': result.get('response_ms', 0),
            'prompt_tokens': result.get('usage', {}).get('prompt_tokens'),
            'output_tokens': result.get('usage', {}).get('completion_tokens'),
            'total_tokens': result.get('usage', {}).get('total_tokens'),
            'finish_reason': result['choices'][0].get('finish_reason'),
            'text': result['choices'][0].get('message', {}).get('content'),
        }
        # Optionally handle reasoning tokens if present
        completion_tokens_details = result.get('usage', {}).get('completion_tokens_details')
        if completion_tokens_details:
            response['reasoning_tokens'] = completion_tokens_details.get('reasoning_tokens')
        # Optionally handle reasoning content if present
        model_extra = result['choices'][0].get('message', {}).get('model_extra')
        if model_extra:
            reasoning_content = model_extra.get('reasoning_content')
            if reasoning_content:
                response['reasoning'] = reasoning_content
        return response

