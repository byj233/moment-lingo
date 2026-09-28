<script lang="ts" setup>
import MlLoading from '@/components/MlLoading.vue';

interface Props {
  playing?: boolean;
  loading?: boolean;
}

withDefaults(defineProps<Props>(), {
  playing: false,
  loading: false
});
</script>
<template>
  <!-- web -->
  <div class="hidden md:block">
    <button
        :class="[
        {
          'bg-success animate-pulse': playing,
          'bg-primary-active': loading,
          'opacity-50': playing || loading
        },
        'btn w-8 h-8 cursor-pointer rounded-[6px] bg-primary text-white flex items-center justify-center transition-all duration-300 ease-in-out'
      ]"
        :disabled="loading"
        v-bind="$attrs"
    >
      <!-- 加载状态：旋转动画 -->
      <template v-if="loading">
        <svg class="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" fill="none" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                fill="currentColor"></path>
        </svg>
      </template>

      <!-- 播放状态：波形动画 -->
      <template v-else-if="playing">
        <div class="flex items-center justify-center gap-1 h-5 w-7">
          <span class="inline-block w-1 bg-white rounded-sm h-2/5 animate-wave1"></span>
          <span class="inline-block w-1 bg-white rounded-sm h-4/5 animate-wave2"></span>
          <span class="inline-block w-1 bg-white rounded-sm h-3/5 animate-wave3"></span>
          <span class="inline-block w-1 bg-white rounded-sm h-5/5 animate-wave4"></span>
          <span class="inline-block w-1 bg-white rounded-sm h-2/5 animate-wave5"></span>
        </div>
      </template>

      <!-- 默认状态：喇叭图标 -->
      <template v-else>
        <svg height="35" viewBox="0 0 24 24" width="35" xmlns="http://www.w3.org/2000/svg">
          <path id="cgoplay" d="M18.25 11.9998L8.5 17.6289L8.5 6.37061L18.25 11.9998Z" fill="#eee"></path>
        </svg>
      </template>
    </button>
  </div>

  <!-- h5 -->
  <div class="block md:hidden">
    <div class="w-8 h-8 cursor-pointer" v-bind="$attrs">

      <!-- 加载状态 -->
      <template v-if="loading">
        <div class="flex items-center justify-center w-full h-full">
          <ml-loading size="small" type="inline"/>
        </div>
      </template>
      <template v-else>
        <!-- 非加载状态（音频图标） -->
        <div :class="{'audio-playing': playing}"
             class="bg-[url('/icon/audio-2.png')] bg-no-repeat bg-cover transition-all w-full h-full"/>
      </template>
    </div>
  </div>
</template>

<style scoped>
/* 波形动画定义 */
@keyframes wave-animation {
  0%, 100% {
    transform: scaleY(1);
  }
  50% {
    transform: scaleY(0.3);
  }
}

.animate-wave1 {
  animation: wave-animation 1s ease-in-out infinite;
}

.animate-wave2 {
  animation: wave-animation 1s ease-in-out 0.1s infinite;
}

.animate-wave3 {
  animation: wave-animation 1s ease-in-out 0.2s infinite;
}

.animate-wave4 {
  animation: wave-animation 1s ease-in-out 0.3s infinite;
}

.animate-wave5 {
  animation: wave-animation 1s ease-in-out 0.4s infinite;
}

/* 播放中脉冲动画 */
@keyframes pulse-coral {
  0% {
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(16, 185, 129, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
  }
}

.animate-pulse {
  animation: pulse 1.5s infinite;
}

/* 加载旋转动画 */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}


@keyframes audioPulse {
  from {
    background-image: url('/icon/audio-1.png');
  }
  to {
    background-image: url('/icon/audio-2.png');
  }
}

.audio-playing {
  animation: audioPulse 1.2s infinite;
}
</style>