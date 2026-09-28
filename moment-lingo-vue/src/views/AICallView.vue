<script lang="ts" setup>
import Recorder from 'recorder-core';
import 'recorder-core/src/engine/pcm';
import 'recorder-core/src/extensions/waveview';
import { computed, nextTick, onMounted, onUnmounted, ref, useTemplateRef } from 'vue';
import { MlMessage } from '@/utils/feedBack.ts';
import MlMarkdown from '@/components/MlMarkdown.vue';
import { wsUrl } from '@/config';
import { useUserStore } from '@/store/userStore.ts';
import { options } from '@/api/auth.ts';
import { listVoices } from '@/api/tts.ts';
import { useMobileDetector } from '@/utils/mobileDetector.ts';
import MlNavbar from '@/components/layout/MlNavbar.vue';
import MlWsAudioPlayer from '@/components/audio/MlWsAudioPlayer.vue';

interface Message {
  role: string;
  content: string;
}

interface Voice {
  voiceId: number;
  voiceKey: string;
  voiceName: string;
  tags: string[];
  model: string;
  type: string;
}


const recWaveRef = useTemplateRef('rec-wave');
const wsPlayerRef = useTemplateRef('ws-player');
const voices = ref<Array<Voice>>();
const selectedVoiceId = ref<number>();
const messages = ref<Message[]>([]);
const messageContainerRef = useTemplateRef('message-container');
const isConnecting = ref(false);
const isConnected = ref(false);
const asrContent = ref('');
const settingsModalVisible = ref(false);
const settingsPopupVisible = ref(false);
const isTalking = ref(false);
const messagesVisible = ref(false);
const memoryEnabled = ref(true);
const userStore = useUserStore();
const { isMobile } = useMobileDetector();
const TTS_MODEL = ['doubao-tts'];

const callDuration = ref(0);
let timer: any = null;
const MAX_DURATION = 10 * 60;

const formattedDuration = computed(() => {
  const m = Math.floor(callDuration.value / 60).toString().padStart(2, '0');
  const s = (callDuration.value % 60).toString().padStart(2, '0');
  return `${ m }:${ s }`;
});

function startTimer() {
  callDuration.value = 0;
  timer = setInterval(() => {
    callDuration.value++;
    if (callDuration.value >= MAX_DURATION) {
      MlMessage.warning('通话已达到最长10分钟限制，自动挂断');
      disconnect();
    }
  }, 1000);
}

function stopTimer() {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
  callDuration.value = 0;
}


let recorder: any;
let wave: any;
let ws: WebSocket;
let lastMessageIndex = -1;
let isInterrupted = false;

function initWebsocket() {
  return new Promise((resolve: any, reject: any) => {
    let url = `${ wsUrl }/ai/call?token=${ userStore.userInfo?.token }&voiceId=${ selectedVoiceId.value }`;
    if (memoryEnabled.value) {
      url += '&memory=open';
    }
    ws = new WebSocket(url);
    ws.onopen = () => {
      console.log('websocket 连接成功');
      wsMsgHandler(resolve);
    };
    ws.onerror = (err: any) => {
      console.log('websocket 连接失败', err);
      reject(err);
    };
  });
}

function initRecorder() {
  recorder = Recorder({
    type: 'pcm',
    sampleRate: 16000,
    bitRate: 16,
    // 实时获取音频能量（用于判断是否静默）
    onProcess: function (buffers: any, powerLevel: any, _: any, bufferSampleRate: any) {
      if (wave && isConnected.value && !isMobile.value) {
        wave.input(buffers[buffers.length - 1], powerLevel, bufferSampleRate);
      }
    },
    takeoffEncodeChunk: function (pcmChunk: Uint8Array) {
      ws.send(pcmChunk);
    }
  });

  return new Promise((resolve: any, reject: any) => {
    recorder.open(
        () => {
          if (!isMobile.value) {
            const interval = setInterval(() => {
              if (recWaveRef.value) {
                wave = Recorder.WaveView({ elem: recWaveRef.value });
                clearInterval(interval);
              }
            }, 100);
          }

          recorder.start();
          console.log('录音设备打开成功');
          resolve();
        },
        (err: any) => {
          console.log('录音初始化失败：', err);
          MlMessage.error('录音初始化失败');
          reject(err);
        }
    );
  });
}

function appendAssistantMessage() {
  messages.value.push({
    role: 'assistant',
    content: ''
  });
  ++lastMessageIndex;
}

function appendUserMessage() {
  messages.value.push({
    role: 'user',
    content: ''
  });
  ++lastMessageIndex;
}

function asrHandler(data: any) {
  isInterrupted = true;
  isTalking.value = true;
  wsPlayerRef.value?.interrupt();
  asrContent.value = data.content.text;

  if (data.content.sentenceEnd) {
    setTimeout(() => {
      asrContent.value = '';
    }, 500);
    isInterrupted = false;
    isTalking.value = false;

    messages.value[lastMessageIndex]!.content = data.content.text;
    appendAssistantMessage();
    nextTick().then(() => {
      scrollToBottom();
    });
  }
}

function aiHandler(data: any) {
  if (data.content.event === 'PROCESSING') {
    if (isInterrupted) {
      return;
    }
    messages.value[lastMessageIndex]!.content += data.content.text;
  } else if (data.content.event === 'END') {
    appendUserMessage();
  }
  nextTick().then(() => {
    scrollToBottom();
  });
}

function ttsHandler(data: any) {
  if (!isInterrupted) {
    wsPlayerRef.value?.appendAudio(data.content);
  }
}

function infoHandler(data: any, onStart?: () => void) {
  const event = data.content.event;
  const text = data.content.text;

  if (event === 'ERROR') {
    MlMessage.error(text);
    disconnect();
  } else if (event === 'START') {
    MlMessage.success(text);
    isConnecting.value = false;
    isConnected.value = true;
    startTimer();
    onStart?.();
  }
}

function wsMsgHandler(onStart?: () => void) {
  ws.onmessage = (event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data);

      if (data.type === 'ASR') {
        asrHandler(data);
      } else if (data.type === 'AI') {
        aiHandler(data);
      } else if (data.type === 'TTS') {
        ttsHandler(data);
      } else if (data.type === 'INFO') {
        infoHandler(data, onStart);
      }
    } catch (err) {
      console.log('处理WebSocket消息失败', err);
    }
  };
}

function checkBrowserSupport() {
  if (!(window.MediaSource && MediaSource.isTypeSupported('audio/mpeg'))) {
    console.log('MediaSource不支持audio/mpeg，将使用AudioContext降级方案');
  }
}

async function connect() {
  checkBrowserSupport();
  try {
    isConnecting.value = true;

    await options();
    await initWebsocket();
    await initRecorder();
    wsMsgHandler();

    appendUserMessage();
  } catch (err) {
    console.error('接通失败', err);
    MlMessage.error('接通失败');
    isConnected.value = false;
    isConnecting.value = false;
  }
}

function disconnect() {
  stopTimer();
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.close();
  } else if (ws) {
    ws.close();
  }
  wsPlayerRef.value?.interrupt();
  isConnected.value = false;
  isConnecting.value = false;
  messages.value = [];
  isTalking.value = false;
  recorder.stop(() => {
    recorder.close();
    console.log('录音设备关闭成功');
  });
  lastMessageIndex = -1;
  isInterrupted = false;
  asrContent.value = '';
}

function scrollToBottom() {
  messageContainerRef.value!.scrollTop = messageContainerRef.value!.scrollHeight;
}

function handleKeyDown(e: KeyboardEvent) {
  if (e.code === 'Space' && e.target === document.body) {
    e.preventDefault();
    if (isConnected.value) {
      disconnect();
    } else {
      connect();
    }
  }
}

function getPickerOptions() {
  return voices.value?.map(item => ({
    data: item,
    value: item.voiceId
  }));
}

function onConfirm(e: any) {
  selectedVoiceId.value = e[0];
  settingsPopupVisible.value = false;
}


onMounted(async () => {
  document.documentElement.setAttribute('theme-mode', 'dark');
  checkBrowserSupport();

  const resp = await listVoices();
  const v = resp.data as Voice[];

  voices.value = v.filter((item) => TTS_MODEL.includes(item.model));
  selectedVoiceId.value = voices.value[0]!.voiceId as number;
  window.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  document.documentElement.removeAttribute('theme-mode');
  if (isConnected.value) {
    disconnect();
  }
  window.removeEventListener('keydown', handleKeyDown);
});
</script>

<template>
  <div>
    <!-- web -->
    <div class="hidden md:block min-h-screen pt-24 pb-6 px-4 sm:px-6 lg:px-8 bg-canvas">
      <div
          class="max-w-7xl mx-auto h-[calc(100vh-140px)] min-h-[600px] grid grid-cols-1 md:grid-cols-12 gap-4 lg:gap-6">

        <!-- 左侧：控制台 -->
        <div class="md:col-span-5 lg:col-span-4 xl:col-span-3 flex flex-col gap-4 lg:gap-6 h-full min-w-0">
          <!-- 主控制卡片 -->
          <div
              class="flex-1 bg-surface-card rounded-[12px] border border-hairline p-4 lg:p-6 flex flex-col relative overflow-hidden transition-all">
            <!-- 顶部工具栏 -->
            <div class="flex flex-wrap justify-between items-center gap-3 z-10 mb-4">
              <div class="flex items-center gap-2 px-3 py-1.5 bg-surface-soft rounded-full flex-shrink-0">
                <div
                    :class="['w-2 h-2 rounded-full animate-pulse', isConnected ? 'bg-success' : 'bg-muted-soft']"></div>
                <span class="text-xs font-medium text-body whitespace-nowrap">{{
                    isConnected ? '通话中 ' + formattedDuration : isConnecting ? '连接中' : '空闲'
                  }}</span>
              </div>

              <div class="flex items-center gap-2 flex-shrink-0">
                <button
                    :class="['px-3 py-1.5 rounded-full text-xs font-medium transition-all flex items-center gap-1.5 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer',
                      memoryEnabled ? 'bg-primary/10 text-primary' : 'bg-surface-soft text-muted hover:bg-hairline']"
                    :disabled="isConnecting || isConnected"
                    @click="memoryEnabled = !memoryEnabled"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                        d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                        stroke-linecap="round" stroke-linejoin="round"
                        stroke-width="2"/>
                  </svg>
                  长期记忆
                </button>

                <button
                    :disabled="isConnecting || isConnected"
                    class="p-2 text-muted-soft hover:text-primary hover:bg-primary/5 rounded-full transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                    @click="settingsModalVisible = true">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                        d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
                        stroke-linecap="round" stroke-linejoin="round"
                        stroke-width="2"></path>
                  </svg>
                </button>
              </div>
            </div>

            <!-- 核心交互区 -->
            <div class="flex-1 flex flex-col items-center justify-center z-10 -mt-6">
              <div class="relative">
                <!-- 呼吸光环 -->
                <template v-if="isConnected || isConnecting">
                  <div
                      class="absolute inset-0 bg-primary rounded-full opacity-20 animate-ping"/>
                </template>

                <template v-if="isConnected">
                  <div
                      class="absolute inset-[-12px] bg-primary rounded-full opacity-10 animate-pulse"/>
                </template>

                <button
                    :class="[
                      'relative w-28 h-28 lg:w-32 lg:h-32 rounded-full flex items-center justify-center transition-all duration-500 shadow-2xl transform hover:scale-105 active:scale-95 cursor-pointer',
                      isConnecting ? 'bg-surface-soft cursor-not-allowed' :
                      isConnected ? 'bg-error hover:bg-red-700 shadow-error/30' :
                      'bg-primary hover:bg-primary-active shadow-primary/20'
                    ]"
                    :disabled="isConnecting"
                    @click="isConnected ? disconnect() : connect()"
                >
                  <template v-if="isConnecting">
                    <svg class="w-10 h-10 text-primary animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                            fill="currentColor"></path>
                    </svg>
                  </template>
                  <template v-else-if="isConnected">
                    <svg class="w-10 h-10 lg:w-12 lg:h-12 text-white" fill="none" stroke="currentColor"
                         viewBox="0 0 24 24">
                      <path d="M6 18L18 6M6 6l12 12" stroke-linecap="round" stroke-linejoin="round"
                            stroke-width="2"></path>
                    </svg>
                  </template>
                  <template v-else>
                    <svg class="w-10 h-10 lg:w-12 lg:h-12 text-white" fill="none" stroke="currentColor"
                         viewBox="0 0 24 24">
                      <path
                          d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                          stroke-linecap="round" stroke-linejoin="round"
                          stroke-width="2"></path>
                    </svg>
                  </template>
                </button>
              </div>

              <p class="mt-6 lg:mt-8 text-base lg:text-lg font-medium text-ink text-center">
                {{ isConnected ? '点击挂断' : isConnecting ? '正在连接...' : '开始对话' }}
              </p>
              <p class="mt-2 text-xs lg:text-sm text-muted text-center">
                {{ isConnected ? 'AI 正在聆听中...' : '按空格键也可快速开始' }}
              </p>
            </div>

            <!-- 波形区域 -->
            <div
                class="mt-auto h-20 lg:h-24 w-full bg-surface-soft rounded-[8px] overflow-hidden relative border border-hairline flex-shrink-0">
              <template v-if="!isConnected">
                <div
                    class="absolute inset-0 flex items-center justify-center text-muted-soft text-xs lg:text-sm">
                  等待音频输入...
                </div>
              </template>
              <template v-else>
                <div ref="rec-wave" class="w-full h-full opacity-80"></div>
              </template>
            </div>

            <!-- 设置弹窗 -->
            <a-modal :ok-button-props="{status: 'success',type:'primary'}" :visible="settingsModalVisible"
                     hide-cancel ok-text="确认" simple title="音色选择" width="400px"
                     @ok="settingsModalVisible = false">
              <div class="flex items-center justify-center">
                <a-select v-model="selectedVoiceId" :style="{width:'240px'}">
                  <template v-for="item in voices" :key="item.voiceId">
                    <a-option :label="item.voiceName" :value="item.voiceId">
                      <a-space :style="{width:'240px'}">
                        <a-space class="w-14">{{ item.voiceName }}</a-space>
                        <a-space>
                          <template v-if="item.type === 'us'">
                            <a-tag color="purple">美音</a-tag>
                          </template>
                          <template v-else>
                            <a-tag color="purple">英音</a-tag>
                          </template>
                          <template v-for="tag in item.tags">
                            <a-tag color="arcoblue">{{ tag }}</a-tag>
                          </template>
                        </a-space>
                      </a-space>
                    </a-option>
                  </template>
                </a-select>
              </div>
            </a-modal>
          </div>

          <!-- ASR 实时识别卡片 -->
          <template v-if="isConnected">
            <div
                class="bg-surface-card/80 backdrop-blur rounded-[8px] p-4 border border-hairline animate-fade-in-up flex-shrink-0 max-h-32 lg:max-h-40 overflow-y-auto">
              <div class="flex items-start gap-3">
                <div class="p-2 bg-primary/5 rounded-[6px] text-primary flex-shrink-0">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                        d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                        stroke-linecap="round" stroke-linejoin="round"
                        stroke-width="2"></path>
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-medium text-primary/70 uppercase tracking-[1.5px] mb-1">实时识别</p>
                  <p class="text-ink text-[14px] font-medium leading-relaxed break-words">
                    {{ asrContent || '...' }}
                  </p>
                </div>
              </div>
            </div>
          </template>
        </div>

        <!-- 右侧：对话列表 -->
        <div
            class="md:col-span-7 lg:col-span-8 xl:col-span-9 bg-surface-card rounded-[12px] border border-hairline flex flex-col overflow-hidden h-full">
          <!-- 头部 -->
          <div
              class="px-4 lg:px-6 py-4 border-b border-hairline flex justify-between items-center">
            <div class="flex items-center gap-2">
              <h2 class="text-[18px] font-medium text-ink">对话记录</h2>
            </div>
            <span class="text-caption text-muted">{{ messages.length }} 条消息</span>
          </div>

          <!-- 列表区域 -->
          <div ref="message-container"
               class="flex-1 overflow-y-auto p-4 lg:p-6 space-y-4 bg-canvas scroll-smooth en-font">
            <template v-if="messages.length > 0">
              <template v-for="(item, index) in messages">
                <div v-if="item.content !== '' || index === messages.length - 1"
                     :class="['flex w-full', item.role === 'user' ? 'justify-end' : 'justify-start']">
                  <div class="max-w-[90%] md:max-w-[80%] lg:max-w-[70%]">
                    <!-- 气泡 -->
                    <div :class="['px-4 rounded-[8px] text-[14px] leading-relaxed',
                        item.role === 'user'
                          ? 'bg-primary text-on-primary'
                          : 'bg-surface-soft text-ink']">
                      <template v-if="item.content === ''">
                        <div class="flex gap-1.5 py-5">
                          <div class="w-1.5 h-1.5 bg-current rounded-full animate-bounce opacity-50"></div>
                          <div class="w-1.5 h-1.5 bg-current rounded-full animate-bounce opacity-50"
                               style="animation-delay: 0.2s"></div>
                          <div class="w-1.5 h-1.5 bg-current rounded-full animate-bounce opacity-50"
                               style="animation-delay: 0.4s"></div>
                        </div>
                      </template>
                      <template v-else>
                        <ml-markdown :class="item.role === 'user' ? 'prose-invert' : ''" :content="item.content"/>
                      </template>
                    </div>
                  </div>
                </div>
              </template>
            </template>

            <!-- 空状态 -->
            <template v-else>
              <div class="h-full flex flex-col items-center justify-center text-muted">
                <div class="w-14 h-14 lg:w-16 lg:h-16 bg-surface-soft rounded-[8px] flex items-center justify-center mb-4">
                  <svg class="w-7 h-7 lg:w-8 lg:h-8 text-muted-soft" fill="none" stroke="currentColor"
                       viewBox="0 0 24 24">
                    <path
                        d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                        stroke-linecap="round" stroke-linejoin="round"
                        stroke-width="1.5"></path>
                  </svg>
                </div>
                <p class="text-[14px] text-muted">暂无对话，点击左侧按钮开始通话</p>
              </div>
            </template>
          </div>
        </div>

      </div>
    </div>

    <!-- h5 -->
    <div class="md:hidden h-screen flex flex-col">
      <div class="h-12 flex-shrink-0 relative z-20">
        <ml-navbar title="口语陪练"/>
      </div>
      <div class="fixed top-0 left-0 h-screen w-screen tech-grid">
        <div class="flex items-center  justify-center h-full w-full">
          <img :class="{'blur-2xl':messagesVisible}"
               :src="messagesVisible?'':'/icon/ai-call.webp'" alt="ai-call"
               class="h-36 w-36">
        </div>
      </div>

      <!-- 主内容区域 -->
      <div class="flex-1 relative z-20 flex flex-col overflow-hidden">
        <!-- 顶部左侧悬浮计时器 -->
        <template v-if="isConnected">
          <div class="absolute top-4 left-4 z-30">
            <div
                class="px-3 py-1.5 rounded-full text-xs font-medium bg-white/10 text-white border border-white/20 backdrop-blur-md flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
              {{ formattedDuration }}
            </div>
          </div>
        </template>


        <!-- 顶部悬浮记忆按钮 -->
        <div class="absolute top-4 right-4 z-30">
          <button
              :class="['px-3 py-1.5 rounded-full text-xs font-medium transition-all flex items-center gap-1.5 backdrop-blur-md',
                memoryEnabled ? 'bg-indigo-500/80 text-white' : 'bg-white/10 text-gray-200 border border-white/20']"
              :disabled="isConnecting || isConnected"
              @click="memoryEnabled = !memoryEnabled"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                  stroke-linecap="round" stroke-linejoin="round"
                  stroke-width="2"/>
            </svg>
            长期记忆
          </button>
        </div>

        <!-- ASR文本显示区域 -->
        <template v-if="isConnected">
          <div class="px-6 mb-4 mt-16">
            <div
                class="bg-white/10 backdrop-blur-md rounded-xl p-4 shadow-lg border border-white/20 transform transition-all duration-300 hover:bg-white/15">
              <div class="flex items-start gap-3">
                <!-- 麦克风图标 -->
                <svg class="w-5 h-5 flex-shrink-0 text-blue-300 mt-0.5" fill="none" stroke="currentColor"
                     viewBox="0 0 24 24">
                  <path
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                      stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                </svg>

                <!-- 识别内容展示 -->
                <div class="flex-1">
                  <p class="text-sm font-medium text-blue-200 mb-1">正在识别:</p>
                  <p class="text-base text-white font-medium">
                    {{ asrContent || '正在听...' }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- 对话记录区域 -->
        <transition name="fade">
          <template v-if="messagesVisible">
            <div class="flex-1 px-6 overflow-hidden">
              <div ref="message-container"
                   class="scroll-smooth space-y-4 overflow-y-auto h-full pb-4 max-h-[calc(100vh-140px)]">
                <template v-if="messages.length > 0">
                  <template v-for="(item, index) in messages">
                    <template v-if="item.content !== '' || index === messages.length - 1">
                      <div :class="['flex', item.role === 'user' ? 'justify-end' : 'justify-start']">
                        <div :class="['max-w-[85%] rounded-xl px-4 transform transition-all duration-300 hover:translate-y-[-2px]',
                    item.role === 'user'? 'bg-blue-500/80 text-white shadow-lg shadow-blue-500/10': 'bg-white/10 text-gray-100 shadow-lg shadow-black/10']">
                          <template v-if="item.content === ''">
                            <div class="flex gap-1.5 py-4">
                              <div class="w-1.5 h-1.5 bg-current rounded-full animate-bounce opacity-50"></div>
                              <div class="w-1.5 h-1.5 bg-current rounded-full animate-bounce opacity-50"
                                   style="animation-delay: 0.2s"></div>
                              <div class="w-1.5 h-1.5 bg-current rounded-full animate-bounce opacity-50"
                                   style="animation-delay: 0.4s"></div>
                            </div>
                          </template>
                          <template v-else>
                            <!-- 用户消息保持白色，系统消息改为浅灰色提高对比度 -->
                            <ml-markdown :content="item.content"/>
                          </template>
                        </div>
                      </div>
                    </template>
                  </template>
                </template>
                <template v-else>
                  <div class="flex flex-col items-center justify-center h-full text-center">
                    <div
                        class="w-16 h-16 rounded-full bg-indigo-100/20 flex items-center justify-center mb-4 backdrop-blur-sm">
                      <svg class="w-8 h-8 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                            stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                      </svg>
                    </div>
                    <h3 class="text-lg font-medium text-gray-100 mb-2">暂无对话记录</h3>
                    <p class="text-gray-300 max-w-xs">
                      开始通话后，您的对话将显示在这里
                    </p>
                  </div>
                </template>
              </div>
            </div>
          </template>
        </transition>
      </div>

      <!-- 底部控制区域 -->
      <div class="backdrop-blur-md p-4 z-20 flex flex-col">
        <!-- 录音状态指示器 -->
        <template v-if="isConnected">
          <div class="flex justify-center mb-3 h-8">
            <div class="flex items-center justify-center gap-1">
              <div
                  :class="['w-1.5 h-1.5 rounded-full transition-all duration-300',isTalking ? 'bg-blue-400 animate-pulse' : 'bg-gray-400']"/>
              <div
                  :class="[ 'w-1.5 h-1.5 rounded-full transition-all duration-300', isTalking ? 'bg-blue-400 animate-pulse' : 'bg-gray-400']"
                  style="animation-delay: 0.2s"/>
              <div
                  :class="[ 'w-1.5 h-1.5 rounded-full transition-all duration-300', isTalking ? 'bg-blue-400 animate-pulse' : 'bg-gray-400']"
                  style="animation-delay: 0.4s"/>
            </div>
          </div>
        </template>

        <!-- 底部按钮栏 -->
        <div class="flex justify-around items-center">
          <!-- 左侧按钮：消息记录 -->
          <button
              :class="['w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300 backdrop-blur-md hover:shadow-lg',
          isConnecting ? 'opacity-50 cursor-not-allowed bg-white/5' : 'bg-indigo-500/20 hover:bg-indigo-500/30 shadow-indigo-500/10']"
              :disabled="isConnecting"
              @click="messagesVisible = !messagesVisible">
            <svg :class="isConnecting || !messagesVisible ? 'text-white/60' : 'text-white'"
                 class="w-6 h-6 transition-colors duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
            </svg>
          </button>

          <!-- 中间按钮：通话核心按钮 -->
          <button
              :class="['w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300 transform hover:scale-105 shadow-md',
          isConnected ? 'bg-red-500 shadow-red-500/30' :
          isConnecting ? 'bg-gray-300 shadow-none cursor-not-allowed' :
          'bg-gradient-to-r from-indigo-500 to-purple-600 shadow-indigo-500/30']"
              :disabled="isConnecting"
              @click="isConnected ? disconnect() : connect()">
            <template v-if="isConnecting">
              <svg class="w-6 h-6 text-white animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3"></circle>
                <path class="opacity-75" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" fill="currentColor"></path>
              </svg>
            </template>
            <template v-else-if="!isConnected">
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                    d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                    stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
              </svg>
            </template>
            <template v-else>
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M6 18L18 6M6 6l12 12" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
              </svg>
            </template>
          </button>

          <!-- 右侧按钮：音色选择 -->
          <button
              :class="['w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300 backdrop-blur-md hover:shadow-lg',
          isConnecting || isConnected ? 'opacity-50 cursor-not-allowed bg-white/5' : 'bg-indigo-500/20 hover:bg-indigo-500/30 shadow-indigo-500/10']"
              :disabled="isConnecting || isConnected"
              @click="settingsPopupVisible = true">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" stroke-linecap="round" stroke-linejoin="round"
                    stroke-width="2"></path>
              <path
                  d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"
                  stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
            </svg>
          </button>
        </div>

        <!-- 音色选择弹窗 -->
        <t-popup :visible="settingsPopupVisible" placement="bottom">
          <t-picker
              :columns="getPickerOptions()"
              title="音色选择"
              @cancel="settingsPopupVisible = false"
              @confirm="onConfirm">
            <template #option="item">
              <a-space class="w-18">{{ item.data.voiceName }}</a-space>
              <a-space>
                <template v-if="item.data.type === 'us'">
                  <t-tag theme="primary" variant="light">美音</t-tag>
                </template>
                <template v-else>
                  <t-tag theme="primary" variant="light">英音</t-tag>
                </template>
                <template v-for="tag in item.data.tags">
                  <t-tag theme="danger" variant="light">{{ tag }}</t-tag>
                </template>
              </a-space>
            </template>
          </t-picker>
        </t-popup>
      </div>
    </div>

    <ml-ws-audio-player ref="ws-player"/>
  </div>
</template>

<style scoped>
:deep(.t-navbar__content) {
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: #e5e7eb;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}


.animate-bounce {
  animation: bounce 1s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.4);
    opacity: 0.7;
  }
}

@keyframes pulse-1 {
  0%, 100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
}

@keyframes pulse-2 {
  0%, 100% {
    opacity: 0.7;
  }
  50% {
    opacity: 1;
  }
}

@keyframes pulse-3 {
  0%, 100% {
    opacity: 0.8;
  }
  50% {
    opacity: 1;
  }
}

/* 科技网格背景 */
.tech-grid {
  background: linear-gradient(rgba(64, 224, 208, 0.1) 1px, transparent 1px),
  linear-gradient(90deg, rgba(64, 224, 208, 0.1) 1px, transparent 1px),
  #0a0a0a;
  background-size: 30px 30px, 30px 30px, 100% 100%;
}

.tech-grid::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 20% 80%, rgba(64, 224, 208, 0.15) 0%, transparent 50%),
  radial-gradient(circle at 80% 20%, rgba(138, 43, 226, 0.15) 0%, transparent 50%);
}
</style>