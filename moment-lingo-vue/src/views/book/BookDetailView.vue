<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import MlNavbar from '@/components/layout/MlNavbar.vue';
import { getBook, listBookDetail } from '@/api/book.ts';
import NoDataView from '@/views/NoDataView.vue';

interface Book {
  bookId: number;
  wordCount: number;
  title: string;
  tags: string[];
}

interface Explanation {
  pos: string;
  en: string[];
  cn: string[];
}

interface VocabularyItem {
  vocabularyId: number;
  vocabulary: string;
  phonetic?: string;
  explanation?: Explanation[];
  rank?: number;
  tags?: string[];
  translation?: string[];
}

const route = useRoute();
const router = useRouter();
const bookId = computed(() => Number(route.params.bookId));

const isLoading = ref(true);
const isDataExist = ref(true);
const currentPage = ref(1);
const pageSize = 20;
const total = ref(0);
const book = ref<Book | null>(null);
const vocabularyItems = ref<VocabularyItem[]>([]);

const coverGradients = [
  'bg-gradient-to-br from-primary to-accent-teal',
  'bg-gradient-to-br from-accent-teal to-primary',
  'bg-gradient-to-br from-primary to-accent-amber',
  'bg-gradient-to-br from-accent-amber to-primary',
  'bg-gradient-to-br from-primary-active to-accent-teal',
  'bg-gradient-to-br from-accent-teal to-primary-active',
  'bg-gradient-to-br from-primary-active to-accent-amber',
  'bg-gradient-to-br from-accent-amber to-primary-active',
  'bg-gradient-to-br from-accent-teal to-accent-amber',
  'bg-gradient-to-br from-accent-amber to-accent-teal'
];

function getBookCoverGradient(bookId: number) {
  const index = bookId % coverGradients.length;
  return coverGradients[index];
}

async function listVocabularies() {
  window.scroll({ top: 0, behavior: 'smooth' });
  try {
    isLoading.value = true;
    const resp = await listBookDetail(bookId.value, currentPage.value, pageSize);
    vocabularyItems.value = resp.data.data as VocabularyItem[];
    total.value = resp.data.total;
  } catch (error) {
    console.error('加载单词列表失败:', error);
  } finally {
    isLoading.value = false;
  }
}

function goToVocabulary(vocabularyId: number) {
  router.push(`/vocabulary/${ vocabularyId }`);
}

async function handlePageChange(newPage: number) {
  currentPage.value = newPage;
  await listVocabularies();
}

onMounted(async () => {
  try {
    isLoading.value = true;
    let resp = await getBook(bookId.value);
    book.value = resp.data;
    await listVocabularies();
  } catch (_) {
    isDataExist.value = false;
  } finally {
    isLoading.value = false;
  }
});
</script>

<template>
  <template v-if="!isDataExist">
    <no-data-view/>
  </template>
  <template v-else>
  <div>
    <div class="h-12 md:hidden">
      <ml-navbar title="词书详情"/>
    </div>

    <div class="min-h-screen py-16 md:py-24 px-4 md:px-3 bg-canvas">
      <transition mode="out-in" name="fade-slide">
        <template v-if="!isLoading && book">
          <div class="max-w-4xl mx-auto">
            <div class="mb-8">
              <div
                  :class="getBookCoverGradient(book.bookId)"
                  class="relative rounded-[12px] p-6 md:p-8 text-white shadow-sm overflow-hidden"
              >
                <div class="relative z-10">
                  <h1 class="text-2xl md:text-4xl font-display font-normal mb-4">{{ book.title }}</h1>
                  <div class="flex flex-wrap gap-3 mb-4">
                    <div class="flex items-center text-white/90">
                      <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                            stroke-linecap="round" stroke-linejoin="round"
                            stroke-width="2"
                        ></path>
                      </svg>
                      <span>{{ book.wordCount }} 词汇</span>
                    </div>
                  </div>
                  <div class="flex flex-wrap gap-2">
                    <template v-for="tag in book.tags" :key="tag">
                    <span
                        class="px-3 py-1 rounded-full text-[13px] font-medium bg-white/20 backdrop-blur-sm"
                    >
                      {{ tag }}
                    </span>
                    </template>
                  </div>
                </div>
              </div>
            </div>

            <div class="bg-surface-card rounded-[8px] border border-hairline overflow-hidden">
              <div class="px-6 py-4 border-b border-hairline">
                <div>
                  <h2 class="text-[18px] font-medium text-ink">单词列表</h2>
                  <p class="text-caption text-muted mt-1">共 {{ total }} 个单词</p>
                </div>
              </div>

              <template v-if="vocabularyItems.length === 0">
                <div class="py-12 text-center">
                  <svg class="w-16 h-16 mx-auto text-muted-soft mb-4" fill="none" stroke="currentColor"
                       viewBox="0 0 24 24">
                    <path
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        stroke-linecap="round" stroke-linejoin="round"
                        stroke-width="2"></path>
                  </svg>
                  <p class="text-muted">暂无单词</p>
                </div>
              </template>
              <template v-else>
                <div class="divide-y divide-hairline">
                  <template v-for="item in vocabularyItems" :key="item.vocabularyId">
                    <div
                        class="px-6 py-4 transition-colors duration-200 hover:bg-surface-soft cursor-pointer"
                        @click="goToVocabulary(item.vocabularyId)"
                    >
                      <div class="flex items-start justify-between">
                        <div class="flex items-start flex-1">
                        <span
                            class="w-10 h-10 flex items-center justify-center bg-primary/10 text-primary rounded-full text-base font-medium mr-4 flex-shrink-0">
                          {{ item.rank }}
                        </span>
                          <div class="flex-1">
                            <div class="flex items-center gap-3 mb-2">
                              <span class="text-xl font-medium text-ink">{{ item.vocabulary }}</span>
                              <template v-if="item.phonetic">
                                <span class="text-sm text-muted font-serif">/ {{ item.phonetic }} /</span>
                              </template>
                            </div>
                            <template v-if="item.explanation && item.explanation.length > 0">
                              <div class="space-y-2 mt-2">
                                <template v-for="exp in item.explanation">
                                  <div class="flex items-start gap-2">
                                    <span
                                        class="inline-flex items-center px-2 py-0.5 bg-surface-soft text-body text-xs font-medium rounded-[4px] flex-shrink-0">
                                      {{ exp.pos ?? '网络' }}
                                    </span>
                                    <span class="text-body text-[14px] leading-relaxed">{{ exp.cn.join('，') }}</span>
                                  </div>
                                </template>
                              </div>
                            </template>
                          </div>
                        </div>
                        <svg class="w-6 h-6 text-muted-soft flex-shrink-0 ml-4 mt-1" fill="none"
                             stroke="currentColor"
                             viewBox="0 0 24 24">
                          <path d="M9 5l7 7-7 7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                        </svg>
                      </div>
                    </div>
                  </template>
                </div>

                <div class="px-6 py-4 border-t border-hairline">
                  <a-pagination :current="currentPage" :page-size="pageSize" :total="total" hide-on-single-page
                                simple @change="handlePageChange"/>
                </div>
              </template>
            </div>
          </div>
        </template>
      </transition>
    </div>
  </div>
  </template>
</template>

<style scoped>
</style>
