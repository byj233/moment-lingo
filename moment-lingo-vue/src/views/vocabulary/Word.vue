<script lang="ts" setup>
import { onMounted, onUnmounted, ref, watch } from 'vue';
import MlAudioButton from '@/components/audio/MlAudioButton.vue';
import { listVoices } from '@/api/tts.ts';
import { getDetailVocabulary, getVocabulary } from '@/api/vocabulary.ts';
import { useMSEAudioPlayer } from '@/composables/useMSEAudioPlayer.js';
import { useRouter } from 'vue-router';
import MlNavbar from '@/components/layout/MlNavbar.vue';
import type { AudioPlayer } from '@/composables/types.js';
import { AudioPlayerFactory } from '@/composables/audioPlayerFactory.js';


const props = defineProps<{
  vocabularyId: string;
  type: number;
}>();
const router = useRouter();

interface Sentence {
  content: string;
  translation: string;
  ukPlayer: AudioPlayer;
  usPlayer: AudioPlayer;
}

interface Explanation {
  pos: string;
  en: string[];
  cn: string[];
}

interface Synonym {
  pos: string;
  translation: string[];
  words: string[];
}

interface RelWord {
  pos: string;
  words: {
    word: string;
    translation: string;
  }[];
}

interface RealExamSentence {
  content: string;
  sourceInfo: {
    level: string;
    year: string;
    type: string;
    paper: string;
  };
}

interface Phrase {
  content: string;
  translation: string;
}

interface Vocabulary {
  vocabularyId: number;
  vocabulary: string;
  did?: string | null;
  done?: string | null;
  doing?: string | null;
  does?: string | null;
  comparative?: string | null;
  superlative?: string | null;
  plural?: string | null;
  lemma?: string | null;
  lexicalId?: number | null;
  type?: string | null;
}

interface Brief {
  word: string;
  usPhonetic: string;
  ukPhonetic: string;
  usPlayer: AudioPlayer;
  ukPlayer: AudioPlayer;
  remMethod: string[];
  vocabulary: Vocabulary;
  sentences: Sentence[];
  phrases: Phrase[];
  explanation: Explanation[];
  synonyms: Synonym[];
  antonyms: string[];
  relWords: RelWord[];
  realExamSentences: RealExamSentence[];
}

interface Voice {
  voiceId: number;
  voiceKey: string;
  voiceName: string;
  tags: string[];
  model: string;
  type: string;
}

const emptyBrief: Brief = {
  word: '',
  usPhonetic: '',
  ukPhonetic: '',
  usPlayer: AudioPlayerFactory.create(),
  ukPlayer: AudioPlayerFactory.create(),
  remMethod: [],
  vocabulary: {
    vocabularyId: 0,
    vocabulary: ''
  },
  sentences: [
    {
      content: '',
      translation: '',
      usPlayer: AudioPlayerFactory.create(),
      ukPlayer: AudioPlayerFactory.create()
    }
  ],
  phrases: [
    {
      content: '',
      translation: ''
    }
  ],
  explanation: [
    {
      pos: '',
      en: [],
      cn: []
    }
  ],
  synonyms: [
    {
      pos: '',
      translation: [],
      words: []
    },
  ],
  antonyms: [],
  relWords: [
    {
      pos: '',
      words: [
        {
          word: '',
          translation: ''
        }
      ]
    }
  ],
  realExamSentences: [
    {
      content: '',
      sourceInfo: {
        level: '',
        year: '',
        type: '',
        paper: ''
      }
    }
  ],
};

const data = ref();
const brief = ref<Brief>(emptyBrief);
const isLoading = ref(false);
const selectedUkVoiceId = ref<number>();
const selectedUsVoiceId = ref<number>();
const ukVoices = ref<Array<Voice>>();
const usVoices = ref<Array<Voice>>();
const ukVoicePopupVisible = ref(false);
const usVoicePopupVisible = ref(false);
const activeNavItem = ref('word-card');
let scrollListener: any;
let ticking = false;
let isClickScrolling = false;
let scrollTimeout: any = null;

function highlightKeyword(sentence: string) {
  const { did, done, doing, does, comparative, superlative, plural, lemma } = brief.value.vocabulary;
  const keywords = [brief.value.word, did, done, doing, does, comparative, superlative, plural, lemma];

  if (!keywords || keywords.length === 0) {
    return sentence;
  }

  // 对关键词进行转义处理，避免特殊字符影响正则
  const escapedKeywords = keywords.map(keyword =>
      keyword?.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  );

  // 生成匹配多个关键词的正则（忽略大小写）
  const regex = new RegExp(`(${escapedKeywords.join('|')})`, 'gi');
  return sentence.replace(regex, '<span class="text-primary font-semibold not-italic">$1</span>');
}


function formatMemoryMethod(text: string) {
  // 高亮英文字母部分（原文中没有 HTML 标签）
  let formatted = text.replace(/([a-zA-Z]+)/g, '<span class="text-primary font-semibold">$1</span>');
  // 替换箭头
  formatted = formatted.replace(/→/g, '<span class="text-muted-soft mx-1">→</span>');
  // 替换加号
  formatted = formatted.replace(/\+/g, '<span class="text-muted-soft mx-1">+</span>');
  return formatted;
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

async function goToVocabulary(vocabulary: string) {
  const resp = await getVocabulary(vocabulary);
  await router.push(`/vocabulary/${ resp.data.vocabularyId }`);
}

async function loadData(vocabularyId: string) {
  isLoading.value = true;
  const resp = await getDetailVocabulary(vocabularyId);
  isLoading.value = false;

  data.value = resp.data;
  brief.value = {
    ...resp.data.brief,
    usPlayer: new useMSEAudioPlayer(),
    ukPlayer: new useMSEAudioPlayer(),
    sentences: resp.data.brief.sentences.map((item: any) => ({
      ...item,
      usPlayer: new useMSEAudioPlayer(),
      ukPlayer: new useMSEAudioPlayer()
    })),
    vocabulary: resp.data.vocabulary,
    word: resp.data.word
  };

  if (brief.value.remMethod.length !== 0) {
    brief.value.remMethod = [brief.value.remMethod[0] as string];
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


function scrollToSection(sectionId: string) {
  const element = document.getElementById(sectionId) as HTMLElement;
  if (!element) return;

  isClickScrolling = true;
  activeNavItem.value = sectionId;

  const navHeight = 96;
  const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
  const offsetPosition = elementPosition - navHeight;

  window.scrollTo({
    top: offsetPosition,
    behavior: 'smooth'
  });

  if (scrollTimeout) {
    clearTimeout(scrollTimeout);
  }
  scrollTimeout = setTimeout(() => {
    isClickScrolling = false;
  }, 1000);
}

function handleScroll() {
  if (ticking || isClickScrolling) {
    return;
  }

  ticking = true;
  requestAnimationFrame(() => {
    const sections = [
      'word-card',
      'brief-explanation',
      'word-forms',
      'memory-method',
      'explanation',
      'sentences',
      'real-exam-sentences',
      'phrases',
      'synonyms',
      'antonyms',
      'rel-words'
    ];

    let currentSection = 'word-card';
    const navHeight = 96;
    const scrollTop = window.pageYOffset;
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const isAtBottom = scrollTop + windowHeight >= documentHeight - 2;

    // 检查是否有内容可滚动
    const hasScrollableContent = documentHeight > windowHeight;

    if (isAtBottom && !hasScrollableContent) {
      // 当页面内容不全时，找到第一个存在的 section
      for (let i = 0; i < sections.length; i++) {
        const sectionId: any = sections[i];
        const element = document.getElementById(sectionId);
        if (element && element.offsetParent !== null) {
          currentSection = sectionId;
          break;
        }
      }
    } else if (isAtBottom) {
      // 真正触底后，激活最后一个存在的 section（保证衍生词可生效）
      for (let i = sections.length - 1; i >= 0; i--) {
        const sectionId: any = sections[i];
        const element = document.getElementById(sectionId);
        if (element && element.offsetParent !== null) {
          currentSection = sectionId;
          break;
        }
      }
    } else {
      // 正常滚动时，找到当前在视口顶部的 section
      for (let i = sections.length - 1; i >= 0; i--) {
        const sectionId: any = sections[i];
        const element = document.getElementById(sectionId) as HTMLElement;

        // 检查元素是否存在
        if (element && element.offsetParent !== null) {
          const rect = element.getBoundingClientRect();
          if (rect.top <= navHeight + 60) {
            currentSection = sectionId;
            break;
          }
        }
      }
    }

    if (activeNavItem.value !== currentSection) {
      activeNavItem.value = currentSection;
    }

    ticking = false;
  });
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

  scrollListener = handleScroll;
  window.addEventListener('scroll', scrollListener);
});

onUnmounted(() => {
  if (scrollListener) {
    window.removeEventListener('scroll', scrollListener);
  }
});
</script>

<template>
  <div>
    <!-- web -->
    <div class="min-h-screen hidden md:block px-3 py-24">
      <transition-group name="fade-from-bottom">
        <template v-if="!isLoading">
          <div class="max-w-7xl mx-auto flex gap-8">
            <!-- 左侧导航栏 -->
            <div class="w-56 flex-shrink-0">
              <div class="sticky top-24">
                <div class="bg-surface-card rounded-[12px] p-4 max-h-[calc(100vh-120px)] overflow-y-auto">
                  <h3 class="text-sm font-semibold text-body mb-3 px-2">目录</h3>
                  <nav class="space-y-1">
                    <button
                        :class="['w-full text-left px-3 py-2 rounded-lg text-sm transition-all duration-300 ease-out flex items-center',
                          activeNavItem === 'word-card'
                            ? 'bg-surface-cream-strong text-ink font-medium'
                            : 'text-muted hover:bg-surface-soft hover:text-ink']"
                        @click="scrollToSection('word-card')"
                    >
                      <span :class="['w-1.5 h-1.5 rounded-full mr-2 transition-all duration-300 ease-out', 
                        activeNavItem === 'word-card' ? 'bg-primary scale-125' : 'bg-muted-soft']"
                      ></span>
                      单词卡片
                    </button>

                    <button
                        :class="['w-full text-left px-3 py-2 rounded-lg text-sm transition-all duration-300 ease-out flex items-center',
                          activeNavItem === 'brief-explanation'
                            ? 'bg-surface-cream-strong text-ink font-medium'
                            : 'text-muted hover:bg-surface-soft hover:text-ink']"
                        @click="scrollToSection('brief-explanation')"
                    >
                      <span :class="['w-1.5 h-1.5 rounded-full mr-2 transition-all duration-300 ease-out', 
                        activeNavItem === 'brief-explanation' ? 'bg-primary scale-125' : 'bg-muted-soft']"
                      ></span>
                      简明释义
                    </button>

                    <template v-if="brief && (brief.vocabulary.did || brief.vocabulary.done || brief.vocabulary.doing ||
                        brief.vocabulary.does || brief.vocabulary.comparative || brief.vocabulary.superlative ||
                        brief.vocabulary.plural || brief.vocabulary.lemma)">
                      <button
                          :class="['w-full text-left px-3 py-2 rounded-lg text-sm transition-all duration-300 ease-out flex items-center',
                            activeNavItem === 'word-forms'
                              ? 'bg-surface-cream-strong text-ink font-medium'
                              : 'text-muted hover:bg-surface-soft hover:text-ink']"
                          @click="scrollToSection('word-forms')"
                      >
                        <span :class="['w-1.5 h-1.5 rounded-full mr-2 transition-all duration-300 ease-out', 
                          activeNavItem === 'word-forms' ? 'bg-primary scale-125' : 'bg-muted-soft']"
                        ></span>
                        词形变化
                      </button>
                    </template>

                    <template v-if="brief.remMethod && brief.remMethod.length > 0">
                      <button
                          :class="['w-full text-left px-3 py-2 rounded-lg text-sm transition-all duration-300 ease-out flex items-center',
                            activeNavItem === 'memory-method'
                              ? 'bg-surface-cream-strong text-ink font-medium'
                              : 'text-muted hover:bg-surface-soft hover:text-ink']"
                          @click="scrollToSection('memory-method')"
                      >
                        <span :class="['w-1.5 h-1.5 rounded-full mr-2 transition-all duration-300 ease-out', 
                          activeNavItem === 'memory-method' ? 'bg-primary scale-125' : 'bg-muted-soft']"
                        ></span>
                        记忆方法
                      </button>
                    </template>

                    <button
                        :class="['w-full text-left px-3 py-2 rounded-lg text-sm transition-all duration-300 ease-out flex items-center',
                          activeNavItem === 'explanation'
                            ? 'bg-surface-cream-strong text-ink font-medium'
                            : 'text-muted hover:bg-surface-soft hover:text-ink']"
                        @click="scrollToSection('explanation')"
                    >
                      <span :class="['w-1.5 h-1.5 rounded-full mr-2 transition-all duration-300 ease-out', 
                        activeNavItem === 'explanation' ? 'bg-primary scale-125' : 'bg-muted-soft']"
                      ></span>
                      释义
                    </button>

                    <template v-if="brief.sentences && brief.sentences.length > 0">
                      <button
                          :class="['w-full text-left px-3 py-2 rounded-lg text-sm transition-all duration-300 ease-out flex items-center',
                            activeNavItem === 'sentences'
                              ? 'bg-surface-cream-strong text-ink font-medium'
                              : 'text-muted hover:bg-surface-soft hover:text-ink']"
                          @click="scrollToSection('sentences')"
                      >
                        <span :class="['w-1.5 h-1.5 rounded-full mr-2 transition-all duration-300 ease-out', 
                          activeNavItem === 'sentences' ? 'bg-primary scale-125' : 'bg-muted-soft']"
                        ></span>
                        例句
                      </button>
                    </template>

                    <template v-if="brief.realExamSentences && brief.realExamSentences.length > 0">
                      <button
                          :class="['w-full text-left px-3 py-2 rounded-lg text-sm transition-all duration-300 ease-out flex items-center',
                            activeNavItem === 'real-exam-sentences'
                              ? 'bg-surface-cream-strong text-ink font-medium'
                              : 'text-muted hover:bg-surface-soft hover:text-ink']"
                          @click="scrollToSection('real-exam-sentences')"
                      >
                        <span :class="['w-1.5 h-1.5 rounded-full mr-2 transition-all duration-300 ease-out', 
                          activeNavItem === 'real-exam-sentences' ? 'bg-primary scale-125' : 'bg-muted-soft']"
                        ></span>
                        真题例句
                      </button>
                    </template>

                    <template v-if="brief.phrases && brief.phrases.length > 0">
                      <button
                          :class="['w-full text-left px-3 py-2 rounded-lg text-sm transition-all duration-300 ease-out flex items-center',
                            activeNavItem === 'phrases'
                              ? 'bg-surface-cream-strong text-ink font-medium'
                              : 'text-muted hover:bg-surface-soft hover:text-ink']"
                          @click="scrollToSection('phrases')"
                      >
                        <span :class="['w-1.5 h-1.5 rounded-full mr-2 transition-all duration-300 ease-out', 
                          activeNavItem === 'phrases' ? 'bg-primary scale-125' : 'bg-muted-soft']"
                        ></span>
                        短语
                      </button>
                    </template>

                    <template v-if="brief.synonyms && brief.synonyms.length > 0">
                      <button
                          :class="['w-full text-left px-3 py-2 rounded-lg text-sm transition-all duration-300 ease-out flex items-center',
                            activeNavItem === 'synonyms'
                              ? 'bg-surface-cream-strong text-ink font-medium'
                              : 'text-muted hover:bg-surface-soft hover:text-ink']"
                          @click="scrollToSection('synonyms')"
                      >
                        <span :class="['w-1.5 h-1.5 rounded-full mr-2 transition-all duration-300 ease-out', 
                          activeNavItem === 'synonyms' ? 'bg-primary scale-125' : 'bg-muted-soft']"
                        ></span>
                        同义词
                      </button>
                    </template>

                    <template v-if="brief.antonyms && brief.antonyms.length > 0">
                      <button
                          :class="['w-full text-left px-3 py-2 rounded-lg text-sm transition-all duration-300 ease-out flex items-center',
                            activeNavItem === 'antonyms'
                              ? 'bg-surface-cream-strong text-ink font-medium'
                              : 'text-muted hover:bg-surface-soft hover:text-ink']"
                          @click="scrollToSection('antonyms')"
                      >
                        <span :class="['w-1.5 h-1.5 rounded-full mr-2 transition-all duration-300 ease-out', 
                          activeNavItem === 'antonyms' ? 'bg-primary scale-125' : 'bg-muted-soft']"
                        ></span>
                        反义词
                      </button>
                    </template>

                    <template v-if="brief.relWords && brief.relWords.length > 0">
                      <button
                          :class="['w-full text-left px-3 py-2 rounded-lg text-sm transition-all duration-300 ease-out flex items-center',
                            activeNavItem === 'rel-words'
                              ? 'bg-surface-cream-strong text-ink font-medium'
                              : 'text-muted hover:bg-surface-soft hover:text-ink']"
                          @click="scrollToSection('rel-words')"
                      >
                        <span :class="['w-1.5 h-1.5 rounded-full mr-2 transition-all duration-300 ease-out', 
                          activeNavItem === 'rel-words' ? 'bg-primary scale-125' : 'bg-muted-soft']"
                        ></span>
                        衍生词
                      </button>
                    </template>
                  </nav>
                </div>
              </div>
            </div>

            <!-- 主要内容区域 -->
            <div class="flex-1 max-w-4xl">
              <div class="flex flex-col gap-8 pb-56">
                <!-- 单词卡片 -->
                <div id="word-card" class="bg-surface-card p-6 rounded-[8px] relative">
                  <div class="font-normal text-[48px] leading-[1.1] tracking-[-1px] text-ink mb-4">
                    {{ brief.word }}
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
                      <template v-if="brief.ukPhonetic">
                        <div class="flex items-center gap-2">
                          <span
                              class="font-mono text-[10px] tracking-[0.1em] uppercase text-muted min-w-[24px]">UK</span>
                          <span class="font-display text-[18px] italic text-phonetic tracking-[0.02em]">
                            /{{ brief.ukPhonetic }}/
                          </span>
                        </div>
                      </template>
                      <a-tooltip :content="'英音'">
                        <ml-audio-button :loading="brief.ukPlayer.isLoading" :playing="brief.ukPlayer.isPlaying"
                                         @click="playAudio('uk', brief.word, brief.ukPlayer as any)"/>
                      </a-tooltip>
                    </div>

                    <!-- 美式音标和播放控制 -->
                    <div class="flex items-center gap-2">
                      <template v-if="brief.usPhonetic">
                        <div class="flex items-center gap-2">
                          <span
                              class="font-mono text-[10px] tracking-[0.1em] uppercase text-muted min-w-[24px]">US</span>
                          <span class="font-display text-[18px] italic text-phonetic tracking-[0.02em]">
                            /{{ brief.usPhonetic }}/
                          </span>
                        </div>
                      </template>
                      <a-tooltip :content="'美音'">
                        <ml-audio-button :loading="brief.usPlayer.isLoading" :playing="brief.usPlayer.isPlaying"
                                         @click="playAudio('us', brief.word, brief.usPlayer as any)"/>
                      </a-tooltip>
                    </div>
                  </div>
                </div>

                <!-- 简明释义 -->
                <div id="brief-explanation" class="bg-surface-card p-6 rounded-[8px]">
                  <h2 class="font-display font-normal text-[28px] leading-[1.2] tracking-[-0.3px] text-ink mb-4">
                    简明释义
                  </h2>
                  <div class="space-y-3">
                    <template v-for="explanation in brief.explanation">
                      <div class="bg-surface-soft p-3 rounded-[8px] border border-hairline">
                        <div class="mb-2 last:mb-0">
                          <div class="flex gap-3 items-center">
                            <span
                                class="inline-flex items-center px-2 py-0.5 bg-surface-cream-strong text-ink text-[12px] font-medium rounded-full uppercase tracking-[1px]">
                              {{ explanation.pos ?? '网络' }}
                            </span>
                            <span class="text-[16px] font-normal text-body leading-[1.5]">{{
                                explanation.cn.join('，')
                              }}</span>
                          </div>
                        </div>
                      </div>
                    </template>
                  </div>
                </div>

                <!-- 词性变化 -->
                <template v-if="brief && (brief.vocabulary.did || brief.vocabulary.done || brief.vocabulary.doing ||
        brief.vocabulary.does || brief.vocabulary.comparative || brief.vocabulary.superlative ||
        brief.vocabulary.plural || brief.vocabulary.lemma)">
                  <div id="word-forms" class="bg-surface-card p-6 rounded-[8px]">
                    <h2 class="font-display font-normal text-[28px] leading-[1.2] tracking-[-0.3px] text-ink mb-4">
                      词形变化
                    </h2>
                    <template v-if="brief.vocabulary && (brief.vocabulary.did || brief.vocabulary.done || brief.vocabulary.doing ||
            brief.vocabulary.does || brief.vocabulary.comparative || brief.vocabulary.superlative ||
            brief.vocabulary.plural || brief.vocabulary.lemma)">
                      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                        <!-- 过去式 -->
                        <template v-if="brief.vocabulary.did">
                          <div
                              class="bg-canvas p-3 rounded-[6px] border border-hairline flex flex-col cursor-pointer transition-colors duration-200 hover:bg-surface-soft hover:border-primary"
                              @click="goToVocabulary(brief.vocabulary.did)">
                            <span class="text-[12px] font-medium text-muted mb-1">过去式</span>
                            <span class="text-[14px] font-medium text-primary">{{ brief.vocabulary.did }}</span>
                          </div>
                        </template>

                        <!-- 过去分词 -->
                        <template v-if="brief.vocabulary.done">
                          <div
                              class="bg-canvas p-3 rounded-[6px] border border-hairline flex flex-col cursor-pointer transition-colors duration-200 hover:bg-surface-soft hover:border-primary"
                              @click="goToVocabulary(brief.vocabulary.done)">
                            <span class="text-[12px] font-medium text-muted mb-1">过去分词</span>
                            <span class="text-[14px] font-medium text-primary">{{ brief.vocabulary.done }}</span>
                          </div>
                        </template>

                        <!-- 现在分词 -->
                        <template v-if="brief.vocabulary.doing">
                          <div
                              class="bg-canvas p-3 rounded-[6px] border border-hairline flex flex-col cursor-pointer transition-colors duration-200 hover:bg-surface-soft hover:border-primary"
                              @click="goToVocabulary(brief.vocabulary.doing)">
                            <span class="text-[12px] font-medium text-muted mb-1">现在分词</span>
                            <span class="text-[14px] font-medium text-primary">{{ brief.vocabulary.doing }}</span>
                          </div>
                        </template>

                        <!-- 第三人称单数 -->
                        <template v-if="brief.vocabulary.does">
                          <div
                              class="bg-canvas p-3 rounded-[6px] border border-hairline flex flex-col cursor-pointer transition-colors duration-200 hover:bg-surface-soft hover:border-primary"
                              @click="goToVocabulary(brief.vocabulary.does)">
                            <span class="text-[12px] font-medium text-muted mb-1">第三人称单数</span>
                            <span class="text-[14px] font-medium text-primary">{{ brief.vocabulary.does }}</span>
                          </div>
                        </template>

                        <!-- 比较级 -->
                        <template v-if="brief.vocabulary.comparative">
                          <div
                              class="bg-canvas p-3 rounded-[6px] border border-hairline flex flex-col cursor-pointer transition-colors duration-200 hover:bg-surface-soft hover:border-primary"
                              @click="goToVocabulary(brief.vocabulary.comparative)">
                            <span class="text-[12px] font-medium text-muted mb-1">比较级</span>
                            <span class="text-[14px] font-medium text-primary">{{
                                brief.vocabulary.comparative
                              }}</span>
                          </div>
                        </template>

                        <!-- 最高级 -->
                        <template v-if="brief.vocabulary.superlative">
                          <div
                              class="bg-canvas p-3 rounded-[6px] border border-hairline flex flex-col cursor-pointer transition-colors duration-200 hover:bg-surface-soft hover:border-primary"
                              @click="goToVocabulary(brief.vocabulary.superlative)">
                            <span class="text-[12px] font-medium text-muted mb-1">最高级</span>
                            <span class="text-[14px] font-medium text-primary">{{
                                brief.vocabulary.superlative
                              }}</span>
                          </div>
                        </template>

                        <!-- 复数 -->
                        <template v-if="brief.vocabulary.plural">
                          <div
                              class="bg-canvas p-3 rounded-[6px] border border-hairline flex flex-col cursor-pointer transition-colors duration-200 hover:bg-surface-soft hover:border-primary"
                              @click="goToVocabulary(brief.vocabulary.plural)">
                            <span class="text-[12px] font-medium text-muted mb-1">复数</span>
                            <span class="text-[14px] font-medium text-primary">{{ brief.vocabulary.plural }}</span>
                          </div>
                        </template>

                        <!-- 词根 -->
                        <template v-if="brief.vocabulary.lemma">
                          <div
                              class="bg-canvas p-3 rounded-[6px] border border-hairline flex flex-col cursor-pointer transition-colors duration-200 hover:bg-surface-soft hover:border-primary"
                              @click="goToVocabulary(brief.vocabulary.lemma)">
                            <span class="text-[12px] font-medium text-muted mb-1">词根</span>
                            <span class="text-[14px] font-medium text-primary">{{ brief.vocabulary.lemma }}</span>
                          </div>
                        </template>
                      </div>
                    </template>
                  </div>
                </template>

                <!-- 记忆方法 -->
                <template v-if="brief.remMethod && brief.remMethod.length > 0">
                  <div id="memory-method" class="bg-surface-card p-6 rounded-[8px]">
                    <h2 class="font-display font-normal text-[28px] leading-[1.2] tracking-[-0.3px] text-ink mb-4">
                      记忆方法
                    </h2>
                    <div class="space-y-3">
                      <template v-for="method in brief.remMethod">
                        <div
                            class="p-6 bg-gradient-to-br from-surface-cream-strong to-surface-card border border-hairline rounded-[8px] relative overflow-hidden">
                          <!-- 装饰圆点 -->
                          <div
                              class="absolute -top-10 -right-10 w-[120px] h-[120px] rounded-full bg-[radial-gradient(circle,rgba(184,92,56,0.08),transparent_70%)] pointer-events-none"></div>
                          <p class="text-[16px] leading-[2] text-body relative z-10"
                             v-html="formatMemoryMethod(method)"></p>
                        </div>
                      </template>
                    </div>
                  </div>
                </template>

                <!-- 释义 -->
                <div id="explanation" class="bg-surface-card p-6 rounded-[8px]">
                  <h2 class="font-display font-normal text-[28px] leading-[1.2] tracking-[-0.3px] text-ink mb-4">
                    释义
                  </h2>
                  <div class="space-y-6">
                    <template v-for="(explanation, index) in brief.explanation">
                      <div class="relative pl-4 border-l-2 border-primary/30">
                        <div
                            class="absolute -left-[11px] top-0 w-5 h-5 rounded-full bg-surface-card border-2 border-primary/30 flex items-center justify-center text-[10px] font-bold text-primary">
                          {{ index + 1 }}
                        </div>
                        <div>
                          <p class="text-[16px] font-medium text-ink mb-3">{{ explanation.pos ?? '网络' }}</p>
                          <ul class="space-y-3">
                            <li class="flex flex-col gap-3 text-sm">
                              <template v-if="explanation.en.length > 0">
                                <div class="bg-surface-soft p-4 rounded-[6px]">
                                  <span
                                      class="font-medium text-[13px] text-primary uppercase tracking-[1px] mb-2 block">英释</span>
                                  <ul class="space-y-2 ml-1">
                                    <template v-for="enItem in explanation.en">
                                      <li class="flex items-start">
                                        <span class="text-primary mr-2 text-[16px] leading-none">·</span>
                                        <span class="text-body text-[15px] leading-[1.55]">{{ enItem }}</span>
                                      </li>
                                    </template>
                                  </ul>
                                </div>
                              </template>
                              <div class="bg-canvas p-4 rounded-[6px] border border-hairline">
                                <span
                                    class="font-medium text-[13px] text-muted uppercase tracking-[1px] mb-2 block">中释</span>
                                <span class="text-body text-[15px] leading-[1.55]">{{ explanation.cn.join('，') }}</span>
                              </div>
                            </li>
                          </ul>
                        </div>
                      </div>
                    </template>
                  </div>
                </div>

                <!-- 例句 -->
                <template v-if="brief.sentences && brief.sentences.length > 0">
                  <div id="sentences" class="bg-surface-card p-6 rounded-[8px]">
                    <h2 class="font-display font-normal text-[28px] leading-[1.2] tracking-[-0.3px] text-ink mb-4">
                      例句
                    </h2>
                    <ul class="space-y-4">
                      <template v-for="sentence in brief.sentences">
                        <li class="flex items-start p-5 pl-6 bg-surface-soft rounded-[8px] border border-hairline relative overflow-hidden before:content-[''] before:absolute before:left-0 before:top-0 before:bottom-0 before:w-[4px] before:bg-gradient-to-b before:from-primary before:to-accent-amber group hover:shadow-sm transition-all duration-200">
                          <div class="flex-1">
                            <div class="flex items-start">
                              <p class="text-ink text-[17px] font-display italic leading-[1.6] mb-2 flex-1"
                                 v-html="highlightKeyword(sentence.content)"></p>
                              <div class="flex gap-2 ml-4">
                                <a-tooltip :content="'英音'">
                                  <ml-audio-button :loading="sentence.ukPlayer.isLoading"
                                                   :playing="sentence.ukPlayer.isPlaying"
                                                   @click="playAudio('uk', sentence.content, sentence.ukPlayer as any)"/>
                                </a-tooltip>

                                <a-tooltip :content="'美音'">
                                  <ml-audio-button :loading="sentence.usPlayer.isLoading"
                                                   :playing="sentence.usPlayer.isPlaying"
                                                   @click="playAudio('us', sentence.content, sentence.usPlayer as any)"/>
                                </a-tooltip>
                              </div>
                            </div>
                            <p class="text-body text-[15px] leading-[1.55]">{{ sentence.translation }}</p>
                          </div>
                        </li>
                      </template>
                    </ul>
                  </div>
                </template>

                <!-- 真题例句 -->
                <template v-if="brief.realExamSentences && brief.realExamSentences.length > 0">
                  <div id="real-exam-sentences" class="bg-surface-card p-6 rounded-[8px]">
                    <h2 class="font-display font-normal text-[28px] leading-[1.2] tracking-[-0.3px] text-ink mb-4">
                      真题例句
                    </h2>
                    <div class="space-y-4">
                      <template v-for="examSentence in brief.realExamSentences">
                        <div class="p-5 bg-surface-cream border border-hairline rounded-[6px] relative">
                          <div
                              class="inline-flex items-center gap-2 mb-2.5 font-mono text-[10px] tracking-[0.08em] uppercase text-muted">
                            <template v-if="examSentence.sourceInfo.level">
                              <span class="px-2 py-0.5 bg-primary text-white rounded-[3px] font-medium">
                                {{ examSentence.sourceInfo.level }}
                              </span>
                            </template>
                            <template v-if="examSentence.sourceInfo.year">
                              <span class="text-accent-light font-medium">
                                {{ examSentence.sourceInfo.year }}
                              </span>
                            </template>
                            <template v-if="examSentence.sourceInfo.type">
                              <span class="text-muted-soft">
                                {{ examSentence.sourceInfo.type }}
                              </span>
                            </template>
                          </div>
                          <p class="text-[14.5px] leading-[1.8] text-body italic"
                             v-html="highlightKeyword(examSentence.content)">
                          </p>
                        </div>
                      </template>
                    </div>
                  </div>
                </template>

                <!-- 短语 -->
                <template v-if="brief.phrases && brief.phrases.length > 0">
                  <div id="phrases" class="bg-surface-card p-6 rounded-[8px]">
                    <h2 class="font-display font-normal text-[28px] leading-[1.2] tracking-[-0.3px] text-ink mb-4">
                      短语
                    </h2>
                    <ul class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <template v-for="phrase in brief.phrases">
                        <li class="flex flex-col justify-center cursor-pointer transition-colors duration-200 hover:bg-surface-soft hover:border-primary p-4 rounded-[6px] border border-hairline bg-canvas"
                            @click="goToVocabulary(phrase.content)">
                          <span class="text-ink font-medium text-[16px] leading-[1.4] mb-1">{{ phrase.content }}</span>
                          <span class="text-muted text-[14px] leading-[1.4]">{{ phrase.translation }}</span>
                        </li>
                      </template>
                    </ul>
                  </div>
                </template>

                <!-- 同义词 -->
                <template v-if="brief.synonyms && brief.synonyms.length > 0">
                  <div id="synonyms" class="bg-surface-card p-6 rounded-[8px]">
                    <h2 class="font-display font-normal text-[28px] leading-[1.2] tracking-[-0.3px] text-ink mb-4">
                      同义词
                    </h2>
                    <div
                        class="p-6 bg-canvas border-t-[3px]  border-x border-b border-hairline rounded-[8px]">
                      <div class="font-mono text-[10px] tracking-[0.12em] uppercase text-syn-accent mb-4">Synonyms</div>
                      <div class="space-y-4">
                        <template v-for="synonymGroup in brief.synonyms">
                          <div>
                            <div class="font-mono text-[10px] text-muted tracking-[0.06em] mb-1">{{ synonymGroup.pos }}
                              &mdash; {{ synonymGroup.translation.join(' ') }}
                            </div>
                            <div class="flex flex-wrap gap-1.5 mt-1.5">
                              <template v-for="word in synonymGroup.words">
                                <span
                                    class="px-3.5 py-1 bg-surface-soft text-[17px] font-medium font-display text-ink border border-hairline rounded-[4px] hover:bg-surface-cream-strong hover:border-primary hover:text-primary transition-all cursor-pointer"
                                    @click="goToVocabulary(word)">
                                  {{ word }}
                                </span>
                              </template>
                            </div>
                          </div>
                        </template>
                      </div>
                    </div>
                  </div>
                </template>

                <!-- 反义词 -->
                <template v-if="brief.antonyms && brief.antonyms.length > 0">
                  <div id="antonyms" class="bg-surface-card p-6 rounded-[8px]">
                    <h2 class="font-display font-normal text-[28px] leading-[1.2] tracking-[-0.3px] text-ink mb-4">
                      反义词
                    </h2>
                    <div
                        class="p-6 bg-canvas border-t-[3px] border-x border-b border-hairline rounded-[8px]">
                      <div class="font-mono text-[10px] tracking-[0.12em] uppercase text-ant-accent mb-4">Antonyms</div>
                      <div>
                        <div class="font-mono text-[10px] text-muted tracking-[0.06em] mb-1">Opposite</div>
                        <div class="flex flex-wrap gap-1.5 mt-1.5">
                          <template v-for="antonym in brief.antonyms">
                            <span
                                class="px-3.5 py-1 bg-surface-soft text-[17px] font-medium font-display text-ink border border-hairline rounded-[4px] hover:bg-surface-cream-strong hover:border-primary hover:text-primary transition-all cursor-pointer"
                                @click="goToVocabulary(antonym)">
                              {{ antonym }}
                            </span>
                          </template>
                        </div>
                      </div>
                    </div>
                  </div>
                </template>

                <!-- 衍生词 -->
                <template v-if="brief.relWords && brief.relWords.length > 0">
                  <div id="rel-words" class="bg-surface-card p-6 rounded-[8px]">
                    <h2 class="font-display font-normal text-[28px] leading-[1.2] tracking-[-0.3px] text-ink mb-4">
                      衍生词
                    </h2>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      <template v-for="relWordGroup in brief.relWords">
                        <template v-for="word in relWordGroup.words">
                          <div
                              class="p-5 bg-canvas border border-hairline rounded-[6px] transition-colors duration-200 hover:bg-surface-soft hover:border-primary cursor-pointer"
                              @click="goToVocabulary(word.word)">
                            <div class="font-mono text-[9px] tracking-[0.1em] uppercase text-primary mb-1.5">
                              {{ relWordGroup.pos }}
                            </div>
                            <div class="font-display text-[20px] font-semibold text-ink mb-1">{{ word.word }}</div>
                            <div class="text-[13px] text-muted leading-[1.6]">{{ word.translation }}</div>
                          </div>
                        </template>
                      </template>
                    </div>
                  </div>
                </template>
              </div>
            </div>
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
                {{ brief.word }}
              </div>
              <!-- 音标和播放控制 -->
              <div class="flex flex-wrap gap-4 mb-4 justify-center">
                <!-- 英式音标和播放控制 -->
                <div class="flex items-center gap-2">
                  <template v-if="brief.ukPhonetic">
                    <div class="flex items-center text-gray-700 bg-gray-100 px-3 py-2 rounded-lg">
                      <span class="mr-1 text-xs font-semibold text-gray-700">英:</span>
                      <span class="font-serif text-xs">/{{ brief.ukPhonetic }}/</span>
                    </div>
                  </template>
                  <ml-audio-button
                      :loading="brief.ukPlayer.isLoading"
                      :playing="brief.ukPlayer.isPlaying"
                      class="w-7 h-7"
                      @click="playAudio('uk', brief.word, brief.ukPlayer as any)"
                  />
                </div>

                <!-- 美式音标和播放控制 -->
                <div class="flex items-center gap-2">
                  <template v-if="brief.usPhonetic">
                    <div class="flex items-center text-gray-700 bg-gray-100 px-3 py-2 rounded-lg">
                      <span class="mr-1 text-xs font-semibold text-gray-700">美:</span>
                      <span class="font-serif text-xs">/{{ brief.usPhonetic }}/</span>
                    </div>
                  </template>
                  <ml-audio-button
                      :loading="brief.usPlayer.isLoading"
                      :playing="brief.usPlayer.isPlaying"
                      class="w-7 h-7"
                      @click="playAudio('us', brief.word, brief.usPlayer as any)"
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
            <template v-if="(brief.explanation && brief.explanation.length > 0) ||
            (brief.synonyms && brief.synonyms.length > 0) || (brief.antonyms && brief.antonyms.length > 0) || (brief.relWords && brief.relWords.length > 0) ||
            (brief.explanation && brief.explanation.length > 0) ||
            (brief.sentences && brief.sentences.length > 0) ||
            (brief.realExamSentences && brief.realExamSentences.length > 0) ||
            (brief.phrases && brief.phrases.length > 0)">
              <div>
                <t-tabs :sticky-props="{offsetTop:48}" class="min-h-screen" default-value="0" sticky theme="line">
                  <template v-if="brief.explanation && brief.explanation.length > 0">
                    <t-tab-panel label="简明" value="0">
                      <div class="p-4">
                        <div class="space-y-4">
                          <!-- 基本释义 -->
                          <template v-for="explanation in brief.explanation">
                            <div class="pb-1">
                              <div class="flex gap-3 items-start">
                            <span
                                class="inline-flex items-center px-3 py-1 bg-blue-50 text-blue-700 text-xs font-semibold rounded-full">
                              {{ explanation.pos ?? '网络' }}
                            </span>
                                <span class="text-gray-800 text-sm leading-6 flex-1">{{
                                    explanation.cn.join('，')
                                  }}</span>
                              </div>
                            </div>
                            <a-divider/>
                          </template>

                          <!-- 词性变化 -->
                          <template v-if="brief.vocabulary && (brief.vocabulary.did || brief.vocabulary.done || brief.vocabulary.doing ||
                    brief.vocabulary.does || brief.vocabulary.comparative || brief.vocabulary.superlative ||
                    brief.vocabulary.plural || brief.vocabulary.lemma)">
                            <div class="pt-2">
                              <div class="grid grid-cols-2 gap-2">
                                <!-- 过去式 -->
                                <template v-if="brief.vocabulary.did">
                                  <div class="bg-gray-50/50 p-3 rounded-lg border border-gray-200 flex flex-col"
                                       @click="goToVocabulary(brief.vocabulary.did)">
                                    <span class="text-xs font-medium text-gray-600 mb-1">过去式</span>
                                    <span class="text-sm font-semibold text-green-700">{{ brief.vocabulary.did }}</span>
                                  </div>
                                </template>

                                <!-- 过去分词 -->
                                <template v-if="brief.vocabulary.done">
                                  <div class="bg-gray-50/50 p-3 rounded-lg border border-gray-200 flex flex-col"
                                       @click="goToVocabulary(brief.vocabulary.done)">
                                    <span class="text-xs font-medium text-gray-600 mb-1">过去分词</span>
                                    <span class="text-sm font-semibold text-green-700">{{
                                        brief.vocabulary.done
                                      }}</span>
                                  </div>
                                </template>

                                <!-- 现在分词 -->
                                <template v-if="brief.vocabulary.doing">
                                  <div class="bg-gray-50/50 p-3 rounded-lg border border-gray-200 flex flex-col"
                                       @click="goToVocabulary(brief.vocabulary.doing)">
                                    <span class="text-xs font-medium text-gray-600 mb-1">现在分词</span>
                                    <span class="text-sm font-semibold text-green-700">{{
                                        brief.vocabulary.doing
                                      }}</span>
                                  </div>
                                </template>

                                <!-- 第三人称单数 -->
                                <template v-if="brief.vocabulary.does">
                                  <div class="bg-gray-50/50 p-3 rounded-lg border border-gray-200 flex flex-col"
                                       @click="goToVocabulary(brief.vocabulary.does)">
                                    <span class="text-xs font-medium text-gray-600 mb-1">第三人称单数</span>
                                    <span class="text-sm font-semibold text-green-700">{{
                                        brief.vocabulary.does
                                      }}</span>
                                  </div>
                                </template>

                                <!-- 比较级 -->
                                <template v-if="brief.vocabulary.comparative">
                                  <div class="bg-gray-50/50 p-3 rounded-lg border border-gray-200 flex flex-col"
                                       @click="goToVocabulary(brief.vocabulary.comparative)">
                                    <span class="text-xs font-medium text-gray-600 mb-1">比较级</span>
                                    <span class="text-sm font-semibold text-green-700">{{
                                        brief.vocabulary.comparative
                                      }}</span>
                                  </div>
                                </template>

                                <!-- 最高级 -->
                                <template v-if="brief.vocabulary.superlative">
                                  <div class="bg-gray-50/50 p-3 rounded-lg border border-gray-200 flex flex-col"
                                       @click="goToVocabulary(brief.vocabulary.superlative)">
                                    <span class="text-xs font-medium text-gray-600 mb-1">最高级</span>
                                    <span class="text-sm font-semibold text-green-700">{{
                                        brief.vocabulary.superlative
                                      }}</span>
                                  </div>
                                </template>

                                <!-- 复数 -->
                                <template v-if="brief.vocabulary.plural">
                                  <div class="bg-gray-50/50 p-3 rounded-lg border border-gray-200 flex flex-col"
                                       @click="goToVocabulary(brief.vocabulary.plural)">
                                    <span class="text-xs font-medium text-gray-600 mb-1">复数</span>
                                    <span class="text-sm font-semibold text-green-700">{{
                                        brief.vocabulary.plural
                                      }}</span>
                                  </div>
                                </template>

                                <!-- 原型 -->
                                <template v-if="brief.vocabulary.lemma">
                                  <div
                                      class="bg-gray-50/50 p-3 rounded-lg border border-gray-200 flex flex-col cursor-pointer"
                                      @click="goToVocabulary(brief.vocabulary.lemma)">
                                    <span class="text-xs font-medium text-gray-600 mb-1">原型</span>
                                    <span class="text-sm font-semibold text-green-700">{{
                                        brief.vocabulary.lemma
                                      }}</span>
                                  </div>
                                </template>
                              </div>
                            </div>
                          </template>
                        </div>
                      </div>
                    </t-tab-panel>
                  </template>

                  <template
                      v-if="(brief.synonyms && brief.synonyms.length > 0) || (brief.antonyms && brief.antonyms.length > 0) || (brief.relWords && brief.relWords.length > 0)">
                    <t-tab-panel class="min-h-screen" label="相关" value="1">
                      <div class="p-4">
                        <div class="space-y-4">
                          <!-- 同义词 -->
                          <template v-if="brief.synonyms && brief.synonyms.length > 0">
                            <div>
                              <h3 class="text-base font-semibold text-gray-900 mb-3">同义词</h3>
                              <div class="space-y-4">
                                <template v-for="synonymGroup in brief.synonyms">
                                  <div>
                                    <div class="flex items-center gap-2 mb-2">
                                      <span class="text-xs font-medium text-gray-500">{{ synonymGroup.pos }}</span>
                                      <span class="text-xs text-gray-600">{{
                                          synonymGroup.translation.join(' ')
                                        }}</span>
                                    </div>
                                    <div class="flex flex-wrap gap-2">
                                      <template v-for="word in synonymGroup.words">
                                    <span
                                        class="px-3 py-1 text-sm text-blue-600 border border-blue-200 rounded-md cursor-pointer hover:bg-blue-50 transition-colors"
                                        @click="goToVocabulary(word)">
                                      {{ word }}
                                    </span>
                                      </template>
                                    </div>
                                  </div>
                                </template>
                              </div>
                            </div>
                            <a-divider/>
                          </template>

                          <!-- 反义词 -->
                          <template v-if="brief.antonyms && brief.antonyms.length > 0">
                            <div>
                              <h3 class="text-base font-semibold text-gray-900 mb-3">反义词</h3>
                              <div class="flex flex-wrap gap-2">
                                <template v-for="antonym in brief.antonyms">
                        <span
                            class="px-3 py-1 text-sm text-gray-700 border border-gray-200 rounded-md cursor-pointer hover:bg-gray-50 transition-colors"
                            @click="goToVocabulary(antonym)">
                          {{ antonym }}
                        </span>
                                </template>
                              </div>
                            </div>
                            <a-divider/>
                          </template>

                          <!-- 衍生词 -->
                          <template v-if="brief.relWords && brief.relWords.length > 0">
                            <div>
                              <h3 class="text-base font-semibold text-gray-900 mb-3">衍生词</h3>
                              <div class="space-y-3">
                                <template v-for="relWordGroup in brief.relWords">
                                  <div>
                                    <p class="text-xs font-medium text-gray-500 mb-2">{{ relWordGroup.pos }}</p>
                                    <div class="space-y-1">
                                      <template v-for="word in relWordGroup.words">
                                        <div class="flex justify-between items-center py-1 gap-5">
                                        <span
                                            class="text-sm text-gray-800 cursor-pointer hover:text-blue-600 transition-colors"
                                            @click="goToVocabulary(word.word)">
                                          {{ word.word }}
                                        </span>
                                          <span class="text-xs text-gray-500">{{ word.translation }}</span>
                                        </div>
                                      </template>
                                    </div>
                                  </div>
                                </template>
                              </div>
                            </div>
                            <a-divider/>
                          </template>
                        </div>
                      </div>
                    </t-tab-panel>
                  </template>

                  <template v-if="brief.explanation && brief.explanation.length > 0">
                    <t-tab-panel class="min-h-screen" label="专业" value="2">
                      <div class="p-4">
                        <div class="space-y-4">
                          <template v-for="explanation in brief.explanation">
                            <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
                              <p class="text-indigo-700 font-semibold mb-2 text-sm">{{ explanation.pos ?? '网络' }}</p>
                              <ul class="space-y-3">
                                <template v-if="explanation.en.length > 0">
                                  <li v-for="(enItem, index) in explanation.en" :key="index"
                                      class="flex flex-col gap-1">
                                    <span class="text-gray-800 text-sm leading-6 tracking-tight">{{ enItem }}</span>
                                    <span class="text-gray-600 text-sm">{{
                                        explanation.cn[index] || explanation.cn[0]
                                      }}</span>
                                  </li>
                                </template>
                                <template v-else>
                                  <li class="flex flex-col gap-1">
                                    <span class="text-gray-600 text-sm">{{ explanation.cn.join('，') }}</span>
                                  </li>
                                </template>
                              </ul>
                            </div>
                          </template>
                        </div>
                      </div>
                    </t-tab-panel>
                  </template>

                  <template v-if="brief.sentences && brief.sentences.length > 0">
                    <t-tab-panel class="min-h-screen" label="例句" value="3">
                      <div class="p-4">
                        <div class="space-y-4">
                          <template v-for="sentence in brief.sentences">
                            <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
                              <p class="text-gray-800 text-sm leading-6 mb-3"
                                 v-html="highlightKeyword(sentence.content)"></p>
                              <p class="text-gray-600 text-sm mb-3">{{ sentence.translation }}</p>
                              <div class="flex gap-3">
                                <ml-audio-button
                                    :loading="sentence.ukPlayer.isLoading"
                                    :playing="sentence.ukPlayer.isPlaying"
                                    class="w-7 h-7"
                                    @click="playAudio('uk', sentence.content, sentence.ukPlayer as any)"
                                />
                                <ml-audio-button
                                    :loading="sentence.usPlayer.isLoading"
                                    :playing="sentence.usPlayer.isPlaying"
                                    class="w-7 h-7"
                                    @click="playAudio('us', sentence.content, sentence.usPlayer as any)"
                                />
                              </div>
                            </div>
                          </template>
                        </div>
                      </div>
                    </t-tab-panel>
                  </template>

                  <template v-if="brief.realExamSentences && brief.realExamSentences.length > 0">
                    <t-tab-panel class="min-h-screen" label="真题" value="4">
                      <div class="p-4">
                        <div class="space-y-4">
                          <template v-for="(examSentence, index) in brief.realExamSentences"
                                    :key="examSentence.content">
                            <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
                              <div class="flex items-start">
                                <span class="text-blue-500 mr-3 mt-1 text-lg font-semibold">{{ index + 1 }}</span>
                                <div class="flex-1">
                                  <p class="text-gray-800 text-sm leading-6 mb-3"
                                     v-html="highlightKeyword(examSentence.content)"></p>
                                  <div class="flex flex-wrap gap-2">
                                    <template v-if="examSentence.sourceInfo.level">
                                <span class="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                                  {{ examSentence.sourceInfo.level }}
                                </span>
                                    </template>
                                    <template v-if="examSentence.sourceInfo.year">
                                <span class="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                                  {{ examSentence.sourceInfo.year }}
                                </span>
                                    </template>
                                    <template v-if="examSentence.sourceInfo.type">
                                <span class="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">
                                  {{ examSentence.sourceInfo.type }}
                                </span>
                                    </template>
                                    <template v-if="examSentence.sourceInfo.paper">
                                <span class="px-2 py-1 bg-orange-100 text-orange-700 rounded-full text-xs font-medium">
                                  {{ examSentence.sourceInfo.paper }}
                                </span>
                                    </template>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </template>
                        </div>
                      </div>
                    </t-tab-panel>
                  </template>

                  <template v-if="brief.phrases && brief.phrases.length > 0">
                    <t-tab-panel class="min-h-screen" label="短语" value="5">
                      <div class="p-4">
                        <div class="space-y-4">
                          <template v-for="phrase in brief.phrases">
                            <div class="bg-gray-50 p-4  rounded-lg border border-gray-200"
                                 @click="goToVocabulary(phrase.content)">
                              <div class="flex items-start">
                                <div class="flex-1">
                                  <p class="text-gray-800 text-sm font-bold mb-2">{{ phrase.content }}</p>
                                  <p class="text-gray-600 text-sm">{{ phrase.translation }}</p>
                                </div>
                              </div>
                            </div>
                          </template>
                        </div>
                      </div>
                    </t-tab-panel>
                  </template>
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
