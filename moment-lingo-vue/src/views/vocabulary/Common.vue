<script lang="ts" setup>
import { onMounted, ref, watch } from 'vue';
import { getDetailVocabulary, getVocabulary } from '@/api/vocabulary.ts';
import { listVoices } from '@/api/tts.ts';
import MlAudioButton from '@/components/audio/MlAudioButton.vue';
import { useRouter } from 'vue-router';
import MlNavbar from '@/components/layout/MlNavbar.vue';
import { type AudioPlayer, AudioPlayerFactory } from '@/composables/audioPlayerFactory';


const props = defineProps<{
  vocabularyId: string;
  type: number;
}>();
const router = useRouter();

interface Vocabulary {
  word: string;
  vocabulary: string;
  phonetic: string;
  translation: string[];
  did?: string | null;
  done?: string | null;
  doing?: string | null;
  does?: string | null;
  comparative?: string | null;
  superlative?: string | null;
  plural?: string | null;
  lemma?: string | null;
  vocabularyId: number;
  explanation: any[];
  tags: any[];
}

interface Voice {
  voiceId: number;
  voiceKey: string;
  voiceName: string;
  tags: string[];
  model: string;
  type: string;
}

const vocabulary = ref<Vocabulary>({
  word: '',
  vocabulary: '',
  phonetic: '',
  translation: [],
  did: null,
  done: null,
  doing: null,
  does: null,
  comparative: null,
  superlative: null,
  plural: null,
  lemma: null,
  vocabularyId: 0,
  explanation: [],
  tags: []
});

const selectedUkVoiceId = ref<number>();
const selectedUsVoiceId = ref<number>();
const ukVoices = ref<Array<Voice>>();
const usVoices = ref<Array<Voice>>();
const isLoading = ref(false);
const usPlayer = AudioPlayerFactory.create();
const ukPlayer = AudioPlayerFactory.create();
const ukVoicePopupVisible = ref(false);
const usVoicePopupVisible = ref(false);


async function loadData(vocabularyId: string) {
  isLoading.value = true;
  const resp = await getDetailVocabulary(String(vocabularyId));
  isLoading.value = false;
  vocabulary.value = resp.data;
}

function playAudio(type: string, content: string, player: AudioPlayer) {
  let voice;
  if (type === 'uk') {
    voice = ukVoices.value?.find((item) => item.voiceId === selectedUkVoiceId.value);
  } else if (type === 'us') {
    voice = usVoices.value?.find((item) => item.voiceId === selectedUsVoiceId.value);
  }

  player.setOptions({
    content,
    model: voice?.model as string,
    voiceKey: voice?.voiceKey as string,
  });
  player.toggle(true);
}


function getPickerOptions(type: string) {
  if (type === 'uk') {
    return ukVoices.value?.map(item => ({
      data: item,
      value: item.voiceId
    }));
  } else {
    return usVoices.value?.map(item => ({
      data: item,
      value: item.voiceId
    }));
  }
}


function getVoiceName(type: string) {
  if (type === 'uk') {
    return ukVoices.value?.find((item) => item.voiceId === selectedUkVoiceId.value)?.voiceName;
  } else {
    return usVoices.value?.find((item) => item.voiceId === selectedUsVoiceId.value)?.voiceName;
  }
}

function onPopupVisible(type: string) {
  if (type === 'uk') {
    ukVoicePopupVisible.value = true;
  } else {
    usVoicePopupVisible.value = true;
  }
}


function onConfirm(type: string, val: any) {
  if (type === 'uk') {
    selectedUkVoiceId.value = val[0] as number;
    ukVoicePopupVisible.value = false;
  } else {
    selectedUsVoiceId.value = val[0] as number;
    usVoicePopupVisible.value = false;
  }
}


async function goToVocabulary(vocabulary: string) {
  const resp = await getVocabulary(vocabulary);
  await router.push(`/vocabulary/${ resp.data.vocabularyId }`);
}


watch(() => props.type, async () => {
  await loadData(props.vocabularyId);
}, { immediate: true });

onMounted(async () => {
  const resp = await listVoices();
  const voices = resp.data as Voice[];
  ukVoices.value = voices.filter((item) => item.type === 'uk');
  usVoices.value = voices.filter((item) => item.type === 'us');
  selectedUkVoiceId.value = ukVoices.value[0]!.voiceId as number;
  selectedUsVoiceId.value = usVoices.value[0]!.voiceId as number;
});
</script>

<template>
  <div>
    <!-- web -->
    <div class="min-h-screen hidden md:block px-3 py-24">
      <transition-group name="fade-from-bottom">
        <template v-if="!isLoading">
          <div class="max-w-4xl mx-auto flex flex-col gap-8 pb-56">
            <!-- 单词卡片 -->
            <div class="bg-surface-card p-6 rounded-[8px] relative">
              <!-- 单词 -->
              <div class="font-normal text-[48px] leading-[1.1] tracking-[-1px] text-ink mb-4">
                {{ vocabulary.vocabulary }}
              </div>
              <!-- 音色选择框 -->
              <div class="items-end flex flex-col gap-2 mb-3">
                <!-- 英音音色选择 -->
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium text-muted whitespace-nowrap">英音:</span>
                  <a-select v-model="selectedUkVoiceId" :style="{width:'200px'}" size="small">
                    <template v-for="item in ukVoices" :key="item.voiceId">
                      <a-option :label="item.voiceName" :value="item.voiceId">
                        <a-space :style="{width:'200px'}">
                          <a-space class="w-14">
                            {{ item.voiceName }}
                          </a-space>
                          <a-space>
                            <template v-for="tag in item.tags">
                              <a-tag color="arcoblue" size="small">
                                {{ tag }}
                              </a-tag>
                            </template>
                          </a-space>
                        </a-space>
                      </a-option>
                    </template>
                  </a-select>
                </div>

                <!-- 美音音色选择 -->
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium text-muted whitespace-nowrap">美音:</span>
                  <a-select v-model="selectedUsVoiceId" :style="{width:'200px'}" size="small">
                    <template v-for="item in usVoices" :key="item.voiceId">
                      <a-option :label="item.voiceName" :value="item.voiceId">
                        <a-space :style="{width:'200px'}">
                          <a-space class="w-14">
                            {{ item.voiceName }}
                          </a-space>
                          <a-space>
                            <template v-for="tag in item.tags">
                              <a-tag color="arcoblue" size="small">
                                {{ tag }}
                              </a-tag>
                            </template>
                          </a-space>
                        </a-space>
                      </a-option>
                    </template>
                  </a-select>
                </div>
              </div>
              <!-- 音标和播放控制 -->
              <div class="flex flex-wrap gap-4">
                <!-- 英式音标和播放控制 -->
                <div class="flex items-center gap-2">
                  <template v-if="vocabulary.phonetic">
                    <div class="flex items-center gap-2">
                      <span class="font-mono text-[10px] tracking-[0.1em] uppercase text-muted min-w-[24px]">UK</span>
                      <span class="font-display text-[18px] italic text-phonetic tracking-[0.02em]">/{{
                          vocabulary.phonetic
                        }}/</span>
                    </div>
                  </template>
                  <a-tooltip :content="'英音'">
                    <ml-audio-button :loading="ukPlayer.isLoading" :playing="ukPlayer.isPlaying"
                                     @click="playAudio('uk', vocabulary.vocabulary ,ukPlayer as any)"/>
                  </a-tooltip>
                </div>

                <!-- 美式音标和播放控制 -->
                <div class="flex items-center gap-2">
                  <template v-if="vocabulary.phonetic">
                    <div class="flex items-center gap-2">
                      <span class="font-mono text-[10px] tracking-[0.1em] uppercase text-muted min-w-[24px]">US</span>
                      <span class="font-display text-[18px] italic text-phonetic tracking-[0.02em]">/{{
                          vocabulary.phonetic
                        }}/</span>
                    </div>
                  </template>
                  <a-tooltip :content="'美音'">
                    <ml-audio-button :loading="usPlayer.isLoading" :playing="usPlayer.isPlaying"
                                     @click="playAudio('us', vocabulary.vocabulary, usPlayer as any)"/>
                  </a-tooltip>
                </div>
              </div>
            </div>

            <!-- 释义 -->
            <template v-if="vocabulary.translation&&vocabulary.translation.length > 0">
              <div class="bg-surface-card p-6 rounded-[8px]">
                <h2 class="font-display font-normal text-[28px] leading-[1.2] tracking-[-0.3px] text-ink mb-4">
                  释义
                </h2>
                <div class="space-y-4">
                  <template v-for="(trans, index) in vocabulary.translation" :key="index">
                    <div class="relative pl-5 border-l-2 border-primary/30">
                      <div
                          class="absolute -left-[12px] top-0 w-[22px] h-[22px] rounded-full bg-surface-card border-2 border-primary/30 flex items-center justify-center text-[11px] font-bold text-primary">
                        {{ index + 1 }}
                      </div>
                      <div class="bg-surface-soft p-4 rounded-[6px]">
                        <span class="text-[16px] font-normal text-body leading-[1.55]">{{ trans }}</span>
                      </div>
                    </div>
                  </template>
                </div>
              </div>
            </template>

            <!-- 词形变化 -->
            <template v-if="vocabulary && (vocabulary.did || vocabulary.done || vocabulary.doing ||
        vocabulary.does || vocabulary.comparative || vocabulary.superlative ||
        vocabulary.plural || vocabulary.lemma)">
              <div class="bg-surface-card p-6 rounded-[8px]">
                <h2 class="font-display font-normal text-[28px] leading-[1.2] tracking-[-0.3px] text-ink mb-4">
                  词形变化
                </h2>

                <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                  <!-- 过去式 -->
                  <template v-if="vocabulary.did">
                    <div
                        class="bg-canvas p-3 rounded-[6px] border border-hairline flex flex-col cursor-pointer transition-colors duration-200 hover:bg-surface-soft hover:border-primary"
                        @click="goToVocabulary(vocabulary.did)">
                      <span class="text-[12px] font-medium text-muted mb-1">过去式</span>
                      <span class="text-[14px] font-medium text-primary">{{ vocabulary.did }}</span>
                    </div>
                  </template>

                  <!-- 过去分词 -->
                  <template v-if="vocabulary.done">
                    <div
                        class="bg-canvas p-3 rounded-[6px] border border-hairline flex flex-col cursor-pointer transition-colors duration-200 hover:bg-surface-soft hover:border-primary"
                        @click="goToVocabulary(vocabulary.done)">
                      <span class="text-[12px] font-medium text-muted mb-1">过去分词</span>
                      <span class="text-[14px] font-medium text-primary">{{ vocabulary.done }}</span>
                    </div>
                  </template>

                  <!-- 现在分词 -->
                  <template v-if="vocabulary.doing">
                    <div
                        class="bg-canvas p-3 rounded-[6px] border border-hairline flex flex-col cursor-pointer transition-colors duration-200 hover:bg-surface-soft hover:border-primary"
                        @click="goToVocabulary(vocabulary.doing)">
                      <span class="text-[12px] font-medium text-muted mb-1">现在分词</span>
                      <span class="text-[14px] font-medium text-primary">{{ vocabulary.doing }}</span>
                    </div>
                  </template>

                  <!-- 第三人称单数 -->
                  <template v-if="vocabulary.does">
                    <div
                        class="bg-canvas p-3 rounded-[6px] border border-hairline flex flex-col cursor-pointer transition-colors duration-200 hover:bg-surface-soft hover:border-primary"
                        @click="goToVocabulary(vocabulary.does)">
                      <span class="text-[12px] font-medium text-muted mb-1">第三人称单数</span>
                      <span class="text-[14px] font-medium text-primary">{{ vocabulary.does }}</span>
                    </div>
                  </template>

                  <!-- 比较级 -->
                  <template v-if="vocabulary.comparative">
                    <div
                        class="bg-canvas p-3 rounded-[6px] border border-hairline flex flex-col cursor-pointer transition-colors duration-200 hover:bg-surface-soft hover:border-primary"
                        @click="goToVocabulary(vocabulary.comparative)">
                      <span class="text-[12px] font-medium text-muted mb-1">比较级</span>
                      <span class="text-[14px] font-medium text-primary">{{ vocabulary.comparative }}</span>
                    </div>
                  </template>

                  <!-- 最高级 -->
                  <template v-if="vocabulary.superlative">
                    <div
                        class="bg-canvas p-3 rounded-[6px] border border-hairline flex flex-col cursor-pointer transition-colors duration-200 hover:bg-surface-soft hover:border-primary"
                        @click="goToVocabulary(vocabulary.superlative)">
                      <span class="text-[12px] font-medium text-muted mb-1">最高级</span>
                      <span class="text-[14px] font-medium text-primary">{{ vocabulary.superlative }}</span>
                    </div>
                  </template>

                  <!-- 复数 -->
                  <template v-if="vocabulary.plural">
                    <div
                        class="bg-canvas p-3 rounded-[6px] border border-hairline flex flex-col cursor-pointer transition-colors duration-200 hover:bg-surface-soft hover:border-primary"
                        @click="goToVocabulary(vocabulary.plural)">
                      <span class="text-[12px] font-medium text-muted mb-1">复数</span>
                      <span class="text-[14px] font-medium text-primary">{{ vocabulary.plural }}</span>
                    </div>
                  </template>

                  <!-- 原型 -->
                  <template v-if="vocabulary.lemma">
                    <div
                        class="bg-canvas p-3 rounded-[6px] border border-hairline flex flex-col cursor-pointer transition-colors duration-200 hover:bg-surface-soft hover:border-primary"
                        @click="goToVocabulary(vocabulary.lemma)">
                      <span class="text-[12px] font-medium text-muted mb-1">原型</span>
                      <span class="text-[14px] font-medium text-primary">{{ vocabulary.lemma }}</span>
                    </div>
                  </template>
                </div>
              </div>
            </template>
          </div>
        </template>
      </transition-group>
    </div>

    <!-- h5 -->
    <div class="md:hidden h-screen flex flex-col">
      <transition-group name="fade-from-bottom">
        <template v-if="!isLoading">
          <div class="h-12">
            <ml-navbar title="词汇"/>
          </div>
          <div id="scroll-container" class="flex flex-col gap-2 flex-1 overflow-auto">
            <!-- 单词卡片 -->
            <div class="bg-white p-3 pt-10">
              <div class="text-4xl font-bold text-gray-900 mb-8 text-center tracking-tight">
                {{ vocabulary.vocabulary }}
              </div>

              <!-- 音标和播放控制 -->
              <div class="flex flex-wrap gap-4 mb-4 justify-center">
                <!-- 英式音标和播放控制 -->
                <div class="flex items-center gap-2">
                  <template v-if="vocabulary.phonetic">
                    <div class="flex items-center text-gray-700 bg-gray-100 px-3 py-2 rounded-lg">
                      <span class="mr-1 text-xs font-semibold text-gray-700">英:</span>
                      <span class="font-serif text-xs">/{{ vocabulary.phonetic }}/</span>
                    </div>
                  </template>
                  <ml-audio-button
                      :loading="ukPlayer.isLoading"
                      :playing="ukPlayer.isPlaying"
                      class="w-7 h-7"
                      @click="playAudio('uk', vocabulary.vocabulary ,ukPlayer as any)"
                  />
                </div>

                <!-- 美式音标和播放控制 -->
                <div class="flex items-center gap-2">
                  <ml-audio-button
                      :loading="usPlayer.isLoading"
                      :playing="usPlayer.isPlaying"
                      class="w-7 h-7"
                      @click="playAudio('us', vocabulary.vocabulary ,usPlayer as any)"
                  />
                </div>
              </div>

              <!-- 音色选择 -->
              <div class="flex gap-3 justify-center">
                <!-- 英音音色选择 -->
                <div @click="onPopupVisible('uk')">
                  <div
                      class="text-xs font-medium text-gray-700 bg-gray-100 px-3 py-1 rounded-lg cursor-pointer"
                  >
                    英音: {{ getVoiceName('uk') }}
                  </div>
                </div>
                <!-- 美音音色选择 -->
                <div @click="onPopupVisible('us')">
                  <div
                      class="text-xs font-medium text-gray-700 bg-gray-100 px-3 py-1 rounded-lg cursor-pointer"
                  >
                    美音: {{ getVoiceName('us') }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 标签页 -->
            <template v-if="vocabulary.translation&&vocabulary.translation.length">
              <div>
                <t-tabs :sticky-props="{offsetTop:48}" class="min-h-screen" default-value="0" sticky theme="line">
                  <t-tab-panel class="min-h-screen" label="简明" value="0">
                    <div class="p-4">
                      <div class="space-y-4">
                        <!-- 基本释义 -->
                        <template v-for="(trans, index) in vocabulary.translation" :key="index">
                          <div class="pb-1">
                            <div class="flex gap-3 items-start">
                        <span
                            class="inline-flex items-center px-3 py-1 bg-blue-50 text-blue-700 text-xs font-semibold rounded-full">
                          {{ index + 1 }}
                        </span>
                              <span class="text-gray-800 text-sm leading-6 flex-1">{{ trans }}</span>
                            </div>
                          </div>
                          <a-divider/>
                        </template>

                        <!-- 词性变化 -->
                        <template
                            v-if="vocabulary && (vocabulary.did || vocabulary.done || vocabulary.doing ||vocabulary.does || vocabulary.comparative || vocabulary.superlative ||vocabulary.plural || vocabulary.lemma)">
                          <div class="pt-2">
                            <div class="grid grid-cols-2 gap-2">
                              <!-- 过去式 -->
                              <template v-if="vocabulary.did">
                                <div class="bg-gray-50/50 p-3 rounded-lg border border-gray-200 flex flex-col"
                                     @click="goToVocabulary(vocabulary.did)">
                                  <span class="text-xs font-medium text-gray-600 mb-1">过去式</span>
                                  <span class="text-sm font-semibold text-green-700">{{ vocabulary.did }}</span>
                                </div>
                              </template>

                              <!-- 过去分词 -->
                              <template v-if="vocabulary.done">
                                <div class="bg-gray-50/50 p-3 rounded-lg border border-gray-200 flex flex-col"
                                     @click="goToVocabulary(vocabulary.done)">
                                  <span class="text-xs font-medium text-gray-600 mb-1">过去分词</span>
                                  <span class="text-sm font-semibold text-green-700">{{ vocabulary.done }}</span>
                                </div>
                              </template>

                              <!-- 现在分词 -->
                              <template v-if="vocabulary.doing">
                                <div class="bg-gray-50/50 p-3 rounded-lg border border-gray-200 flex flex-col"
                                     @click="goToVocabulary(vocabulary.doing)">
                                  <span class="text-xs font-medium text-gray-600 mb-1">现在分词</span>
                                  <span class="text-sm font-semibold text-green-700">{{ vocabulary.doing }}</span>
                                </div>
                              </template>

                              <!-- 第三人称单数 -->
                              <template v-if="vocabulary.does">
                                <div class="bg-gray-50/50 p-3 rounded-lg border border-gray-200 flex flex-col"
                                     @click="goToVocabulary(vocabulary.does)">
                                  <span class="text-xs font-medium text-gray-600 mb-1">第三人称单数</span>
                                  <span class="text-sm font-semibold text-green-700">{{ vocabulary.does }}</span>
                                </div>
                              </template>

                              <!-- 比较级 -->
                              <template v-if="vocabulary.comparative">
                                <div class="bg-gray-50/50 p-3 rounded-lg border border-gray-200 flex flex-col"
                                     @click="goToVocabulary(vocabulary.comparative)">
                                  <span class="text-xs font-medium text-gray-600 mb-1">比较级</span>
                                  <span class="text-sm font-semibold text-green-700">
                                {{ vocabulary.comparative }}
                              </span>
                                </div>
                              </template>

                              <!-- 最高级 -->
                              <template v-if="vocabulary.superlative">
                                <div class="bg-gray-50/50 p-3 rounded-lg border border-gray-200 flex flex-col"
                                     @click="goToVocabulary(vocabulary.superlative)">
                                  <span class="text-xs font-medium text-gray-600 mb-1">最高级</span>
                                  <span class="text-sm font-semibold text-green-700">
                                {{ vocabulary.superlative }}
                              </span>
                                </div>
                              </template>

                              <!-- 复数 -->
                              <template v-if="vocabulary.plural">
                                <div class="bg-gray-50/50 p-3 rounded-lg border border-gray-200 flex flex-col"
                                     @click="goToVocabulary(vocabulary.plural)">
                                  <span class="text-xs font-medium text-gray-600 mb-1">复数</span>
                                  <span class="text-sm font-semibold text-green-700">{{ vocabulary.plural }}</span>
                                </div>
                              </template>

                              <!-- 原型 -->
                              <template v-if="vocabulary.lemma">
                                <div class="bg-gray-50/50 p-3 rounded-lg border border-gray-200 flex flex-col"
                                     @click="goToVocabulary(vocabulary.lemma)">
                                  <span class="text-xs font-medium text-gray-600 mb-1">原型</span>
                                  <span class="text-sm font-semibold text-green-700">{{ vocabulary.lemma }}</span>
                                </div>
                              </template>
                            </div>
                          </div>
                        </template>
                      </div>
                    </div>
                  </t-tab-panel>
                </t-tabs>
                <a-back-top target-container="#scroll-container">
                  <div class="w-10 h-10 rounded-full flex items-center justify-center shadow-lg transition-all duration-300
              bg-gradient-to-br from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700
              hover:scale-110 hover:shadow-xl">
                    <svg class="w-6 h-6 text-white" height="200" p-id="8652" t="1761297920393"
                         version="1.1" viewBox="0 0 1024 1024" width="200" xmlns="http://www.w3.org/2000/svg">
                      <path
                          d="M752.736 431.063C757.159 140.575 520.41 8.97 504.518 0.41V0l-0.45 0.205-0.41-0.205v0.41c-15.934 8.56-252.723 140.165-248.259 430.653-48.21 31.457-98.713 87.368-90.685 184.074 8.028 96.666 101.007 160.768 136.601 157.287 35.595-3.482 25.232-30.31 25.232-30.31l12.206-50.095s52.47 80.569 69.304 80.528c15.114-1.23 87-0.123 95.6 0h0.82c8.602-0.123 80.486-1.23 95.6 0 16.794 0 69.305-80.528 69.305-80.528l12.165 50.094s-10.322 26.83 25.272 30.31c35.595 3.482 128.574-60.62 136.602-157.286 8.028-96.665-42.475-152.617-90.685-184.074z m-248.669-4.26c-6.758-0.123-94.781-3.359-102.891-107.192 2.95-98.714 95.97-107.438 102.891-107.93 6.964 0.492 99.943 9.216 102.892 107.93-8.11 103.833-96.174 107.07-102.892 107.192z m-52.019 500.531c0 11.838-9.42 21.382-21.012 21.382a21.217 21.217 0 0 1-21.054-21.34V821.74c0-11.797 9.421-21.382 21.054-21.382 11.591 0 21.012 9.585 21.012 21.382v105.635z m77.333 57.222a21.504 21.504 0 0 1-21.34 21.626 21.504 21.504 0 0 1-21.34-21.626V827.474c0-11.96 9.543-21.668 21.299-21.668 11.796 0 21.38 9.708 21.38 21.668v157.082z m71.147-82.043c0 11.796-9.42 21.34-21.053 21.34a21.217 21.217 0 0 1-21.013-21.34v-75.367c0-11.755 9.421-21.299 21.013-21.299 11.632 0 21.053 9.544 21.053 21.3v75.366z"
                          fill="currentColor" p-id="8653"></path>
                    </svg>
                  </div>
                </a-back-top>
              </div>
            </template>
          </div>
        </template>
      </transition-group>

      <!-- 音色选择弹窗 -->
      <t-popup :visible="ukVoicePopupVisible" placement="bottom">
        <t-picker
            :columns="getPickerOptions('uk')"
            title="英音"
            @cancel="ukVoicePopupVisible = false"
            @confirm="onConfirm('uk',$event)">
          <template #option="item">
            <a-space class="w-14">{{ item.data.voiceName }}</a-space>
            <a-space>
              <template v-for="tag in item.data.tags">
                <t-tag theme="danger" variant="light">{{ tag }}</t-tag>
              </template>
            </a-space>
          </template>
        </t-picker>
      </t-popup>
      <t-popup :visible="usVoicePopupVisible" placement="bottom">
        <t-picker
            :columns="getPickerOptions('us')"
            title="美音"
            @cancel="usVoicePopupVisible = false"
            @confirm="onConfirm('us',$event)">
          <template #option="item">
            <a-space class="w-14">{{ item.data.voiceName }}</a-space>
            <a-space>
              <template v-for="tag in item.data.tags">
                <t-tag theme="danger" variant="light">{{ tag }}</t-tag>
              </template>
            </a-space>
          </template>
        </t-picker>
      </t-popup>
    </div>
  </div>
</template>