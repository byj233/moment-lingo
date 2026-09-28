<script lang="ts" setup>
// 基于 WebSocket 的流式音频播放器（MSE + AudioContext 降级）
import { onMounted, onUnmounted, useTemplateRef } from 'vue';
import { b64ToUint8Array } from '@/utils/common.ts';

const player = useTemplateRef('player');
const isMseSupported = window.MediaSource && MediaSource.isTypeSupported('audio/mpeg');

// --- MSE 状态 ---
let mediaSource: MediaSource | null = null;
let sourceBuffer: SourceBuffer | null = null;
let isAppending = false;
let audioChunk: Uint8Array[] = [];

// --- AudioContext 状态 ---
let audioCtx: AudioContext | null = null;
let nextPlayTime = 0;
let sourceNodes: AudioBufferSourceNode[] = [];
let fullBuffer = new Uint8Array(0);
let pendingBytes = 0;
let decodedSamples = 0;
let isDecoding = false;
const MIN_DECODE_BYTES = 8192;

function concatUint8Arrays(a: Uint8Array, b: Uint8Array) {
  const c = new Uint8Array(a.length + b.length);
  c.set(a, 0);
  c.set(b, a.length);
  return c;
}

function init() {
  if (isMseSupported) {
    initMse();
  } else {
    initAudioContext();
  }
}

// --- MSE 实现 ---
function initMse() {
  mediaSource = new MediaSource();
  mediaSource.addEventListener('sourceopen', () => {
    sourceBuffer = mediaSource!.addSourceBuffer('audio/mpeg');
    sourceBuffer.addEventListener('updateend', () => {
      isAppending = false;
      appendBuffer();
    });
  });
  if (player.value) {
    player.value.src = URL.createObjectURL(mediaSource);
  }
}

function appendBuffer() {
  if (isAppending || audioChunk.length === 0 || !sourceBuffer || sourceBuffer.updating) {
    return;
  }
  isAppending = true;
  const data = audioChunk.shift()!;
  sourceBuffer.appendBuffer(data as any);
}

// --- AC 实现 ---
function initAudioContext() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
  }
  if (audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
}

async function processCumulativeDecode() {
  if (isDecoding || !audioCtx || fullBuffer.length === 0) return;
  if (pendingBytes < MIN_DECODE_BYTES) return;

  isDecoding = true;
  const bufferToDecode = fullBuffer.slice().buffer;
  const currentPending = pendingBytes;

  try {
    const audioBuffer = await audioCtx.decodeAudioData(bufferToDecode);
    if (audioBuffer.length > decodedSamples) {
      const newSamplesCount = audioBuffer.length - decodedSamples;
      const newBuffer = audioCtx.createBuffer(
          audioBuffer.numberOfChannels,
          newSamplesCount,
          audioBuffer.sampleRate
      );

      for (let i = 0; i < audioBuffer.numberOfChannels; i++) {
        const channelData = audioBuffer.getChannelData(i);
        newBuffer.copyToChannel(channelData.subarray(decodedSamples), i);
      }

      decodedSamples = audioBuffer.length;
      pendingBytes -= currentPending;
      if (pendingBytes < 0) pendingBytes = 0;

      const source = audioCtx.createBufferSource();
      source.buffer = newBuffer;
      source.connect(audioCtx.destination);

      const currentTime = audioCtx.currentTime;
      if (nextPlayTime < currentTime) {
        nextPlayTime = currentTime + 0.02;
      }

      source.start(nextPlayTime);
      nextPlayTime += newBuffer.duration;
      sourceNodes.push(source);

      source.onended = () => {
        const idx = sourceNodes.indexOf(source);
        if (idx > -1) sourceNodes.splice(idx, 1);
      };
    } else {
      pendingBytes -= currentPending;
      if (pendingBytes < 0) pendingBytes = 0;
    }
  } catch (e) {
    // 解码异常通常是因为截断
  }

  isDecoding = false;

  if (pendingBytes >= MIN_DECODE_BYTES) {
    await processCumulativeDecode();
  }
}

// --- 暴露给外部的方法 ---

function appendAudio(base64Data: string) {
  const chunk = b64ToUint8Array(base64Data);
  if (isMseSupported) {
    audioChunk.push(chunk);
    appendBuffer();
    player.value?.play().catch(() => {
    });
  } else {
    initAudioContext();
    fullBuffer = concatUint8Arrays(fullBuffer, chunk);
    pendingBytes += chunk.length;
    processCumulativeDecode();
  }
}

function interrupt() {
  if (isMseSupported) {
    audioChunk = [];
    isAppending = false;
    if (sourceBuffer) {
      try {
        if (sourceBuffer.updating) {
          sourceBuffer.abort();
        }
        player.value?.pause();
        if (sourceBuffer.buffered.length > 0) {
          sourceBuffer.remove(0, Infinity);
          if (mediaSource && player.value) {
            player.value.src = URL.createObjectURL(mediaSource);
          }
        }
      } catch (e) {
        console.error('Interrupt MSE error', e);
      }
    }
  } else {
    if (audioCtx) {
      sourceNodes.forEach(source => {
        try {
          source.stop();
        } catch (e) {
        }
        source.disconnect();
      });
    }
    sourceNodes = [];
    nextPlayTime = 0;
    fullBuffer = new Uint8Array(0);
    pendingBytes = 0;
    decodedSamples = 0;
    isDecoding = false;
  }
}

onMounted(() => {
  init();
});

onUnmounted(() => {
  interrupt();
  if (audioCtx && audioCtx.state !== 'closed') {
    audioCtx.close().catch(console.warn);
  }
});

defineExpose({ appendAudio, interrupt, isMseSupported });
</script>

<template>
  <audio v-if="isMseSupported" ref="player"/>
</template>
