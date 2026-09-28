<script lang="ts" setup>
import { type ComputedRef, ref, useTemplateRef } from 'vue';
import { useRouter } from 'vue-router';
import { searchVocabulary } from '@/api/search.ts';
import { useSearchHistoryStore } from '@/store/searchHistoryStore.ts';
import { useMobileDetector } from '@/utils/mobileDetector.ts';
import { IconSend } from '@arco-design/web-vue/es/icon';
import MlNavbar from '@/components/layout/MlNavbar.vue';


const router = useRouter();
const searchHistoryStore = useSearchHistoryStore();
const inputRef = useTemplateRef('input');
const scrollContainerRef = useTemplateRef('scroll-container');
const { isMobile } = useMobileDetector();
const query = ref('');
const searchResults = ref<any[]>([]);
const currentPage = ref(1);
const pageSize = 10;
const total = ref(0);
const isLoading = ref(false);
const searchPerformed = ref(false);
const isInputFocused = ref(false);
const showClearButton = ref(false);

const recentHistory = searchHistoryStore.getHistory(10) as ComputedRef<any[]>;

function goToDetail(vocabularyId: number) {
  router.push(`/vocabulary/${ vocabularyId }`);
  const searchItem = searchResults.value.find((item: any) => item.vocabularyId === vocabularyId);
  const historyItem = recentHistory.value.find((item: any) => item.vocabularyId === vocabularyId);
  searchHistoryStore.addHistory(searchItem ?? historyItem);
  query.value = '';
  resetSearchResults();
}

function resetSearchResults() {
  searchResults.value = [];
  searchPerformed.value = false;
  currentPage.value = 1;
  total.value = 0;
}

async function search() {
  if (!query.value.trim()) {
    resetSearchResults();
    return;
  }

  // 输入是否全是符号
  const isAllPunctuation = (str: string) => {
    const punctuationRegex = /^[\p{P}\p{S}]+$/u;
    return punctuationRegex.test(str);
  };

  if (isAllPunctuation(query.value.trim())) {
    return;
  }

  isLoading.value = true;
  searchPerformed.value = true;
  try {
    const resp = await searchVocabulary({
      query: query.value,
      page: currentPage.value,
      limit: 10
    });

    searchResults.value = resp.data.data;
    total.value = resp.data.total;
  } catch (err) {
    console.log(err);
  } finally {
    isLoading.value = false;
  }
}

function clearHistory() {
  searchHistoryStore.clearHistory();
}

function removeHistory(item: any) {
  searchHistoryStore.removeHistory(item);
  if (searchHistoryStore.history.length > 0) {
    inputRef.value?.focus();
  }
}


function onFocus() {
  isInputFocused.value = true;
}

function onBlur() {
  isInputFocused.value = false;
}

async function onChange(page: any) {
  if (isMobile.value) {
    scrollContainerRef.value?.scroll({ top: 0, behavior: 'smooth' });
  } else {
    window.scroll({ top: 0, behavior: 'smooth' });
  }
  currentPage.value = page;
  await search();
}

function clearInput() {
  query.value = '';
  resetSearchResults();
  showClearButton.value = false;
  inputRef.value?.focus();
}

async function onInput() {
  showClearButton.value = query.value.length > 0;
  currentPage.value = 1;
  if (query.value.trim()) {
    await search();
  } else {
    query.value = '';
  }
}

function onEnterKey() {
  if (searchResults.value.length === 0) {
    return;
  }

  goToDetail(searchResults.value[0].vocabularyId);
}

</script>

<template>
  <div class="min-h-screen">
    <!-- web -->
    <div class="hidden md:block px-3 py-24">
      <div class="max-w-4xl mx-auto">
        <div class="text-center mb-12">
          <div class="relative inline-block">
            <h1 class="font-display text-[48px] leading-[1.1] tracking-[-1px] text-ink mb-3 relative z-10">
              <span class="text-primary">单词检索</span>
            </h1>
            <p class="text-muted text-[16px]">海量单词，一键检索</p>
          </div>
        </div>

        <!-- 搜索框容器 -->
        <div
            :class="[searchPerformed ? 'translate-y-[-30px]' : 'translate-y-0', searchPerformed ? 'mb-[1rem]' : 'mb-[3rem]']"
            class="flex justify-center my-6 md:my-12 transition-all duration-500 ease-out"
        >
          <div class="relative w-full max-w-xl group">
            <input
                ref="input"
                v-model="query"
                autocomplete="off"
                class="w-full py-4 px-6 pr-14 rounded-[8px] border border-hairline focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none transition-all duration-300 text-[16px] bg-canvas placeholder-muted-soft text-ink"
                placeholder="请输入要搜索的单词..."
                @blur="onBlur"
                @focus="onFocus"
                @input="onInput"
                @keydown.enter="onEnterKey"
            />
            <button
                class="absolute right-3 top-1/2 -translate-y-1/2 bg-primary hover:bg-primary-active p-2 rounded-[6px] transition-all duration-300 cursor-pointer text-on-primary flex items-center justify-center h-10 w-10"
                @click="search"
            >
              <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20"
                   xmlns="http://www.w3.org/2000/svg">
                <path clip-rule="evenodd"
                      d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                      fill-rule="evenodd"/>
              </svg>
            </button>
          </div>
        </div>

        <transition mode="out-in" name="fade-from-bottom">
          <!-- 搜索历史面板 -->
          <template v-if="isInputFocused && query.trim().length === 0 && recentHistory.length > 0">
            <div
                class="mt-2 bg-surface-card rounded-[8px] shadow-sm border border-hairline z-10 transition-all duration-200 transform opacity-100 scale-100 origin-top">
              <div class="p-4">
                <div class="flex justify-between items-center mb-4 pb-2 border-b border-hairline-soft">
                  <h3 class="text-[13px] font-medium text-muted uppercase tracking-[1px] flex items-center">
                    搜索历史
                  </h3>
                  <button
                      v-if="recentHistory.length > 0"
                      class="text-[13px] text-muted hover:text-primary transition-colors flex items-center opacity-80 hover:opacity-100 font-medium"
                      @click="clearHistory"
                  >
                    全部清除
                  </button>
                </div>

                <div class="space-y-2 max-h-80 overflow-y-auto pr-1 scrollbar-thin">
                  <template v-for="item in recentHistory">
                    <div
                        class="bg-canvas rounded-[6px] border border-hairline overflow-hidden cursor-pointer hover:border-primary transition-all duration-200"
                        @click="goToDetail(item.vocabularyId)"
                    >
                      <div class="group/word-item">
                        <div class="p-5 hover:bg-surface-soft transition-colors duration-150">
                          <div class="flex items-center">
                            <h3 class="text-[16px] font-medium text-ink mr-3 flex-shrink-0"
                                v-html="item.highlight?.word || item.word">
                            </h3>
                            <div class="flex-1 min-w-0">
                              <p class="text-body text-[14px] truncate"
                                 v-html="item.highlight?.translation || item.translation">
                              </p>
                            </div>
                            <div class="flex-shrink-0 text-muted-soft ml-2 transition-all duration-200 group-hover/word-item:text-primary group-hover/word-item:translate-x-1">
                              <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                                <path clip-rule="evenodd"
                                      d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                                      fill-rule="evenodd"></path>
                              </svg>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div
                          class="p-2.5 text-muted hover:text-error transition-all duration-200 flex-shrink-0 w-full text-left border-t border-hairline-soft hover:bg-red-50 flex items-center justify-between group/delete"
                          @click.stop="removeHistory(item)"
                      >
                        <div class="flex items-center">
                          <svg class="w-4 h-4 mr-2 transition-transform duration-200 group-hover/delete:scale-110"
                               fill="currentColor" viewBox="0 0 20 20">
                            <path clip-rule="evenodd"
                                  d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                                  fill-rule="evenodd"></path>
                          </svg>
                          <span class="text-[13px]">删除此记录</span>
                        </div>
                      </div>
                    </div>
                  </template>
                </div>
              </div>
            </div>
          </template>
          
          <!-- 搜索结果区域 -->
          <template v-else-if="searchPerformed">
            <div
                :class="[searchPerformed ? 'opacity-100' : 'opacity-0', searchPerformed ? 'translate-y-0' : 'translate-y-[20px]']"
                class="flex-1 transition-all duration-500 ease-in"
            >
              <transition mode="out-in" name="fade">
                <template v-if="isLoading">
                  <div class="flex flex-col items-center justify-center py-12 text-muted">
                    <div class="w-8 h-8 border-2 border-hairline border-t-primary rounded-full animate-spin mb-4"></div>
                    <p class="text-[15px] font-medium">搜索中...</p>
                  </div>
                </template>
                <template v-else-if="searchResults && searchResults.length > 0">
                  <div class="bg-surface-card p-6 rounded-[8px] border border-hairline">
                    <div class="flex justify-between items-center mb-5 pb-3 border-b border-hairline-soft">
                      <h2 class="text-[18px] font-medium text-ink">搜索结果</h2>
                      <p class="text-[13px] text-muted">{{ total }} 个结果</p>
                    </div>

                    <div class="space-y-3">
                      <div
                          v-for="result in searchResults"
                          :key="result.vocabularyId"
                          class="bg-canvas rounded-[6px] border border-hairline cursor-pointer hover:border-primary transition-all duration-200"
                          @click="goToDetail(result.vocabularyId)"
                      >
                        <div class="p-4">
                          <div class="flex items-center">
                            <h3 class="text-[16px] font-medium text-ink mr-4 flex-shrink-0 min-w-[120px]"
                                v-html="result.highlight && result.highlight.word ? result.highlight.word : result.word">
                            </h3>
                            <div class="flex-1 min-w-0">
                              <p class="text-[14px] text-body truncate"
                                 v-html="result.highlight && result.highlight.translation ? result.highlight.translation : result.translation">
                              </p>
                            </div>
                            <div class="flex-shrink-0 text-muted-soft ml-2">
                              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path d="M9 5l7 7-7 7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                              </svg>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div class="pt-4 flex justify-center">
                        <a-pagination :current="currentPage" :page-size="pageSize" :total="total" hide-on-single-page
                                      simple @change="onChange">
                          <template #page-item-step="{ type }">
                            <icon-send :style="type==='previous' ? {transform:`rotate(180deg)`} : undefined"/>
                          </template>
                        </a-pagination>
                      </div>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <div class="flex flex-col items-center justify-center py-16 text-center bg-surface-card rounded-[8px] border border-hairline">
                    <div class="bg-surface-soft p-4 rounded-full mb-4">
                      <svg class="h-8 w-8 text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"/>
                      </svg>
                    </div>
                    <h3 class="text-[16px] font-medium text-ink mb-2">未找到相关结果</h3>
                    <p class="text-body text-[14px] max-w-md">抱歉，没有找到与 "{{ query }}" 相关的结果</p>
                  </div>
                </template>
              </transition>
            </div>
          </template>

          <!-- 默认欢迎/功能展示状态 -->
          <template v-else>
            <div class="mt-16">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
                <div class="group p-6 rounded-[8px] bg-surface-card border border-hairline hover:border-primary transition-all duration-300">
                  <div class="w-12 h-12 bg-canvas border border-hairline text-ink rounded-[6px] flex items-center justify-center mx-auto mb-4 group-hover:bg-primary group-hover:text-on-primary group-hover:border-transparent transition-all duration-300">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                    </svg>
                  </div>
                  <h3 class="text-[16px] font-medium text-ink mb-2">精准搜索</h3>
                  <p class="text-body text-[14px] leading-[1.55]">支持中英文互译，智能匹配，快速找到你想要的单词解释</p>
                </div>

                <div class="group p-6 rounded-[8px] bg-surface-card border border-hairline hover:border-primary transition-all duration-300">
                  <div class="w-12 h-12 bg-canvas border border-hairline text-ink rounded-[6px] flex items-center justify-center mx-auto mb-4 group-hover:bg-primary group-hover:text-on-primary group-hover:border-transparent transition-all duration-300">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                    </svg>
                  </div>
                  <h3 class="text-[16px] font-medium text-ink mb-2">历史记录</h3>
                  <p class="text-body text-[14px] leading-[1.55]">自动保存搜索历史，方便随时回顾和复习，记录你的学习轨迹</p>
                </div>

                <div class="group p-6 rounded-[8px] bg-surface-card border border-hairline hover:border-primary transition-all duration-300">
                  <div class="w-12 h-12 bg-canvas border border-hairline text-ink rounded-[6px] flex items-center justify-center mx-auto mb-4 group-hover:bg-primary group-hover:text-on-primary group-hover:border-transparent transition-all duration-300">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                    </svg>
                  </div>
                  <h3 class="text-[16px] font-medium text-ink mb-2">详细释义</h3>
                  <p class="text-body text-[14px] leading-[1.55]">提供详尽的单词解释、例句和发音，助你深入理解每个词汇</p>
                </div>
              </div>
            </div>
          </template>
        </transition>
      </div>
    </div>

    <!-- h5 -->
    <div class="h-screen flex flex-col md:hidden px-3">
      <!-- 顶部导航栏 -->
      <div class="h-12">
        <ml-navbar title="单词搜索"/>
      </div>
      <!-- 搜索区域 -->
      <div class="py-4 pb-2">
        <div class="relative">
          <input
              v-model="query"
              autocomplete="off"
              class="w-full py-3 px-4 pr-10 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-0 focus:outline-none bg-white placeholder-gray-400 text-base transition-all duration-300"
              placeholder="请输入要搜索的单词..."
              @input="onInput"
              @keydown.enter="onEnterKey"
          />
          <transition mode="out-in" name="fade">
            <template v-if="showClearButton">
              <button
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
                  @click="clearInput"
              >
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path clip-rule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                        fill-rule="evenodd"/>
                </svg>
              </button>
            </template>

            <template v-else>
              <button
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 transition-colors duration-200"
                  @click="search"
              >
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path clip-rule="evenodd"
                        d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                        fill-rule="evenodd"/>
                </svg>
              </button>
            </template>
          </transition>
        </div>
      </div>
      <!-- 内容区域 -->
      <div ref="scroll-container" class="flex-1 overflow-auto pb-4">
        <transition mode="out-in" name="slide-fade">
          <!-- 搜索历史面板 -->
          <template v-if="query.trim().length === 0 && recentHistory.length > 0">
            <div
                class="pt-2">
              <div class="flex justify-between items-center mb-3">
                <h3 class="text-sm font-medium text-gray-700 flex items-center">
                  <svg class="w-4 h-4 mr-1 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
                    <path clip-rule="evenodd"
                          d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z"
                          fill-rule="evenodd"/>
                  </svg>
                  搜索历史
                </h3>
                <template v-if="recentHistory.length > 0">
                  <button
                      class="text-xs text-gray-500 hover:text-blue-600 transition-colors flex items-center opacity-80 hover:opacity-100"
                      @click="clearHistory"
                  >
                    <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path clip-rule="evenodd"
                            d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                            fill-rule="evenodd"/>
                    </svg>
                    清空
                  </button>
                </template>
              </div>

              <div class="space-y-2">
                <transition-group name="list">
                  <template v-for="item in recentHistory" :key="item.vocabularyId">
                    <div
                        class="bg-white rounded-2xl p-3 border border-gray-100 relative active:bg-gray-50 transition-all duration-200"
                        @click="goToDetail(item.vocabularyId)"
                    >
                      <div class="flex items-center justify-between">
                        <div class="flex-1 min-w-0">
                          <h3 class="text-base font-medium text-gray-900 truncate"
                              v-html="item.highlight?.word || item.word"></h3>
                          <p class="text-sm text-gray-500 truncate mt-1"
                             v-html="item.highlight?.translation || item.translation"></p>
                        </div>
                        <button
                            class="ml-2 p-1 text-gray-400 hover:text-red-500 active:scale-95 transition-all duration-200"
                            @click.stop="removeHistory(item)"
                        >
                          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path clip-rule="evenodd"
                                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                                  fill-rule="evenodd"/>
                          </svg>
                        </button>
                      </div>
                    </div>
                  </template>
                </transition-group>
              </div>
            </div>
          </template>

          <!-- 搜索结果区域 -->
          <template v-else-if="searchPerformed">
            <div class="px-4">
              <transition mode="out-in" name="fade">
                <template v-if="isLoading">
                  <div class="flex flex-col items-center justify-center py-12 text-gray-600">
                    <div
                        class="w-8 h-8 border-2 border-gray-200 border-t-blue-500 rounded-full animate-spin mb-3"></div>
                    <p class="text-base">搜索中...</p>
                  </div>
                </template>
                <template v-else-if="searchResults && searchResults.length > 0">
                  <div class="space-y-4">
                    <div class="mb-3 flex items-center justify-between">
                      <h2 class="text-base font-medium text-gray-800 flex items-center">
                        <svg class="w-4 h-4 mr-1 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                          <path clip-rule="evenodd"
                                d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                                fill-rule="evenodd"/>
                        </svg>
                        搜索结果
                      </h2>
                      <p class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">{{ total }} 个结果</p>
                    </div>

                    <!-- 搜索结果列表 -->
                    <div class="space-y-2">
                      <template v-for="result in searchResults">
                        <div
                            class="bg-white rounded-2xl p-3 border border-gray-100 overflow-hidden cursor-pointer active:bg-gray-50 transition-all duration-200"
                            @click="goToDetail(result.vocabularyId)"
                        >
                          <div class="flex items-center justify-between">
                            <div class="flex-1 min-w-0">
                              <h3 class="text-base font-medium text-gray-900 truncate"
                                  v-html="result.highlight && result.highlight.word ? result.highlight.word : result.word">
                              </h3>
                              <p class="text-sm text-gray-500 truncate mt-1"
                                 v-html="result.highlight && result.highlight.translation
                             ? result.highlight.translation
                             : result.translation">
                              </p>
                            </div>
                            <div class="flex-shrink-0 text-gray-400 ml-2">
                              <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                                <path clip-rule="evenodd"
                                      d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                                      fill-rule="evenodd"/>
                              </svg>
                            </div>
                          </div>
                        </div>
                      </template>
                    </div>

                    <!-- 分页 -->
                    <a-pagination :current="currentPage" :page-size="pageSize" :total="total" hide-on-single-page simple
                                  @change="onChange">
                      <template #page-item-step="{ type }">
                        <icon-send :style="type==='previous' ? {transform:`rotate(180deg)`} : undefined"/>
                      </template>
                    </a-pagination>
                  </div>
                </template>
                <!-- 无搜索结果 -->
                <template v-else>
                  <div class="flex flex-col items-center justify-center py-12 text-center">
                    <div class="bg-gray-100 p-4 rounded-full mb-4">
                      <svg class="h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                              stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                      </svg>
                    </div>
                    <h3 class="text-base font-medium text-gray-800 mb-1">未找到相关结果</h3>
                    <p class="text-sm text-gray-500 px-4">抱歉，没有找到与 "{{ query }}" 相关的结果</p>
                  </div>
                </template>
              </transition>
            </div>
          </template>

          <!-- 默认状态 -->
          <template v-else>
            <div class="px-4">
              <div class="pt-8">
                <div class="text-center mb-6">
                  <div
                      class="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-3 transition-all duration-500 hover:scale-105">
                    <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"/>
                    </svg>
                  </div>
                  <h2 class="text-lg font-semibold text-gray-900 mb-1">单词搜索</h2>
                  <p class="text-gray-500 text-sm">输入单词或短语开始搜索</p>
                </div>
              </div>
            </div>
          </template>
        </transition>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 滑动淡入过渡 */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}

.slide-fade-enter-from {
  transform: translateY(10px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}


/* 基础过渡设置 */
.list-move,
.list-enter-active,
.list-leave-active {
  transition: all 0.4s cubic-bezier(0.25, 0.1, 0.25, 1);
}

/* 入场/退场初始状态 */
.list-enter-from {
  opacity: 0;
  transform: translateX(10px);
}

/* 优化删除动画：向右淡出并缩小 */
.list-leave-from {
  /* 保留删除前的原始状态作为过渡起点 */
  opacity: 1;
  transform: translateX(0) scale(1);
}

.list-leave-to {
  opacity: 0;
  transform: translateX(20px) scale(0.95); /* 向右移动更远并轻微缩小 */
}

/* 关键优化：删除时脱离文档流但保持占位，避免其他元素瞬移 */
.list-leave-active {
  position: absolute;
  /* 固定宽度防止布局抖动 */
  width: calc(100% - 20px); /* 根据实际内边距调整 */
  pointer-events: none; /* 避免删除过程中触发交互 */
}

/* 移动动画优化：其他元素填补空位时更平滑 */
.list-move {
  transition-delay: 0.05s; /* 等待删除动画开始后再移动 */
}
</style>