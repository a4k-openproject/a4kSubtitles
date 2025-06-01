import os
from PySubtitle.Providers.NexosAI.NexosAIClient import NexosAIClient
from PySubtitle.TranslationClient import TranslationClient
from PySubtitle.TranslationProvider import TranslationProvider

class Provider_NexosAI(TranslationProvider):
    name = "NexosAI"

    information = """
    <p>NexosAI API-provider. Compatible with OpenAI API format.</p>
    <p>To use NexosAI as a provider you need to provide an API Key.</p>
    """

    def __init__(self, settings: dict):
        super().__init__(self.name, {
            "api_key": settings.get('api_key', os.getenv('NEXOSAI_API_KEY')),
            "api_base": settings.get('api_base', os.getenv('NEXOSAI_API_BASE', 'https://api.nexos.ai/v1')),
            "model": settings.get('model', os.getenv('NEXOSAI_MODEL')),
        })
        self.refresh_when_changed = ['api_key', 'api_base', 'model']

    @property
    def api_key(self):
        return self.settings.get('api_key')

    @property
    def api_base(self):
        return self.settings.get('api_base')

    @property
    def model(self):
        return self.settings.get('model')

    def GetTranslationClient(self, settings: dict) -> TranslationClient:
        client_settings = self.settings.copy()
        client_settings.update(settings)
        return NexosAIClient(client_settings)

    def GetOptions(self) -> dict:
        options = {
            'api_key': (str, "A NexosAI API key is required"),
            'api_base': (str, "The NexosAI API base URL to use for requests."),
            'model': (str, "The model to use for translation."),
        }
        return options

    def GetInformation(self) -> str:
        information = self.information
        if not self.ValidateSettings():
            information = information + f"<p>{self.validation_message}</p>"
        return information

    def GetAvailableModels(self) -> list:
        # Directly use MinimalNexosAIClient to avoid unnecessary TranslationClient logic
        try:
            from PySubtitle.Providers.NexosAI.MinimalNexosAIClient import MinimalNexosAIClient
            client = MinimalNexosAIClient(self.api_key, self.api_base)
            return client.list_models()
        except Exception as e:
            import logging
            logging.error(f"Failed to list NexosAI models: {e}")
            return []

    def ValidateSettings(self) -> bool:
        if not self.api_key:
            self.validation_message = "API Key is required"
            return False
        if not self.model:
            self.validation_message = "Model is required (e.g. --model=MODEL_ID)"
            return False

        if len(self.model) != 36:
            # Model should be a valid UUID, assume that name is passed and get id from available models
            available_models = self.GetAvailableModels()
            model_name = self.model
            self.settings.update({'model': None})  # Clear model setting to avoid confusion

            for model in available_models:
                if model["name"] == model_name or model["id"] == model_name:
                    self.settings.update({'model': model["id"]})
                    return True

            if not self.model:
                self.validation_message = f"Model is not available: {model_name}"
                return False
        return True

    def _allow_multithreaded_translation(self) -> bool:
        return False
