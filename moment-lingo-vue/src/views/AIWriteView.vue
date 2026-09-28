<script lang="ts" setup>
import { computed, ref } from 'vue';
import { MlMessage } from '@/utils/feedBack.ts';
import { AIWrite } from '@/api/ai.ts';
import DesktopOnly from '@/components/DesktopOnly.vue';

interface Correction {
  error: string;
  original: string;
  corrected: string;
  explanation: string;
  sentence: string;
  errorPart: string;
  correctPart: string;
}

interface CorrectionResult {
  id: number;
  comment: string;
  corrections: Correction;
}

let timer: any = null;
let hasPendingRequest = false;

const input = ref('');
const isAnalyzing = ref(false);
const correctionResult = ref<CorrectionResult[]>([]);

const wordCount = computed(() => {
  const trimmed = input.value.trim();
  if (!trimmed) {
    return 0;
  }

  const isAsciiOnly = /^[\x20-\x7E]*$/.test(trimmed);
  if (isAsciiOnly) {
    return trimmed.split(/\s+/).filter(word => word.length > 0).length;
  } else {
    return trimmed.replace(/\s+/g, '').length;
  }
});

function onInput() {
  if (timer) {
    clearTimeout(timer);
  }

  timer = setTimeout(() => {
    if (isAnalyzing.value) {
      hasPendingRequest = true;
      return;
    }
    handleAIWriter();
  }, 500);
}

async function handleAIWriter() {
  if (isAnalyzing.value || input.value.trim() === '') {
    return;
  }

  isAnalyzing.value = true;
  hasPendingRequest = false;

  try {
    const resp = await AIWrite({
      content: input.value,
      corrections: correctionResult.value
    });
    resp.data.forEach((newData: CorrectionResult) => {
      const index = correctionResult.value.findIndex(oldData => oldData.id === newData.id);
      if (index !== -1) {
        correctionResult.value[index] = newData;
      } else {
        correctionResult.value.push(newData);
      }
    });
  } finally {
    isAnalyzing.value = false;
    if (hasPendingRequest) {
      await handleAIWriter();
    }
  }
}

function position(content: string, sentence: string, errorPart: string) {
  try {
    const normalizedContent = content.replace(/\n/g, ' ');
    const normalizedSentence = sentence.replace(/\n/g, ' ');
    const normalizedErrorPart = errorPart.replace(/\n/g, ' ');

    const sentenceStart = normalizedContent.indexOf(normalizedSentence);
    if (sentenceStart >= 0) {
      const errorStart = normalizedSentence.indexOf(normalizedErrorPart);

      if (errorStart >= 0) {
        const fullStart = sentenceStart + errorStart;
        const fullEnd = fullStart + errorPart.length;

        return {
          text: content.substring(fullStart, fullEnd),
          start: fullStart,
          end: fullEnd,
          found: true
        };
      }
    }
  } catch (error) {
    console.error('Error during positioning:', error);
  }

  return {
    text: errorPart,
    start: -1,
    end: -1,
    found: false
  };
}

function acceptCorrection(correction: Correction, resultIndex: number) {
  const pos = position(input.value, correction.sentence, correction.errorPart);

  if (pos.found) {
    input.value = input.value.substring(0, pos.start) + correction.correctPart + input.value.substring(pos.end);
    MlMessage.success('已采纳修改');
  } else if (input.value.includes(correction.original)) {
    input.value = input.value.replace(correction.original, correction.corrected);
    MlMessage.success('已采纳修改');
  } else if (input.value.includes(correction.errorPart)) {
    input.value = input.value.replace(correction.errorPart, correction.correctPart);
    MlMessage.success('已采纳修改');
  } else {
    MlMessage.warning('未找到对应的文本，可能已被修改');
  }

  correctionResult.value.splice(resultIndex, 1);
}

function rejectCorrection(resultIndex: number) {
  correctionResult.value.splice(resultIndex, 1);
}

function clearAll() {
  correctionResult.value = [];
}

function acceptAll() {
  const replacements: { index: number; start: number; end: number; text: string }[] = [];
  const unresolved: { index: number; correction: Correction }[] = [];

  for (let i = 0; i < correctionResult.value.length; i++) {
    const result = correctionResult.value[i]!;
    if (result.corrections) {
      const correction = result.corrections;
      const pos = position(input.value, correction.sentence, correction.errorPart);

      if (pos.found) {
        replacements.push({
          index: i,
          start: pos.start,
          end: pos.end,
          text: correction.correctPart
        });
      } else {
        unresolved.push({ index: i, correction });
      }
    }
  }

  // 按照开始位置降序排序，从后往前替换，避免前面的替换影响后面内容的索引位置
  replacements.sort((a, b) => b.start - a.start);

  let successCount = 0;

  for (const rep of replacements) {
    input.value = input.value.substring(0, rep.start) + rep.text + input.value.substring(rep.end);
    successCount++;
  }

  const successfullyRemovedIndices = new Set<number>(replacements.map(r => r.index));

  for (const unres of unresolved) {
    const correction = unres.correction;
    if (input.value.includes(correction.original)) {
      input.value = input.value.replace(correction.original, correction.corrected);
      successCount++;
      successfullyRemovedIndices.add(unres.index);
    } else if (input.value.includes(correction.errorPart)) {
      input.value = input.value.replace(correction.errorPart, correction.correctPart);
      successCount++;
      successfullyRemovedIndices.add(unres.index);
    }
  }

  // 按索引降序移除，避免影响尚未移除的项
  const indicesToRemove = Array.from(successfullyRemovedIndices).sort((a, b) => b - a);
  for (const idx of indicesToRemove) {
    correctionResult.value.splice(idx, 1);
  }

  const failCount = unresolved.length - (successfullyRemovedIndices.size - replacements.length);

  if (successCount > 0) {
    MlMessage.success(`已批量采纳 ${successCount} 处修改`);
  }
  if (failCount > 0) {
    MlMessage.warning(`${failCount} 处未找到对应的文本，可能已被修改`);
  }
}


</script>

<template>
  <div>
    <div class="md:hidden">
      <desktop-only
          message="AI 写作助手功能需要较大的屏幕空间来展示原文和批改建议，为了获得最佳体验，请使用电脑浏览器访问。"
      />
    </div>

    <div class="min-h-screen hidden md:block pt-16 bg-canvas">
      <div class="mx-auto w-full max-w-[1520px] h-[calc(100vh-4rem)] px-6 py-5">
        <div class="h-full grid grid-cols-[minmax(0,1fr)_400px] gap-4">
          <!-- 左侧写作区 -->
          <div class="min-w-0 h-full flex flex-col">
            <div class="bg-surface-card flex-1 rounded-[8px] border border-hairline flex flex-col overflow-hidden relative">
          <div class="px-6 py-4 border-b border-hairline flex justify-between items-center bg-surface-soft backdrop-blur-sm z-10">
            <h2 class="text-[18px] font-medium text-ink flex items-center gap-2.5">
              <span class="flex items-center justify-center w-8 h-8 rounded-[6px] bg-primary/10 text-primary">
                <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                      stroke-linecap="round" stroke-linejoin="round"
                      stroke-width="2"/>
                </svg>
              </span>
              AI 写作助手
            </h2>
            <div class="flex items-center gap-2 text-caption text-muted bg-canvas px-3.5 py-1.5 rounded-full border border-hairline">
              <template v-if="isAnalyzing">
                <div class="w-3.5 h-3.5 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
                <span class="font-medium text-primary">AI 正在分析...</span>
              </template>
              <template v-else>
                <div class="w-2 h-2 rounded-full bg-success relative">
                  <div class="absolute inset-0 rounded-full bg-success animate-ping opacity-75"></div>
                </div>
                <span>输入内容后 AI 将自动纠错</span>
              </template>
            </div>
          </div>
              <div class="flex-1 p-4">
                <div
                    class="h-full rounded-[6px] border-2 border-hairline focus-within:border-primary/70 transition-colors duration-200">
                  <textarea
                      v-model="input"
                      class="h-full w-full p-6 resize-none rounded-[6px] focus:outline-none text-ink text-base leading-[1.85] tracking-wide bg-canvas placeholder-muted-soft transition-all duration-300"
                      placeholder="在这里开始你的写作之旅..."
                      @input="onInput"
                  ></textarea>
                </div>
              </div>
              <div class="px-6 py-2.5 border-t border-hairline bg-surface-soft flex items-center justify-between text-caption text-muted-soft">
                <div class="flex items-center gap-4">
                  <span>字数 <span class="text-muted font-medium tabular-nums">{{ wordCount }}</span></span>
                </div>
                <span v-if="isAnalyzing" class="text-primary flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></span>
              实时纠错中
            </span>
                <span v-else-if="correctionResult.length > 0" class="text-warning">
              {{ correctionResult.length }} 条建议待处理
            </span>
              </div>
            </div>
          </div>

          <!-- 右侧智能纠错结果区 -->
          <div class="hidden md:flex h-full min-w-0 flex-col">
            <div class="bg-surface-card flex-1 rounded-[8px] border border-hairline flex flex-col overflow-hidden">
          <div class="px-6 py-4 border-b border-hairline bg-surface-soft backdrop-blur-sm flex justify-between items-center z-10">
            <h2 class="text-[18px] font-medium text-ink flex items-center gap-2.5">
              <span class="flex items-center justify-center w-8 h-8 rounded-[6px] bg-success/10 text-success">
                <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                </svg>
              </span>
              <span>智能纠错</span>
            </h2>
            <div class="flex items-center gap-2">
              <template v-if="correctionResult.length > 0">
                <span class="text-xs px-2.5 py-1 bg-primary/10 text-primary rounded-full font-medium border border-primary/10">
                  {{ correctionResult.length }} 条建议
                </span>
                <button
                    class="text-xs px-2.5 py-1 text-primary hover:text-white hover:bg-primary rounded-full transition-all cursor-pointer border border-primary/20 hover:border-primary"
                    @click="acceptAll"
                >
                  一键采纳
                </button>
                <button
                    class="text-xs px-2.5 py-1 text-muted-soft hover:text-error hover:bg-error/5 rounded-full transition-all cursor-pointer border border-transparent hover:border-error/10"
                    @click="clearAll"
                >
                  清空
                </button>
              </template>
            </div>
          </div>

          <div class="flex-1 overflow-y-auto p-5 bg-canvas relative">
            <template v-if="correctionResult.length > 0">
              <TransitionGroup
                  class="space-y-4"
                  name="list"
                  tag="div"
              >
                <div v-for="(result, resultIndex) in correctionResult" :key="result.id || resultIndex" class="w-full">
                  <template v-if="result.comment && !result.corrections">
                    <div class="bg-primary/5 rounded-[8px] p-4 border border-primary/10 relative overflow-hidden mb-4">
                      <div class="absolute -right-4 -top-4 w-20 h-20 bg-primary/10 rounded-full blur-xl"></div>
                      <p class="text-primary text-[14px] leading-relaxed font-medium flex items-start gap-2.5 relative z-10">
                        <span class="text-base leading-none shrink-0 mt-0.5">💡</span>
                        <span>{{ result.comment }}</span>
                      </p>
                    </div>
                  </template>

                  <div
                      v-if="result.corrections"
                      class="bg-surface-card rounded-[8px] border border-hairline overflow-hidden hover:border-primary/30 transition-all duration-300 group">
                    <div class="px-4 py-3 border-b border-hairline bg-surface-soft flex items-center gap-3 group-hover:bg-surface-soft/80 transition-colors">
                      <span class="flex items-center justify-center w-6 h-6 rounded-[4px] bg-primary text-white text-xs font-bold shrink-0">
                        {{ resultIndex + 1 }}
                      </span>
                      <span class="text-xs font-medium px-2.5 py-1 bg-error/5 text-error rounded-[4px] border border-error/10">
                        {{ result.corrections.error }}
                      </span>
                      <template v-if="result.comment">
                        <span class="ml-auto text-xs text-primary bg-primary/5 px-2 py-0.5 rounded-full truncate max-w-[140px]" :title="result.comment">
                          {{ result.comment }}
                        </span>
                      </template>
                    </div>

                    <div class="p-4 space-y-3">
                      <div class="flex items-stretch gap-3">
                        <div class="flex-1 flex flex-col space-y-1.5">
                          <p class="text-caption text-muted-soft font-medium flex items-center gap-1.5">
                            <span class="w-1.5 h-1.5 rounded-full bg-error"></span>
                            原文
                          </p>
                          <div class="flex-1 text-[14px] text-body bg-error/5 p-3 rounded-[4px] border border-error/10 line-through decoration-error/30">
                            {{ result.corrections.original }}
                          </div>
                        </div>

                        <div class="flex flex-col justify-center px-1 text-muted-soft">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path d="M14 5l7 7m0 0l-7 7m7-7H3" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                          </svg>
                        </div>

                        <div class="flex-1 flex flex-col space-y-1.5">
                          <p class="text-caption text-muted-soft font-medium flex items-center gap-1.5">
                            <span class="w-1.5 h-1.5 rounded-full bg-success"></span>
                            修改
                          </p>
                          <div class="flex-1 text-[14px] text-success font-medium bg-success/5 p-3 rounded-[4px] border border-success/10">
                            {{ result.corrections.corrected }}
                          </div>
                        </div>
                      </div>

                      <div class="space-y-1.5">
                        <p class="text-caption text-muted-soft font-medium flex items-center gap-1.5">
                          <span class="w-1.5 h-1.5 rounded-full bg-primary"></span>
                          说明
                        </p>
                        <p class="text-[14px] text-body leading-relaxed bg-surface-soft p-3 rounded-[4px] border border-hairline">
                          {{ result.corrections.explanation }}
                        </p>
                      </div>
                    </div>

                    <div class="px-4 py-3 bg-surface-soft border-t border-hairline flex justify-end gap-2">
                      <button
                          class="px-4 py-1.5 text-xs font-medium text-muted hover:text-ink hover:bg-canvas active:bg-surface-soft bg-canvas border border-hairline rounded-[6px] transition-all cursor-pointer"
                          @click="rejectCorrection(resultIndex)"
                      >
                        忽略
                      </button>
                      <button
                          class="px-4 py-1.5 text-xs font-medium text-on-primary bg-primary hover:bg-primary-active active:bg-primary-active rounded-[6px] transition-all cursor-pointer flex items-center gap-1.5"
                          @click="acceptCorrection(result.corrections, resultIndex)"
                      >
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path d="M5 13l4 4L19 7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                        </svg>
                        采纳
                      </button>
                    </div>
                  </div>
                </div>
              </TransitionGroup>
            </template>

            <template v-else>
              <div class="h-full flex flex-col items-center justify-center text-muted space-y-6 pb-10 absolute inset-0">
                <div class="w-20 h-20 bg-surface-soft rounded-[8px] flex items-center justify-center border border-hairline relative">
                  <div class="absolute inset-0 rounded-[8px] border border-primary/20 animate-ping opacity-20"></div>
                  <svg class="w-8 h-8 text-muted-soft" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        stroke-linecap="round" stroke-linejoin="round"
                        stroke-width="1.5"/>
                  </svg>
                </div>
                <div class="text-center space-y-2.5">
                  <p class="text-[14px] font-medium text-muted">等待输入</p>
                  <p class="text-caption text-muted-soft leading-relaxed max-w-[200px]">在左侧输入文本，AI 将自动识别并给出纠错建议</p>
                </div>
              </div>
            </template>
          </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
::-webkit-scrollbar {
  width: 5px;
  height: 5px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--color-hairline);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-primary);
}

.list-move,
.list-enter-active,
.list-leave-active {
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.list-enter-from {
  opacity: 0;
  transform: translateY(-12px) scale(0.98);
}

.list-leave-to {
  opacity: 0;
  transform: translateX(20px) scale(0.96);
}

.list-leave-active {
  position: absolute;
  width: 100%;
}
</style>
