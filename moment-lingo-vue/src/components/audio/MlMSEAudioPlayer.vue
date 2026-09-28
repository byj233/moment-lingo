<script lang="ts" setup>
// 基于MediaSource的音频播放器
import { onMounted, onUnmounted, ref, useTemplateRef } from 'vue';
import { ttsStream } from '@/api/tts.ts';
import { b64ToUint8Array } from '@/utils/common.ts';

const props = defineProps<{
  content: string;
  model: string;
  voiceKey: string;
}>();


const player = useTemplateRef('player');
const mediaSource = new MediaSource();
const isPlaying = ref(false);
const isLoading = ref(false);
const isAllLoaded = ref(false);


function ttsMseHandler(appendB64Audio: (data: string) => void, completeHandler: () => void) {
  isLoading.value = true;
  ttsStream({
    content: props.content,
    model: props.model,
    voiceKey: props.voiceKey
  }, {
    onProcessing: (e: any) => {
      isLoading.value = false;
      isPlaying.value = true;
      const data = JSON.parse(e.data);
      appendB64Audio(data.content);
    },
    onEnd: completeHandler,
    onError: () => {
      isLoading.value = false;
      isPlaying.value = false;
      isAllLoaded.value = false;
    }
  });
}

function ttsHandler() {
  const chunks: Uint8Array[] = [];
  isLoading.value = true;

  ttsStream({
    content: props.content,
    model: props.model,
    voiceKey: props.voiceKey
  }, {
    onProcessing: (e: any) => {
      const data = JSON.parse(e.data);
      chunks.push(b64ToUint8Array(data.content));
    },
    onEnd: () => {
      const totalLength = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
      const concatenated = new Uint8Array(totalLength);
      let offset = 0;
      chunks.forEach(chunk => {
        concatenated.set(chunk, offset);
        offset += chunk.length;
      });

      const audioBlob = new Blob([concatenated], { type: 'audio/mpeg' });
      player.value!.src = URL.createObjectURL(audioBlob);

      isAllLoaded.value = true;
      isLoading.value = false;
      isPlaying.value = true;
    },
    onError: () => {
      isLoading.value = false;
      isPlaying.value = false;
      isAllLoaded.value = false;
    }
  });
}

function sourceOpenHandler() {
  const sourceBuffer = mediaSource.addSourceBuffer('audio/mpeg');
  const chunkQueue: Uint8Array[] = [];
  let isAppending = false;

  const appendBuffer = () => {
    if (isAppending || chunkQueue.length === 0 || sourceBuffer.updating) {
      return;
    }

    isAppending = true;
    const data = chunkQueue.shift()!;
    sourceBuffer.appendBuffer(data as any);
  };

  sourceBuffer.addEventListener('updateend', () => {
    isAppending = false;
    appendBuffer();
  });

  const handleChunkComplete = () => {
    const interval = setInterval(() => {
      if (mediaSource.readyState === 'open') {
        mediaSource.endOfStream();
        isAllLoaded.value = true;
        clearInterval(interval);
      }
    }, 100);
  };

  ttsMseHandler((b64String: string) => {
    chunkQueue.push(b64ToUint8Array(b64String));
    appendBuffer();
  }, handleChunkComplete);
}

function tts() {
  isAllLoaded.value = false;
  isLoading.value = true;
  if (!MediaSource.isTypeSupported('audio/mpeg')) {
    console.log('MediaSource不支持audio/mpeg');
    ttsHandler();
    return;
  }

  mediaSource.addEventListener('sourceopen', sourceOpenHandler);
  player.value!.src = URL.createObjectURL(mediaSource);
}

function onPlay() {
  if (isAllLoaded.value) {
    isPlaying.value = true;
  }
  player.value!.play();
}

function onPause() {
  if (isPlaying.value) {
    isPlaying.value = false;
    player.value!.pause();
  }
}

function onToggle(toStart: boolean = false) {
  if (toStart) {
    player.value!.currentTime = 0;
  }
  player.value!.paused ? player.value!.play() : player.value!.pause();
}

function onEnded() {
  isPlaying.value = false;
}

onMounted(() => {
  if (player.value) {
    player.value.addEventListener('play', onPlay);
    player.value.addEventListener('pause', onPause);
    player.value.addEventListener('ended', onEnded);
  }
});

onUnmounted(() => {
  if (player.value) {
    player.value.removeEventListener('play', onPlay);
    player.value.removeEventListener('pause', onPause);
    player.value.removeEventListener('ended', onEnded);
  }
});

defineExpose({ tts, onPlay, onToggle, onPause, isPlaying, isLoading, isAllLoaded });
</script>

<template>
  <audio ref="player"/>
</template>
