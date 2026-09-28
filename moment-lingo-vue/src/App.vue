<script lang="ts" setup>
import { useMobileDetector } from '@/utils/mobileDetector.ts';
import { onMounted } from 'vue';
import { options } from '@/api/auth.ts';
import { useUserStore } from '@/store/userStore.ts';
import MlHeader from '@/components/layout/MlHeader.vue';
import { useTheme } from '@/composables/useTheme.ts';

const {isMobile} = useMobileDetector();
const userStore = useUserStore();

useTheme();

onMounted(async () => {
  if (userStore.isLogin()) {
    await options();
    await userStore.update();
  }
});
</script>

<template>
  <div :class="isMobile ? 'bg-gray-50' : 'bg-canvas text-ink font-sans'" class="min-h-screen">
    <ml-header/>
    <router-view v-slot="{ Component, route }">
      <transition :name="route.meta?.transition as string ?? 'fade-slide'" mode="out-in">
        <component :is="Component" :key="route.name"/>
      </transition>
    </router-view>
  </div>
</template>