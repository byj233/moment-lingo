<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue';
import { listBooks } from '@/api/book.ts';
import MlNavbar from '@/components/layout/MlNavbar.vue';
import { useRouter } from 'vue-router';
import { delay } from '@/utils/common.ts';
import NoDataView from '@/views/NoDataView.vue';

interface Book {
  bookId: number;
  wordCount: number;
  title: string;
  tags: string[];
}

const router = useRouter();
const isLoading = ref(true);
const isDataExist = ref(true);
const searchQuery = ref('');
const selectedTag = ref('');
const books = ref<Book[]>([]);
const allTags = ref<string[]>([]);

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


const filteredBooks = computed(() => {
  let filtered = books.value;

  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim();
    filtered = filtered.filter(book =>
        book.title.toLowerCase().includes(query)
    );
  }

  if (selectedTag.value) {
    filtered = filtered.filter(book =>
        book.tags.includes(selectedTag.value)
    );
  }

  return filtered;
});

function goToBookDetail(bookId: number) {
  router.push(`/book/${ bookId }`);
}

onMounted(async () => {
  try {
    isLoading.value = true;

    const resp = await listBooks();
    await delay(150);
    books.value = resp.data;

    const tagsSet = new Set<string>();
    books.value.forEach(book => {
      book.tags.forEach(tag => tagsSet.add(tag));
    });
    allTags.value = Array.from(tagsSet).sort();
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
      <ml-navbar title="词书"/>
    </div>

    <!-- web & h5 -->
    <div class="min-h-screen py-16 md:py-24 px-4 md:px-3">
      <transition mode="out-in" name="fade-slide">
        <template v-if="!isLoading">
          <div class="max-w-6xl mx-auto">
            <div class="text-center mb-8 md:mb-12 hidden md:block">
              <div class="relative inline-block">
                <h1 class="font-display text-[48px] leading-[1.1] tracking-[-1px] text-ink mb-3 relative z-10">
                  <span class="text-primary">词汇书籍</span>
                </h1>
                <p class="text-muted text-[16px]">精选词汇学习资源，助力语言提升</p>
              </div>
            </div>

            <div class="mb-6 md:mb-8">
              <!-- 搜索框 -->
              <div class="flex justify-center mb-4 md:mb-6">
                <div class="relative w-full max-w-xl">
                  <input v-model="searchQuery"
                         class="w-full py-3 px-5 pr-12 rounded-[8px] border border-hairline focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none transition-all duration-300 text-base bg-canvas placeholder-muted-soft text-ink"
                         placeholder="搜索词书名称..." type="text"/>
                  <div class="absolute right-4 top-1/2 -translate-y-1/2">
                    <svg class="h-5 w-5 text-muted-soft" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-linecap="round"
                            stroke-linejoin="round" stroke-width="2"></path>
                    </svg>
                  </div>
                </div>
              </div>

              <!-- 标签筛选 -->
              <div class="flex flex-wrap justify-center gap-2 md:gap-3 mb-4 md:mb-6">
                <button
                    :class="selectedTag === '' ? 'bg-primary text-on-primary' : 'bg-surface-card text-body hover:bg-surface-soft border border-hairline'"
                    class="px-4 py-2 rounded-full transition-all duration-300 font-medium text-[13px] active:scale-95"
                    @click="selectedTag = ''">
                  全部
                </button>
                <template v-for="tag in allTags" :key="tag">
                  <button
                      :class="selectedTag === tag ? 'bg-primary text-on-primary' : 'bg-surface-card text-body hover:bg-surface-soft border border-hairline'"
                      class="px-4 py-2 rounded-full transition-all duration-300 font-medium text-[13px] active:scale-95"
                      @click="selectedTag = tag">
                    {{ tag }}
                  </button>
                </template>
              </div>
            </div>

            <div class="mt-6 md:mt-12 grid grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
              <template v-for="book in filteredBooks" :key="book.bookId">
                <div
                    class="cursor-pointer group bg-surface-card rounded-[12px] shadow-sm hover:shadow-md transition-all duration-300 ease-in-out transform active:scale-[0.98] border border-hairline overflow-hidden"
                    @click="goToBookDetail(book.bookId)">
                  <!-- 词书封面区域 - 使用随机主题色 -->
                  <div :class="getBookCoverGradient(book.bookId)" class="relative h-36 md:h-48 overflow-hidden">
                    <div class="absolute inset-0 flex items-center justify-center">
                      <div class="text-center text-white px-3">
                        <div class="text-lg md:text-2xl font-bold leading-tight">{{ book.title }}</div>
                      </div>
                    </div>
                  </div>

                  <!-- 词书信息 -->
                  <div class="p-4 md:p-6">
                    <!-- 标题 -->
                    <h3 class="text-base md:text-xl font-medium text-ink mb-2 line-clamp-2">
                      {{ book.title }}
                    </h3>

                    <!-- 词汇数量 -->
                    <div class="flex items-center text-muted mb-3">
                      <svg class="w-3.5 h-3.5 md:w-4 md:h-4 mr-1.5" fill="none" stroke="currentColor"
                           viewBox="0 0 24 24">
                        <path
                            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                            stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                      </svg>
                      <span class="text-xs md:text-sm">{{ book.wordCount }} 词汇</span>
                    </div>

                    <!-- 标签 -->
                    <div class="flex flex-wrap gap-1.5 md:gap-2 mb-4">
                      <template v-for="tag in book.tags" :key="tag">
                          <span
                              class="inline-flex items-center px-2.5 py-1 rounded-full text-[10px] md:text-xs font-medium bg-primary/5 text-primary border border-primary/10">
                            <svg class="w-2.5 h-2.5 md:w-3 md:h-3 mr-1 text-primary/60" fill="currentColor"
                                 viewBox="0 0 20 20">
                              <path clip-rule="evenodd"
                                    d="M17.707 9.293a1 1 0 010 1.414l-7 7a1 1 0 01-1.414 0l-7-7A.997.997 0 012 10V5a3 3 0 013-3h5c.256 0 .512.098.707.293l7 7zM5 6a1 1 0 100-2 1 1 0 000 2z"
                                    fill-rule="evenodd"></path>
                            </svg>
                            {{ tag }}
                          </span>
                      </template>
                    </div>

                    <!-- 操作按钮 -->
                    <button
                        class="transition duration-300 cursor-pointer w-full bg-primary text-on-primary py-2.5 md:py-3 rounded-[8px] font-medium text-sm hover:bg-primary-active active:scale-[0.98]">
                      查看详情
                    </button>
                  </div>
                </div>
              </template>
            </div>

            <template v-if="filteredBooks.length === 0">
              <div class="text-center py-12">
                <div class="text-muted text-lg">未找到匹配的词书</div>
                <div class="text-muted-soft text-[14px] mt-2">尝试调整搜索条件或标签筛选</div>
              </div>
            </template>

          </div>
        </template>
      </transition>
    </div>
  </div>
  </template>
</template>
