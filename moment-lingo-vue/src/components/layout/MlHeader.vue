<script lang="ts" setup>
import { useUserStore } from '@/store/userStore.ts';
import { onMounted, onUnmounted, ref, useTemplateRef } from 'vue';
import { useMobileDetector } from '@/utils/mobileDetector.ts';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const { isMobile } = useMobileDetector();
const userStore = useUserStore();
const userInfo = userStore.userInfo;

const navItems = [
  { name: '首页', path: '/' },
  { name: '搜索', path: '/search' },
  { name: '词书', path: '/book' },
  { name: '作文批改', path: '/essay' },
  { name: '口语陪练', path: '/ai-call' },
  { name: 'AI写作', path: '/ai-write' }
];


const header = useTemplateRef('header');
let lastScrollPosition = 0;
let isHeaderVisible = false;
const isMobileMenuOpen = ref(false);

function onLogout() {
  userStore.clear();
}

function handleScroll() {
  if (isMobile.value) {
    return;
  }
  const currentScrollPosition = window.pageYOffset ?? document.documentElement.scrollTop;
  isHeaderVisible = currentScrollPosition <= lastScrollPosition;
  lastScrollPosition = currentScrollPosition;
  header.value!.style.transform = isHeaderVisible ? 'translateY(0)' : 'translateY(-100%)';
}

onMounted(() => {
  if (isMobile.value) {
    return;
  }
  window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
  if (isMobile.value) {
    return;
  }
  window.removeEventListener('scroll', handleScroll);
});
</script>

<template>
  <header ref="header"
          :class="[isMobile && route.path === '/' ? 'block':isMobile ? 'hidden':'block',isMobileMenuOpen?'backdrop-blur-none bg-surface-card':'backdrop-blur-sm bg-canvas/85']"
          class="transition-all duration-300 fixed top-0 left-0 w-full z-50 border-b border-hairline"
  >
    <div class="flex px-4 sm:px-8 lg:px-16 items-center justify-between h-14 md:h-16">
      <div class="flex items-center">
        <router-link class="flex items-center space-x-2" to="/">
          <div>
            <img alt="logo" class="w-7 h-7 sm:w-8 sm:h-8 md:w-10 md:h-10 hover:scale-110 hover:rotate-4 duration-300"
                 src="/logo.webp">
          </div>
          <span
              class="text-base sm:text-lg md:text-xl font-display font-normal text-primary">
              MomentLingo
            </span>
        </router-link>
      </div>

      <nav class="hidden md:flex space-x-8">
        <template v-for="item in navItems">
          <router-link
              :to="item.path"
              active-class="text-primary"
              class="text-muted hover:text-primary font-medium transition-all duration-200 relative group"
          >
            {{ item.name }}
            <span
                class="absolute bottom-[-4px] left-0 w-0 h-0.5 bg-primary transition-all duration-300 group-hover:w-full"></span>
          </router-link>
        </template>
      </nav>

      <div class="hidden md:flex items-center space-x-4">
        <template v-if="userStore.isLogin()">
          <div class="relative">
            <button
                class="flex items-center space-x-2 text-body hover:text-primary transition-colors duration-200 cursor-pointer"
                @click="router.push('/user')">
              <img
                  :alt="userStore.userInfo?.nickname"
                  :src="userStore.userInfo?.avatarUrl"
                  class="w-9 h-9 rounded-full object-cover border-2 border-hairline hover:border-primary transition-colors duration-200"
              />
              <span class="font-medium">{{ userStore.userInfo?.nickname }}</span>
            </button>
          </div>
          <button
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-[8px] text-on-primary bg-primary hover:bg-primary-active focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition duration-300 cursor-pointer"
              @click="onLogout">
            退出
          </button>
        </template>
        <template v-else>
          <button
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-[8px] text-on-primary bg-primary hover:bg-primary-active focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition duration-300 cursor-pointer"
              @click="router.push('/auth/login')">
            登录
          </button>
        </template>
      </div>

      <button
          class="md:hidden inline-flex items-center justify-center w-10 h-10 rounded-full text-body hover:text-primary hover:bg-surface-soft focus:outline-none transition-all duration-200 active:scale-95"
          @click="isMobileMenuOpen = !isMobileMenuOpen">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path d="M4 6h16M4 12h16M4 18h16" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
        </svg>
      </button>
    </div>

    <transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
    >
      <template v-if="isMobileMenuOpen">
        <div class="md:hidden border-t border-hairline bg-surface-card">
          <div class="px-4 py-4 space-y-1">
            <template v-for="item in navItems">
              <router-link
                  :to="item.path"
                  class="block px-3 py-3 rounded-[8px] text-body hover:bg-surface-soft hover:text-primary font-medium transition-all duration-200 active:scale-[0.98]"
                  @click="isMobileMenuOpen = false">
                {{ item.name }}
              </router-link>
            </template>
            <div class="pt-3 mt-3 border-t border-hairline">
              <template v-if="userStore.isLogin()">
                <div class="flex items-center justify-between px-3 py-3" @click="router.push('/user')">
                  <div class="flex items-center space-x-3">
                    <img
                        :alt="userInfo?.nickname"
                        :src="userInfo?.avatarUrl"
                        class="w-10 h-10 rounded-full object-cover border-2 border-hairline"
                    />
                    <span class="text-body font-medium">{{ userStore.userInfo?.nickname }}</span>
                  </div>
                  <button
                      class="px-4 py-2 rounded-[8px] text-on-primary bg-primary font-medium active:scale-[0.98] transition-all duration-200"
                      @click="onLogout">退出
                  </button>
                </div>
              </template>
              <template v-else>
                <button
                    class="w-full block text-center px-4 py-3 rounded-[8px] text-on-primary bg-primary font-medium active:scale-[0.98] transition-all duration-200 cursor-pointer"
                    @click="() => { isMobileMenuOpen = false; router.push('/auth/login'); }">登录
                </button>
              </template>
            </div>
          </div>
        </div>
      </template>
    </transition>
  </header>
</template>