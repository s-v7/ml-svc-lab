"""
Clients unificados de LLM.

Interface única para todos os provedores:
    client.complete(prompt, system="", max_tokens=None) -> str

Provedores:
    - anthropic : Anthropic Claude
    - nvidia    : NVIDIA NIM, endpoint compatível com OpenAI
    - openai    : OpenAI
    - echo      : OFFLINE, devolve texto fixo, sem rede/chave

Chaves via variáveis de ambiente:
    ANTHROPIC_API_KEY, NVIDIA_API_KEY, OPENAI_API_KEY
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import os


class LLMClientError(RuntimeError):
    """Erro controlado dos clients de LLM."""


class LLMClient(ABC):
    @abstractmethod
    def complete(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int | None = None,
    ) -> str:
        pass


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise LLMClientError(
            f"Variável de ambiente obrigatória não definida: {name}"
        )

    return value


class AnthropicClient(LLMClient):
    def __init__(
        self,
        model: str = "claude-3-5-haiku-latest",
        api_key: str | None = None,
    ):
        try:
            from anthropic import Anthropic
        except ModuleNotFoundError as exc:
            raise LLMClientError(
                "Pacote 'anthropic' não instalado. Rode: python3 -m pip install anthropic"
            ) from exc

        self.model = model
        self.client = Anthropic(
            api_key=api_key or get_required_env("ANTHROPIC_API_KEY")
        )

    def complete(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int | None = None,
    ) -> str:
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens or 1024,
            "messages": [{"role": "user", "content": prompt}],
        }

        if system:
            kwargs["system"] = system

        try:
            response = self.client.messages.create(**kwargs)
        except Exception as exc:
            raise LLMClientError(f"Erro ao chamar provider Anthropic: {exc}") from exc

        return "".join(
            block.text
            for block in response.content
            if getattr(block, "type", "") == "text"
        )


class NvidiaClient(LLMClient):
    """NVIDIA NIM: mesmo SDK da OpenAI, mudando apenas a base_url."""

    def __init__(
        self,
        model: str = "meta/llama-3.1-70b-instruct",
        api_key: str | None = None,
    ):
        try:
            from openai import OpenAI
        except ModuleNotFoundError as exc:
            raise LLMClientError(
                "Pacote 'openai' não instalado. Rode: python3 -m pip install openai"
            ) from exc

        self.model = model
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key or get_required_env("NVIDIA_API_KEY"),
            timeout=90.0,
        )

    def complete(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int | None = None,
    ) -> str:
        messages = []

        if system:
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or 256,
                temperature=0.0,
            )
        except Exception as exc:
            raise LLMClientError(f"Erro ao chamar provider NVIDIA: {exc}") from exc

        return response.choices[0].message.content or ""


class OpenAIClient(LLMClient):
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
    ):
        try:
            from openai import OpenAI
        except ModuleNotFoundError as exc:
            raise LLMClientError(
                "Pacote 'openai' não instalado. Rode: python3 -m pip install openai"
            ) from exc

        self.model = model
        self.client = OpenAI(
            api_key=api_key or get_required_env("OPENAI_API_KEY"),
            timeout=30.0,
        )

    def complete(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int | None = None,
    ) -> str:
        messages = []

        if system:
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or 512,
                temperature=0.0,
            )
        except Exception as exc:
            raise LLMClientError(f"Erro ao chamar provider OpenAI: {exc}") from exc

        return response.choices[0].message.content or ""


class EchoClient(LLMClient):
    """Cliente OFFLINE para testes: não faz rede."""

    def __init__(self, resposta: str = ""):
        self.resposta = resposta

    def complete(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int | None = None,
    ) -> str:
        if self.resposta:
            return self.resposta

        return f"[echo] {prompt[:80]}"


_PROVIDERS = {
    "anthropic": AnthropicClient,
    "nvidia": NvidiaClient,
    "openai": OpenAIClient,
    "echo": EchoClient,
}


def get_client(provider: str, **kw) -> LLMClient:
    p = provider.lower()

    if p not in _PROVIDERS:
        raise ValueError(
            f"Provider inválido: {provider}. Use -> {list(_PROVIDERS)}"
        )

    return _PROVIDERS[p](**kw)
