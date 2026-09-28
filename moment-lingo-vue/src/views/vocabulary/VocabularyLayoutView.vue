<script lang="ts" setup>
import { ref, watch } from 'vue';
import { getBriefVocabulary } from '@/api/vocabulary.ts';
import { useRoute } from 'vue-router';
import Word from '@/views/vocabulary/Word.vue';
import Phrase from '@/views/vocabulary/Phrase.vue';
import Common from '@/views/vocabulary/Common.vue';
import NoDataView from '@/views/NoDataView.vue';
import MlFooter from '@/components/layout/MlFooter.vue';

const route = useRoute();
const vocabularyId = ref('');

// 1 word 2 phrase 3 common
const type = ref(0);
const isLoading = ref(true);
const isDataExist = ref(true);

async function loadData(vocId: string) {
  isLoading.value = true;
  vocabularyId.value = vocId;
  try {
    const resp = await getBriefVocabulary(vocId);
    if (resp.data.type === 'word') {
      type.value = 1;
    } else if (resp.data.type === 'phrase') {
      type.value = 2;
    } else {
      type.value = 3;
    }
  } catch (_) {
    isDataExist.value = false;
  } finally {
    isLoading.value = false;
  }
}

watch(() => route.params.vocabularyId, async (newId: any) => {
  await loadData(String(newId));
}, {immediate: true});
</script>

<template>
  <div class=" text-ink font-sans min-h-screen">
    <template v-if="isLoading">
    </template>
    <template v-else-if="type === 0">
      <no-data-view/>
      <ml-footer/>
    </template>
    <template v-else-if="type === 1">
      <word :type="type" :vocabulary-id="vocabularyId"/>
      <ml-footer/>
    </template>
    <template v-else-if="type === 2">
      <phrase :type="type" :vocabulary-id="vocabularyId"/>
      <ml-footer/>
    </template>
    <template v-else-if="type === 3">
      <common :type="type" :vocabulary-id="vocabularyId"/>
      <ml-footer/>
    </template>
  </div>
</template>
