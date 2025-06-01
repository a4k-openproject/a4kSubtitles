
import logging
import time


from PySubtitle.Helpers.Parse import ParseDelayFromHeader
from PySubtitle.Helpers import FormatMessages
from PySubtitle.Translation import Translation
from PySubtitle.TranslationClient import TranslationClient
from PySubtitle.TranslationPrompt import TranslationPrompt
from PySubtitle.SubtitleError import TranslationImpossibleError, TranslationResponseError
from PySubtitle.Providers.OpenAI.MinimalOpenAIClient import MinimalOpenAIClient

class AzureOpenAIClient(TranslationClient):
    """
    Handles communication with AzureOpenAI-compatible endpoints to request translations
    """
    def __init__(self, settings : dict):
        super().__init__(settings)

        if not self.api_key:
            raise TranslationImpossibleError('API key must be provided as an argument')

        if not self.api_base:
            raise TranslationImpossibleError('API base must be provided as an argument')

        if not self.api_version:
            raise TranslationImpossibleError('API version must be provided as an argument')

        if not self.deployment_name:
            raise TranslationImpossibleError('Deployment name must be provided as an argument')

        logging.info(f"Translating with Azure OpenAI deployment {self.deployment_name}, API-version {self.api_version}, API Base: {self.api_base}")

        # Use MinimalOpenAIClient with Azure endpoint
        self.client = MinimalOpenAIClient(
            api_key=self.api_key,
            api_base=self.api_base,
            timeout=60
        )


    @property
    def api_key(self):
        return self.settings.get('api_key')

    @property
    def api_base(self):
        return self.settings.get('api_base')

    @property
    def api_version(self):
        return self.settings.get('api_version')

    @property
    def deployment_name(self):
        return self.settings.get('deployment_name')

    @property
    def rate_limit(self):
        return self.settings.get('rate_limit')


    def _request_translation(self, prompt : TranslationPrompt, temperature : float = None) -> Translation:
        """
        Request a translation based on the provided prompt
        """
        logging.debug(f"Messages:\n{FormatMessages(prompt.messages)}")

        temperature = temperature or self.temperature
        response = self._send_messages(prompt.messages, temperature)
        translation = Translation(response) if response else None
        return translation

    def _send_messages(self, messages : list[str], temperature):
        """
        Make a request to the Azure OpenAI-compatible API to provide a translation
        """
        response = None
        for retry in range(self.max_retries + 1):
            if self.aborted:
                return None
            try:
                # Use deployment_name as the model for Azure
                result = self.client.chat_completion(
                    model=self.deployment_name,
                    messages=messages,
                    temperature=temperature
                )
                if self.aborted:
                    return None
                # MinimalOpenAIClient returns a dict
                if not result or 'choices' not in result or not result['choices']:
                    raise TranslationResponseError("No choices returned in the response", response=result)
                response = {
                    'response_time': result.get('response_ms', 0),
                    'prompt_tokens': result.get('usage', {}).get('prompt_tokens'),
                    'completion_tokens': result.get('usage', {}).get('completion_tokens'),
                    'total_tokens': result.get('usage', {}).get('total_tokens'),
                    'finish_reason': result['choices'][0].get('finish_reason'),
                    'text': result['choices'][0].get('message', {}).get('content'),
                }
                return response
            except TranslationResponseError as e:
                if retry < self.max_retries and not self.aborted:
                    backoff_time = self.backoff_time * 2.0**retry
                    logging.warning(f"{str(e)}, retrying in {backoff_time} seconds...")
                    time.sleep(backoff_time)
                    continue
                raise
            except Exception as e:
                # Handle HTTP errors from MinimalOpenAIClient
                if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                    if e.response.status_code == 429 and not self.aborted:
                        retry_after = e.response.headers.get('x-ratelimit-reset-requests') or e.response.headers.get('Retry-After')
                        if retry_after:
                            backoff_time = ParseDelayFromHeader(retry_after)
                            logging.warning(f"Rate limit hit, retrying in {backoff_time} seconds...")
                            time.sleep(backoff_time)
                            continue
                        else:
                            raise TranslationImpossibleError("Account quota reached, please upgrade your plan")
                raise TranslationImpossibleError(f"Unexpected error communicating with Azure OpenAI-compatible endpoint", error=e)
        if not self.aborted:
            raise TranslationImpossibleError(f"Failed to communicate with provider after {self.max_retries} retries")

    def _abort(self):
        # MinimalOpenAIClient does not require explicit close
        return super()._abort()
