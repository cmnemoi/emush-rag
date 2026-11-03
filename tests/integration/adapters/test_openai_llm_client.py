import os

import pytest

from emush_rag.adapters.openai_llm_client import OpenAILLMClient
from emush_rag.config import Config
from emush_rag.ports.llm_client import ChatMessage


class TestOpenAILLMClient:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        if not os.getenv("OPENROUTER_API_KEY"):
            pytest.skip("OPENROUTER_API_KEY not set")
        config = Config()
        self.client = OpenAILLMClient(
            model=config.evaluation_model, api_key=config.openrouter_api_key, base_url=config.llm_api_base_url
        )

    def test_complete_returns_valid_response_with_system_prompt_and_user_message(self) -> None:
        system_prompt = "You are a helpful assistant. Answer questions concisely."
        messages = self._given_user_message("What is 2+2?")

        response = self._when_completing(system_prompt, messages)

        self._then_response_should_be_valid(response)
        self._then_response_should_contain_answer(response, "4")

    def test_complete_returns_valid_response_with_context_in_system_message(self) -> None:
        system_prompt = "You are a helpful assistant. Use the following context to answer the question:\n\n{context}"
        context_message = self._given_system_message(
            "The capital of France is Paris. Paris is known for the Eiffel Tower."
        )
        user_message = self._given_user_message_with_content("What is the capital of France?")
        messages = [context_message, user_message]

        response = self._when_completing(system_prompt, messages)

        self._then_response_should_be_valid(response)
        self._then_response_should_contain_answer(response, "Paris")

    def test_complete_uses_correct_temperature_setting(self) -> None:
        system_prompt = "You are a helpful assistant. Answer with exactly: 'Test response'."
        messages = self._given_user_message("Please respond.")

        response = self._when_completing(system_prompt, messages)

        self._then_response_should_be_valid(response)
        assert isinstance(response, str)
        assert len(response) > 0

    def _given_user_message(self, content: str) -> list[ChatMessage]:
        return [ChatMessage(role="user", content=content)]

    def _given_user_message_with_content(self, content: str) -> ChatMessage:
        return ChatMessage(role="user", content=content)

    def _given_system_message(self, content: str) -> ChatMessage:
        return ChatMessage(role="system", content=content)

    def _when_completing(self, system_prompt: str, messages: list[ChatMessage]) -> str:
        return self.client.complete(system_prompt, messages)

    def _then_response_should_be_valid(self, response: str) -> None:
        assert isinstance(response, str)
        assert len(response) > 0

    def _then_response_should_contain_answer(self, response: str, expected_content: str) -> None:
        assert expected_content.lower() in response.lower()
