from openai import OpenAI

from emush_rag.ports.llm_client import ChatMessage, LLMClient


class OpenAILLMClient(LLMClient):
    def __init__(self, model: str, api_key: str | None, base_url: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def complete(self, system_prompt: str, messages: list[ChatMessage]) -> str:
        instructions, user_input = self._format_messages(system_prompt, messages)
        return self._get_response(instructions, user_input)

    def _format_messages(self, system_prompt: str, messages: list[ChatMessage]) -> tuple[str, str]:
        if not messages:
            return system_prompt, ""

        context = ""
        question = ""

        for msg in messages:
            role = self._classify_message_role(msg, messages)
            if role == "system":
                context = msg.content
            elif role == "last_user":
                question = msg.content

        instructions = system_prompt.format(context=context)
        return instructions, question

    def _get_response(self, instructions: str, user_input: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=user_input,
        )
        if not response.output_text:
            raise ValueError("No response content received from OpenAI")

        return response.output_text

    def _classify_message_role(self, message: ChatMessage, messages: list[ChatMessage]) -> str:
        if message.role == "system":
            return "system"
        if message.role == "assistant":
            return "chat_assistant"
        if message.role == "user":
            return "last_user" if message == messages[-1] else "chat_user"
        return "unknown"
