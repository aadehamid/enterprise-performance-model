"""
llm.py  --  Named-provider LLM factory.

LLM_PROVIDER selects one of four natively-supported neo4j-graphrag
wrappers. No custom adapters: each is the library's own class.

  azure      AzureOpenAILLM key: AZURE_OPENAI_API_KEY (Azure hosted models)
  openai     OpenAILLM      key: OPENAI_API_KEY
  anthropic  AnthropicLLM   key: ANTHROPIC_API_KEY   (needs [anthropic] extra)
  google     VertexAILLM    auth: GCP ADC service-account JSON
                             (GOOGLE_APPLICATION_CREDENTIALS) (needs [google])

Default model per provider is filled in if LLM_MODEL is blank.
"""
from neo4j_graphrag.llm import OpenAILLM, AnthropicLLM, VertexAILLM, AzureOpenAILLM
import app.config as config

_DEFAULT_MODEL = {
    "azure": "gpt-5.4",
    "openai": "gpt-4o",
    "anthropic": "claude-sonnet-4-6",
    "google": "gemini-1.5-pro",
}


class LLM:
    _instance = None

    def __init__(self, provider, model, temperature,
                 openai_key, anthropic_key, project, location,
                 azure_endpoint="", azure_key="", azure_version=""):
        
        provider = provider or config.LLM_PROVIDER
        model = model or config.LLM_MODEL or _DEFAULT_MODEL.get(provider)
        temperature = temperature if temperature is not None else config.LLM_TEMPERATURE

        if provider == "azure":
            azure_key = azure_key or config.AZURE_OPENAI_API_KEY
            azure_endpoint = azure_endpoint or config.AZURE_OPENAI_ENDPOINT
            azure_version = azure_version or config.AZURE_API_VERSION
            
            # Resolve deployment_name and default model to AZURE_DEPLOYMENT_NAME if not specified
            deployment_name = config.AZURE_DEPLOYMENT_NAME or model
            if (not model or model == _DEFAULT_MODEL.get("azure")) and config.AZURE_DEPLOYMENT_NAME:
                model = config.AZURE_DEPLOYMENT_NAME
                deployment_name = model
            
            if not azure_key or not azure_endpoint:
                raise RuntimeError("LLM_PROVIDER=azure but keys/endpoint are empty in environment.")
            
            # Format/replace placeholders in azure_endpoint if they exist
            if "{deployment-id}" in azure_endpoint:
                azure_endpoint = azure_endpoint.replace("{deployment-id}", deployment_name)
            if "{api-version}" in azure_endpoint:
                azure_endpoint = azure_endpoint.replace("{api-version}", azure_version)
            
            # AzureOpenAILLM passes kwargs (azure_endpoint, api_key, api_version)
            # directly to the openai.AzureOpenAI client constructor!
            self._llm = AzureOpenAILLM(
                model_name=model,
                model_params={"temperature": temperature},
                azure_endpoint=azure_endpoint,
                api_key=azure_key,
                api_version=azure_version,
            )

        elif provider == "openai":
            openai_key = openai_key or config.OPENAI_API_KEY or ""
            if not openai_key:
                raise RuntimeError("LLM_PROVIDER=openai but OPENAI_API_KEY is empty.")
            self._llm = OpenAILLM(
                model_name=model,
                model_params={"temperature": temperature},
                api_key=openai_key,
            )

        elif provider == "anthropic":
            anthropic_key = anthropic_key or config.ANTHROPIC_API_KEY or ""
            if not anthropic_key:
                raise RuntimeError("LLM_PROVIDER=anthropic but ANTHROPIC_API_KEY is empty.")
            self._llm = AnthropicLLM(
                model_name=model,
                model_params={"max_tokens": 4096},
                api_key=anthropic_key,
            )

        elif provider == "google":
            project = project or config.GOOGLE_PROJECT
            location = location or config.GOOGLE_LOCATION
            kw = {}
            if project:
                kw["project"] = project
            if location:
                kw["location"] = location
            self._llm = VertexAILLM(
                model_name=model,
                model_params={"temperature": temperature},
                **kw,
            )

        else:
            raise RuntimeError(
                f"Unknown LLM_PROVIDER={provider!r}. "
                "Use one of: azure, openai, anthropic, google."
            )

    @classmethod
    def get_instance(cls, provider="", model="", temperature=None,
                      openai_key="", anthropic_key="",
                      project="", location="",
                      azure_endpoint="", azure_key="", azure_version=""):
        if cls._instance is None:
            cls._instance = cls(
                provider, model, temperature,
                openai_key, anthropic_key, project, location,
                azure_endpoint, azure_key, azure_version
            )
        return cls._instance

    @property
    def llm(self):
        return self._llm
