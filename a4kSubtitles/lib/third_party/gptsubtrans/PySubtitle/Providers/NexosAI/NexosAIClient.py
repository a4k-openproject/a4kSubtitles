import logging
from PySubtitle.Providers.NexosAI.MinimalNexosAIClient import MinimalNexosAIClient
from PySubtitle.SubtitleError import TranslationError, TranslationImpossibleError
from PySubtitle.Translation import Translation
from PySubtitle.TranslationClient import TranslationClient
from PySubtitle.TranslationPrompt import TranslationPrompt
from PySubtitle.Helpers import FormatMessages

class NexosAIClient(TranslationClient):
    """
    Handles communication with Nexos AI to request translations
    """
    def __init__(self, settings: dict):
        super().__init__(settings)
        if not self.api_key:
            raise TranslationImpossibleError('API key must be provided as an argument')
        if not self.model:
            raise TranslationImpossibleError('Model must be provided as an argument (e.g. --model=MODEL_ID)')
        logging.info(f"Translating with model {self.model}, Using API Base: {self.api_base or 'https://api.nexos.ai/v1'}")
        self.client = MinimalNexosAIClient(self.api_key, self.api_base)

    @property
    def api_key(self):
        return self.settings.get('api_key')

    @property
    def api_base(self):
        return self.settings.get('api_base', 'https://api.nexos.ai/v1')

    @property
    def model(self):
        return self.settings.get('model')

    def _request_translation(self, prompt: TranslationPrompt, temperature: float = None) -> Translation:
        """
        Request a translation from Nexos AI using the chat completion endpoint.
        """
        temperature = temperature or self.settings.get('temperature', 0.0)
        response = self._send_messages(prompt.messages, temperature)
        # Extract the text content from the OpenAI-compatible response
        content = None
        if response and isinstance(response, dict):
            choices = response.get('choices')
            if choices and isinstance(choices, list) and len(choices) > 0:
                choice = choices[0]
                # OpenAI format: {'choices': [{'message': {'content': ...}}]}
                message = choice.get('message')
                if message and isinstance(message, dict):
                    content = message.get('content')
                # Some APIs may use 'text' directly
                if not content:
                    content = choice.get('text')
        if not content:
            logging.error(f"NexosAI response did not contain expected text content: {response}")
        translation = Translation({'text': content}) if content else None
        if translation:
            if translation.quota_reached:
                raise TranslationImpossibleError("Account quota reached, please upgrade your plan or wait until it renews")
            if translation.reached_token_limit:
                raise TranslationError(f"Too many tokens in translation", translation=translation)
        return translation

    def _send_messages(self, messages: list, temperature: float):
        response = self.client.chat_completion(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        return response

    def _abort(self):
        return super()._abort()
