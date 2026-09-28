<script lang="ts" setup>
import { computed } from 'vue';

interface Props {
  type?: 'fullscreen' | 'inline';
  size?: 'small' | 'medium' | 'large';
  text?: string;
  showText?: boolean;
  overlay?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  type: 'fullscreen',
  size: 'medium',
  text: '',
  showText: false,
  overlay: true
});

// 计算属性
const sizeClasses = computed(() => {
  const sizeMap = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  };
  return sizeMap[props.size];
});

const iconSizeClasses = computed(() => {
  const sizeMap = {
    small: 'w-4 h-4',
    medium: 'w-6 h-6',
    large: 'w-8 h-8'
  };
  return sizeMap[props.size];
});
</script>

<template>
  <!-- 全屏加载 -->
  <template v-if="type === 'fullscreen'">
    <div
        :class="overlay ? 'bg-canvas/95' : 'bg-canvas/40'"
        class="fixed inset-0 z-50 flex items-center justify-center backdrop-blur-sm">
      <div class="flex flex-col items-center space-y-6">
        <!-- 语言学习主题动画：文字图标旋转 -->
        <div class="relative">
          <div class="animate-spin-slow w-16 h-16 rounded-full bg-primary p-1">
            <div class="w-full h-full rounded-full bg-canvas flex items-center justify-center">
              <svg class="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                    d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                    stroke-linecap="round" stroke-linejoin="round"
                    stroke-width="2"/>
              </svg>
            </div>
          </div>
          <!-- 装饰性小圆点 -->
          <div class="absolute -top-2 -right-2 w-4 h-4 bg-accent-amber rounded-full animate-bounce"></div>
          <div class="absolute -bottom-2 -left-2 w-3 h-3 bg-accent-teal rounded-full animate-bounce delay-300"></div>
        </div>

        <!-- 加载文字 -->
        <template v-if="showText">
          <div class="text-center space-y-2">
            <p class="text-lg font-medium text-ink">
              {{ text }}
            </p>
            <div class="flex space-x-1 justify-center">
              <div class="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
              <div class="w-2 h-2 bg-accent-amber rounded-full animate-bounce delay-100"></div>
              <div class="w-2 h-2 bg-accent-teal rounded-full animate-bounce delay-200"></div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </template>

  <!-- 内联加载 -->
  <template v-else>
    <div class="flex items-center justify-center space-x-3">
      <div :class="sizeClasses" class="relative">
        <!-- 旋转加载图标 -->
        <svg :class="iconSizeClasses" class="animate-spin text-primary" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                fill="currentColor"></path>
        </svg>
      </div>
      <template v-if="showText">
        <span class="text-muted font-medium">{{ text }}</span>
      </template>
    </div>
  </template>
</template>

<style scoped>
/* 自定义动画 */
@keyframes spin-slow {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin-slow {
  animation: spin-slow 3s linear infinite;
}

@keyframes bounce {
  0%, 20%, 53%, 80%, 100% {
    animation-timing-function: cubic-bezier(0.215, 0.61, 0.355, 1);
    transform: translate3d(0, 0, 0);
  }
  40%, 43% {
    animation-timing-function: cubic-bezier(0.755, 0.05, 0.855, 0.06);
    transform: translate3d(0, -8px, 0);
  }
  70% {
    animation-timing-function: cubic-bezier(0.755, 0.05, 0.855, 0.06);
    transform: translate3d(0, -4px, 0);
  }
  90% {
    transform: translate3d(0, -2px, 0);
  }
}

.delay-100 {
  animation-delay: 100ms;
}

.delay-200 {
  animation-delay: 200ms;
}

.delay-300 {
  animation-delay: 300ms;
}
</style>
