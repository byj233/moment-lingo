import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { TypeChecker } from '@/utils/typeChecker.ts';

const useSearchHistoryStore = defineStore('searchHistoryStore', () => {
  const refHistory = ref<any[]>([]);
  // 只读版本
  const history = computed(() => refHistory.value);

  const addHistory = (item: any) => {
    if (TypeChecker.isNullOrUndefined(item)) {
      return;
    }

    const existingIndex = refHistory.value.findIndex(
      i => i.vocabularyId === item.vocabularyId
    );

    // 如果存在，先移除再添加到开头（置顶）
    if (existingIndex !== -1) {
      refHistory.value.splice(existingIndex, 1);
    }

    refHistory.value.unshift(item);
  };


  const clearHistory = () => {
    refHistory.value = [];
  };

  const removeHistory = (item: any) => {
    if (TypeChecker.isNullOrUndefined(item)) {
      return;
    }
    refHistory.value = refHistory.value.filter(i => i.vocabularyId !== item.vocabularyId);
  };

  // 响应式返回
  const getHistory = (limit: number = 0) => {
    if (TypeChecker.isNullOrUndefined(limit)) {
      return [];
    }

    return computed(() => {
      if (limit <= 0) return [];
      return refHistory.value.slice(0, limit);
    });
  };

  return {
    refHistory,
    history,
    addHistory,
    getHistory,
    clearHistory,
    removeHistory
  };
}, {
  persist: true
});

export { useSearchHistoryStore };
