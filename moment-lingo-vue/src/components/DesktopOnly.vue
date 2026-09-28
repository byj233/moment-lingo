<script lang="ts" setup>

import MlNavbar from '@/components/layout/MlNavbar.vue';

interface Props {
  message?: string;
}

withDefaults(defineProps<Props>(), {
  message: '为了获得最佳体验，请使用电脑浏览器访问。'
});
</script>

<template>
  <div class="min-h-screen bg-canvas flex flex-col items-center justify-center p-6 text-center">
    <ml-navbar title="Moment Lingo"/>
    <div class="w-24 h-24 bg-primary/10 rounded-full flex items-center justify-center mb-6">
      <svg class="w-12 h-12 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
            d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
            stroke-linecap="round" stroke-linejoin="round"
            stroke-width="1.5"/>
      </svg>
    </div>
    <h2 class="text-xl font-medium text-ink mb-2">请在电脑端体验</h2>
    <p class="text-muted text-sm leading-relaxed max-w-[260px]">
      {{ message }}
    </p>
  </div>
</template>
