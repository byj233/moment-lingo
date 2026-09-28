import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

import dashscope
from dashscope.audio.asr import Recognition, RecognitionCallback

from src.config import AIConf

logger = logging.getLogger(__name__)


class AsrClient(ABC):
    format = 'pcm'

    @abstractmethod
    def open(self, callback: Any):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def send(self, data: bytes):
        pass


class FunAsrClient(AsrClient):
    dashscope.api_key = AIConf.bailian.api_key
    client: Optional[Recognition] = None

    def open(self, callback: RecognitionCallback):
        try:
            self.client = Recognition(
                model='fun-asr-realtime-2026-02-28',
                format=self.format,
                sample_rate=16000,
                heartbeat=True,
                callback=callback,
                language_hints=['zh', 'en'],
                max_sentence_silence=800,
                speech_noise_threshold=0.1
            )

            self.client.start()
        except Exception as e:
            logger.error(f'FunAsrClient开启连接失败 {e}')

    def close(self):
        try:
            if not self.client:
                raise Exception('FunAsrClient未开启')

            self.client.stop()
        except Exception as e:
            logger.error(f'FunAsrClient关闭连接失败 已强制关闭 {e}')
        finally:
            self.client = None

    def send(self, data: bytes):
        try:
            if not self.client:
                raise Exception('FunAsrClient未开启')
            self.client.send_audio_frame(data)
        except Exception as e:
            logger.error(f'FunAsrClient发送数据失败 {e}')
