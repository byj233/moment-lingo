<script lang="ts" setup>
// 基于AudioContext的音频播放器
import { onUnmounted, ref } from 'vue';
import { ttsStream } from '@/api/tts.ts';
import { b64ToUint8Array } from '@/utils/common.ts';

const props = defineProps<{
  content: string;
  model: string;
  voiceKey: string;
}>();

const isPlaying = ref(false);
const isLoading = ref(false);
const isAllLoaded = ref(false);

let audioCtx: AudioContext | null = null;
let nextPlayTime = 0;
let sourceNodes: AudioBufferSourceNode[] = [];

// 【核心修复】累积解码（Cumulative Decoding）状态
let fullBuffer = new Uint8Array(0); // 完整累积的 MP3 字节
let pendingBytes = 0;               // 尚未参与成功解码的新增字节数
let decodedSamples = 0;             // 已经成功解码播放的样本数（长度）
let isDecoding = false;
let streamEnded = false;

// 缓存最终解码出来的完整 AudioBuffer
let cachedAudioBuffer: AudioBuffer | null = null;

// 避免太频繁解码消耗 CPU（至少积攒多少字节再解）
const MIN_DECODE_BYTES = 8192;

function concatUint8Arrays(a: Uint8Array, b: Uint8Array) {
  const c = new Uint8Array(a.length + b.length);
  c.set(a, 0);
  c.set(b, a.length);
  return c;
}

function initAudioContext() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
  }
  if (audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
}

// 注意：如果是使用缓存重播，我们只需要停止当前正在播放的节点并重置时间，
// 不应该清空 fullBuffer 和 cachedAudioBuffer
function resetPlaybackState() {
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
  isPlaying.value = false;
}

// 彻底重置状态（用于网络请求新流时）
function resetAllState() {
  resetPlaybackState();

  fullBuffer = new Uint8Array(0);
  pendingBytes = 0;
  decodedSamples = 0;
  cachedAudioBuffer = null;

  isDecoding = false;
  streamEnded = false;

  isLoading.value = false;
  isAllLoaded.value = false;
}

function checkEnded() {
  if (streamEnded && pendingBytes === 0 && sourceNodes.length === 0) {
    isPlaying.value = false;
    isAllLoaded.value = true;
  }
}

// 从缓存中直接完整播放（0 网络请求，0 分块处理）
function playFromCache() {
  if (!audioCtx || !cachedAudioBuffer) return;

  resetPlaybackState(); // 先停止当前的
  initAudioContext();

  const source = audioCtx.createBufferSource();
  source.buffer = cachedAudioBuffer;
  source.connect(audioCtx.destination);

  source.start(audioCtx.currentTime);
  sourceNodes.push(source);

  isPlaying.value = true;

  source.onended = () => {
    const idx = sourceNodes.indexOf(source);
    if (idx > -1) sourceNodes.splice(idx, 1);
    isPlaying.value = false;
  };
}

// 累积解码核心逻辑：将所有历史收到的字节作为一个完整 MP3 统一解码，截取出新增的部分播放。
// 这样浏览器就不会在每个分片头尾乱加静音（Padding），彻底解决 MP3 块重叠导致的卡顿破音！
async function processCumulativeDecode() {
  if (isDecoding || !audioCtx || fullBuffer.length === 0) return;

  // 如果流还没结束，且新积攒的数据太少，就等一等再解（避免每收到一点点都全量解码导致卡顿）
  if (!streamEnded && pendingBytes < MIN_DECODE_BYTES) return;

  isDecoding = true;

  // 必须复制一份 buffer 传给 decodeAudioData，否则原 buffer 会被转移剥夺
  const bufferToDecode = fullBuffer.slice().buffer;
  const currentPending = pendingBytes;

  try {
    const audioBuffer = await audioCtx.decodeAudioData(bufferToDecode);

    // 如果流已经结束，将最终完整的 audioBuffer 存入缓存
    if (streamEnded) {
      cachedAudioBuffer = audioBuffer;
    }

    // 如果解码出来的新样本总数 > 之前已经播放的样本数，说明有了有效的新增音频
    if (audioBuffer.length > decodedSamples) {
      const newSamplesCount = audioBuffer.length - decodedSamples;

      // 创建一个只包含新增音频的缓冲区（切片）
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
      pendingBytes -= currentPending; // 扣除这次参与解码的字节
      if (pendingBytes < 0) pendingBytes = 0;

      const source = audioCtx.createBufferSource();
      source.buffer = newBuffer;
      source.connect(audioCtx.destination);

      const currentTime = audioCtx.currentTime;
      // 预留微小的安全缓冲（20ms），确保两块之间完全无缝拼接且不欠载
      if (nextPlayTime < currentTime) {
        nextPlayTime = currentTime + 0.02;
      }

      source.start(nextPlayTime);
      nextPlayTime += newBuffer.duration;
      sourceNodes.push(source);

      source.onended = () => {
        const idx = sourceNodes.indexOf(source);
        if (idx > -1) sourceNodes.splice(idx, 1);
        checkEnded();
      };

      if (audioCtx.state === 'running') {
        isPlaying.value = true;
      }
    } else {
      // 增加的字节没有产生新的样本（可能都是帧头），直接跳过
      pendingBytes -= currentPending;
      if (pendingBytes < 0) pendingBytes = 0;
    }
  } catch (e) {
    // 解码失败通常是因为 MP3 被截断。我们只需吞掉异常，下一次带上新收到的字节再一起解即可。
  }

  isDecoding = false;

  // 继续检查是否需要解码（可能在刚刚解码期间又收到了很多新数据）
  if ((pendingBytes >= MIN_DECODE_BYTES) || (streamEnded && pendingBytes > 0)) {
    await processCumulativeDecode();
  } else {
    checkEnded();
  }
}

function tts() {
  // 【新增缓存逻辑】如果之前已经完整加载完毕，且缓存存在，直接重播，不再发请求
  if (isAllLoaded.value && cachedAudioBuffer) {
    playFromCache();
    return;
  }

  resetAllState();
  initAudioContext();
  isLoading.value = true;

  ttsStream({
    content: props.content,
    model: props.model,
    voiceKey: props.voiceKey
  }, {
    onProcessing: (e: any) => {
      isLoading.value = false;
      const data = JSON.parse(e.data);
      const chunk = b64ToUint8Array(data.content);

      fullBuffer = concatUint8Arrays(fullBuffer, chunk);
      pendingBytes += chunk.length;

      processCumulativeDecode();
    },
    onEnd: () => {
      streamEnded = true;
      processCumulativeDecode();
    },
    onError: () => {
      isLoading.value = false;
      isPlaying.value = false;
      isAllLoaded.value = false;
      streamEnded = true;
    }
  });
}

async function onPlay() {
  if (isAllLoaded.value && !isPlaying.value && sourceNodes.length === 0) {
    playFromCache();
    return;
  }
  if (audioCtx && audioCtx.state === 'suspended') {
    await audioCtx.resume();
    isPlaying.value = true;
  }
}

async function onPause() {
  if (audioCtx && audioCtx.state === 'running') {
    await audioCtx.suspend();
    isPlaying.value = false;
  }
}

function onToggle(toStart: boolean = false) {
  if (toStart) {
    if (isAllLoaded.value && cachedAudioBuffer) {
      playFromCache();
    } else {
      tts();
    }
    return;
  }

  if (isPlaying.value) {
    onPause();
  } else {
    onPlay();
  }
}

onUnmounted(() => {
  resetAllState();
  if (audioCtx && audioCtx.state !== 'closed') {
    audioCtx.close().catch(console.warn);
  }
});

defineExpose({ tts, onPlay, onPause, onToggle, isPlaying, isLoading, isAllLoaded });
</script>