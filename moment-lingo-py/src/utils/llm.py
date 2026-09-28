import logging
from abc import abstractmethod, ABC
from typing import Generator, Any, AsyncGenerator, cast

from openai import OpenAI, AsyncOpenAI, AsyncStream
from pydantic import BaseModel, Field
from sse_starlette import ServerSentEvent

import src.utils.common as utils
from src.config import AIConf, BaseAIConf
from src.utils.sse import Sse

logger = logging.getLogger(__name__)


class ChatCompletion(BaseModel):
    content: str
    reasoning_content: str | None = Field(None, alias="reasoningContent")
    timestamp: int = Field(default_factory=utils.timestamp)


class BaseThinkingConf:
    def __init__(self, enable: dict, disable: dict):
        self.enable = enable
        self.disable = disable


class BaseAIModel:
    def __init__(self, model: str, conf: BaseAIConf, thinking: BaseThinkingConf, adapter: str = 'openai'):
        self.model = model
        self.base_url = conf.base_url
        self.api_key = conf.api_key
        self.provider = conf.provider
        # 深度思考模式配置
        self.thinking = thinking
        # 模型适配器 默认兼容openai
        self.adapter = adapter


class BaseAIAdapter(ABC):
    def __init__(self, model: BaseAIModel):
        self.model = model

    @abstractmethod
    def chat_completions(self, messages: list, stream: bool, thinking: bool, **kwargs) -> Generator[
        ServerSentEvent, Any, ChatCompletion | None]:
        pass

    @abstractmethod
    async def chat_completions_async(self, messages: list, stream: bool, thinking: bool, **kwargs) -> AsyncGenerator[
        ServerSentEvent, ChatCompletion | None]:
        pass


class AIThinkingConf:
    volcengine = BaseThinkingConf(
        enable={
            'thinking': {
                'type': 'enabled'
            }
        },
        disable={
            'thinking': {
                'type': 'disabled'
            }
        }
    )

    bailian = BaseThinkingConf(
        enable={
            'enable_thinking': True
        },

        disable={
            'enable_thinking': False
        }
    )


class AIModel:
    doubao_seed_vision = BaseAIModel('ep-20251016140950-4mnhr', AIConf.volcengine, AIThinkingConf.volcengine)
    deepseek_v3_2 = BaseAIModel('ep-20251207173906-krn29', AIConf.volcengine, AIThinkingConf.volcengine)
    deepseek_v3_1 = BaseAIModel('ep-20251013223959-ls6sp', AIConf.volcengine, AIThinkingConf.volcengine)
    doubao_seed_v1_6_flash = BaseAIModel('ep-20251013224145-x5fgl', AIConf.volcengine, AIThinkingConf.volcengine)
    qwen_flash = BaseAIModel('qwen-flash', AIConf.bailian, AIThinkingConf.bailian)
    doubao_seed_v2_lite = BaseAIModel('ep-20260216001035-bprqd', AIConf.volcengine, AIThinkingConf.volcengine)
    doubao_seed_v2_mini = BaseAIModel('ep-20260216001100-t7fw7', AIConf.volcengine, AIThinkingConf.volcengine)
    deepseek_v4_flash = BaseAIModel('deepseek-v4-flash', AIConf.bailian, AIThinkingConf.bailian)
    deepseek_v4_pro = BaseAIModel('deepseek-v4-pro', AIConf.bailian, AIThinkingConf.bailian)


class OpenAIAdapter(BaseAIAdapter):
    def __init__(self, model: BaseAIModel):
        super().__init__(model)

        self.client = OpenAI(
            base_url=self.model.base_url,
            api_key=self.model.api_key
        )

        self.async_client = AsyncOpenAI(
            base_url=self.model.base_url,
            api_key=self.model.api_key
        )

    def chat_completions(self, messages: list, stream: bool, thinking: bool, **kwargs) \
        -> ChatCompletion | Generator[ServerSentEvent, None, None]:
        if stream:
            def _generator():
                try:
                    yield Sse.start_event()

                    _completion = self.client.chat.completions.create(
                        model=self.model.model,
                        messages=messages,
                        stream=True,
                        extra_body=self.model.thinking.enable if thinking else self.model.thinking.disable,
                        **kwargs
                    )

                    for chunk in _completion:
                        delta = chunk.choices[0].delta

                        if hasattr(delta, 'reasoning_content'):
                            _reasoning_content = delta.reasoning_content
                        else:
                            _reasoning_content = None

                        yield Sse.processing_event(
                            ChatCompletion(content=delta.content or "",
                                reasoningContent=_reasoning_content).model_dump_json(
                                by_alias=True
                            ), False
                        )

                    yield Sse.end_event()
                except Exception as _e:
                    logger.error(f'OpenAIAdapter.chat_completions 调用错误 {_e}')
                    yield Sse.error_event("服务器内部错误")

            return _generator()
        else:
            try:
                completion = self.client.chat.completions.create(
                    model=self.model.model,
                    messages=messages,
                    stream=False,
                    extra_body=self.model.thinking.enable if thinking else self.model.thinking.disable,
                    **kwargs
                )
                message = completion.choices[0].message
                if hasattr(message, 'reasoning_content'):
                    reasoning_content = message.reasoning_content
                else:
                    reasoning_content = None

                return ChatCompletion(content=message.content or "", reasoningContent=reasoning_content)
            except Exception as e:
                logger.error(f'OpenAIAdapter.chat_completions 调用错误 {e}')
                raise e

    async def chat_completions_async(self, messages: list, stream: bool, thinking: bool, **kwargs) \
        -> ChatCompletion | AsyncGenerator[ServerSentEvent, ChatCompletion | None]:
        if stream:
            async def _async_generator():
                try:
                    yield Sse.start_event()

                    _completion = await self.async_client.chat.completions.create(
                        model=self.model.model,
                        messages=messages,
                        stream=True,
                        extra_body=self.model.thinking.enable if thinking else self.model.thinking.disable,
                        **kwargs
                    )

                    async for chunk in cast(AsyncStream, _completion):
                        delta = chunk.choices[0].delta

                        if hasattr(delta, 'reasoning_content'):
                            _reasoning_content = delta.reasoning_content
                        else:
                            _reasoning_content = None

                        yield Sse.processing_event(
                            ChatCompletion(content=delta.content or "",
                                reasoningContent=_reasoning_content).model_dump_json(
                                by_alias=True
                            ), False
                        )

                    yield Sse.end_event()
                except Exception as _e:
                    logger.error(f'OpenAIAdapter.chat_completions_async 调用错误 {_e}')
                    yield Sse.error_event("服务器内部错误")

            return _async_generator()
        else:
            try:
                completion = await self.async_client.chat.completions.create(
                    model=self.model.model,
                    messages=messages,
                    stream=False,
                    extra_body=self.model.thinking.enable if thinking else self.model.thinking.disable,
                    **kwargs
                )
                message = completion.choices[0].message
                if hasattr(message, 'reasoning_content'):
                    reasoning_content = message.reasoning_content
                else:
                    reasoning_content = None

                return ChatCompletion(content=message.content, reasoningContent=reasoning_content)
            except Exception as e:
                logger.error(f'OpenAIAdapter.chat_completions_async 调用错误 {e}')
                raise e


class LLMClient:
    _adapter = {
        'openai': OpenAIAdapter
    }

    _clients_cache = {}

    def __init__(self, model: BaseAIModel):
        self.model = model
        if self.model.adapter not in self._adapter:
            raise ValueError(f'不支持的模型适配器 {self.model.adapter}')

        if self.model.model not in self._clients_cache:
            self._clients_cache[self.model.model] = self._adapter[self.model.adapter](self.model)

        self.client = self._clients_cache[self.model.model]

    def chat_completions(
        self,
        messages: list,
        *,
        stream: bool = False,
        thinking: bool = False,
        **kwargs
    ) -> ChatCompletion | Generator[ServerSentEvent, None, None]:
        return self.client.chat_completions(messages, stream, thinking, **kwargs)

    async def chat_completions_async(
        self,
        messages: list,
        *,
        stream: bool = False,
        thinking: bool = False,
        **kwargs
    ) -> ChatCompletion | AsyncGenerator[
        ServerSentEvent, ChatCompletion | None]:
        return await self.client.chat_completions_async(messages, stream, thinking, **kwargs)
