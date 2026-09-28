<script lang="ts" setup>
import { ref } from 'vue';
import { version as v } from '@/config/index';

const version = ref(v);
const currentYear = new Date().getFullYear();
</script>

<template>
  <!-- web -->
  <footer
      class="hidden md:block bg-surface-card border-t border-hairline py-4 px-4 transition-all duration-300">
    <div class="max-w-6xl mx-auto">
      <div class="flex flex-col md:flex-row justify-between items-center gap-2">
        <!-- 左侧：版权信息 -->
        <div class ="flex items-center space-x-2 text-muted text-sm">
          <span class="inline-block w-2 h-2 rounded-full bg-primary"></span>
          <span>© {{ currentYear }} MomentLingo. All rights reserved.</span>
        </div>

        <!-- 右侧：版本信息和链接 -->
        <div class="flex items-center space-x-4">
          <div class="text-sm text-muted flex items-center">
            <span class="hidden sm:inline">Version</span>
            <span class="ml-2 font-mono bg-surface-soft px-2 py-1 rounded-[4px] text-xs">{{
                version
              }}</span>
          </div>
        </div>
      </div>

      <!-- 分隔线 -->
      <div
          class="mt-2 pt-4 border-t border-hairline flex flex-col md:flex-row justify-between items-center gap-2 text-xs text-muted-soft">
        <div class="flex space-x-4">
          <a class="hover:text-primary transition-colors" href="#">隐私政策</a>
          <a class="hover:text-primary transition-colors" href="#">服务条款</a>
          <a class="hover:text-primary transition-colors" href="#">联系我们</a>
        </div>

        <!-- 备案号信息 -->
        <div class="text-muted-soft">
          <a class="hover:text-primary transition-colors" href="https://beian.miit.gov.cn/" target="_blank">
            浙ICP备2025148323号-3
          </a>
        </div>
      </div>
    </div>
  </footer>
</template>