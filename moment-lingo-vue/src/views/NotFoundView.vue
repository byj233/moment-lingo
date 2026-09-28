<script lang="ts" setup>
import { useRouter } from 'vue-router';
import { onMounted } from 'vue';

const router = useRouter();

onMounted(() => {
  // 添加一些简单的动画效果
  const blobElements = document.querySelectorAll('.animate-blob');
  blobElements.forEach((el, index) => {
    el.classList.add(`animation-delay-${index * 2000}`);
  });
});
</script>

<template>
  <div class="bg-canvas min-h-screen flex items-center justify-center overflow-hidden">
    <!-- 背景装饰元素 -->
    <div class="absolute inset-0 overflow-hidden">
      <div
          class="absolute top-0 left-0 w-48 h-48 sm:w-56 sm:h-56 md:w-72 md:h-72 bg-primary/15 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob"></div>
      <div
          class="absolute top-0 right-0 w-48 h-48 sm:w-56 sm:h-56 md:w-72 md:h-72 bg-accent-amber/20 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-2000"></div>
      <div
          class="absolute bottom-0 left-1/2 w-48 h-48 sm:w-56 sm:h-56 md:w-72 md:h-72 bg-accent-teal/15 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-4000"></div>
    </div>

    <div class="container px-4 sm:px-6 py-8 sm:py-12 mx-auto lg:flex lg:items-center lg:gap-12 relative z-10 max-w-full">
      <div class="lg:w-1/2 mt-8 sm:mt-12 lg:mt-0">
        <p class="text-sm font-medium text-primary">404 Not Found</p>
        <h1 class="mt-3 text-2xl sm:text-3xl font-display font-normal text-ink md:text-4xl">
          诶呀！你来到了知识的荒原 🌵
        </h1>
        <p class="mt-4 text-muted text-base sm:text-lg">
          这个页面似乎并不存在，就像在语言学习中遇到的陌生词汇一样，我们可以选择绕过去或者探索新的路径。
        </p>

        <div class="flex flex-col sm:flex-row items-center mt-6 sm:mt-8 gap-3 sm:gap-4">
          <button
              class="flex items-center justify-center w-full sm:w-auto px-4 sm:px-6 py-2.5 sm:py-3 text-sm sm:text-base font-medium text-body transition-all duration-300 bg-surface-card border border-hairline rounded-[8px] gap-x-2 hover:bg-surface-soft shadow-sm hover:shadow-md cursor-pointer"
              @click="router.back()">
            <svg class="w-4 h-4 sm:w-5 sm:h-5 rtl:rotate-180" fill="none" stroke="currentColor" stroke-width="1.5"
                 viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M6.75 15.75L3 12m0 0l3.75-3.75M3 12h18" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>返回上一页</span>
          </button>

          <button
              class="w-full sm:w-auto px-4 sm:px-6 py-2.5 sm:py-3 text-sm sm:text-base font-medium tracking-wide text-on-primary transition-all duration-300 bg-primary rounded-[8px] shrink-0 hover:bg-primary-active shadow-md hover:shadow-lg transform hover:-translate-y-0.5 cursor-pointer"
              @click="router.push('/')">
            回到首页
          </button>
        </div>
      </div>

      <div class="relative w-full lg:w-1/2 lg:mt-0 mt-8 sm:mt-12 flex justify-center">
        <div class="relative w-full flex justify-center">
          <!-- 装饰性SVG -->
          <svg class="opacity-80 w-full max-w-xs sm:max-w-sm md:max-w-md lg:max-w-lg h-auto" fill="none" viewBox="0 0 514 164"
               xmlns="http://www.w3.org/2000/svg">
            <circle cx="101" cy="22" r="20" stroke="var(--color-primary)" stroke-width="2"/>
            <circle cx="101" cy="142" r="20" stroke="var(--color-primary)" stroke-width="2"/>
            <circle cx="21" cy="102" r="20" stroke="var(--color-primary)" stroke-width="2"/>
            <circle cx="141" cy="102" r="20" stroke="var(--color-primary)" stroke-width="2"/>
            <circle cx="193" cy="82" r="20" stroke="var(--color-primary)" stroke-width="2"/>
            <circle cx="313" cy="82" r="20" stroke="var(--color-primary)" stroke-width="2"/>
            <circle cx="253" cy="22" r="20" stroke="var(--color-primary)" stroke-width="2"/>
            <circle cx="253" cy="142" r="20" stroke="var(--color-primary)" stroke-width="2"/>
            <path
                d="M1 102C1 90.9543 9.9543 82 21 82H141C152.046 82 161 90.9543 161 102C161 113.046 152.046 122 141 122H21C9.9543 122 1 113.046 1 102Z"
                stroke="var(--color-primary)" stroke-width="2"/>
            <path
                d="M101 162C89.9543 162 81 153.046 81 142L81 22C81 10.9543 89.9543 2 101 2C112.046 2 121 10.9543 121 22L121 142C121 153.046 112.046 162 101 162Z"
                stroke="var(--color-primary)" stroke-width="2"/>
            <path
                d="M7.14214 115.995C-0.668351 108.184 -0.668351 95.5211 7.14214 87.7106L86.7107 8.1421C94.5212 0.331614 107.184 0.331607 114.995 8.14209C122.805 15.9526 122.805 28.6159 114.995 36.4264L35.4264 115.995C27.6159 123.805 14.9526 123.805 7.14214 115.995Z"
                stroke="var(--color-primary)" stroke-width="2"/>
            <circle cx="453" cy="22" r="20" stroke="var(--color-primary)" stroke-width="2"/>
            <circle cx="453" cy="142" r="20" stroke="var(--color-primary)" stroke-width="2"/>
            <circle cx="373" cy="102" r="20" stroke="var(--color-primary)" stroke-width="2"/>
            <circle cx="493" cy="102" r="20" stroke="var(--color-primary)" stroke-width="2"/>
            <path
                d="M353 102C353 90.9543 361.954 82 373 82H493C504.046 82 513 90.9543 513 102C513 113.046 504.046 122 493 122H373C361.954 122 353 113.046 353 102Z"
                stroke="var(--color-primary)" stroke-width="2"/>
            <path
                d="M453 162C441.954 162 433 153.046 433 142L433 22C433 10.9543 441.954 2 453 2C464.046 2 473 10.9543 473 22L473 142C473 153.046 464.046 162 453 162Z"
                stroke="var(--color-primary)" stroke-width="2"/>
            <path
                d="M359.142 115.995C351.332 108.184 351.332 95.5211 359.142 87.7106L438.711 8.1421C446.521 0.331614 459.184 0.331607 466.995 8.14209C474.805 15.9526 474.805 28.6159 466.995 36.4264L387.426 115.995C379.616 123.805 366.953 123.805 359.142 115.995Z"
                stroke="var(--color-primary)" stroke-width="2"/>
            <circle cx="253" cy="82" r="80" stroke="var(--color-primary)" stroke-width="2"/>
            <circle cx="253" cy="82" r="40" stroke="var(--color-primary)" stroke-width="2"/>
            <line stroke="var(--color-primary)" stroke-width="2" x1="8.74228e-08" x2="513" y1="1" y2="1.00004"/>
            <line stroke="var(--color-primary)" stroke-width="2" x1="-8.74228e-08" x2="513" y1="163" y2="163"/>
          </svg>

          <!-- 装饰性emoji -->
          <div class="absolute -top-4 -left-4 sm:-top-6 sm:-left-6 text-2xl sm:text-3xl md:text-4xl animate-bounce animation-delay-1000">🤔</div>
          <div class="absolute -bottom-4 -right-4 sm:-bottom-6 sm:-right-6 text-2xl sm:text-3xl md:text-4xl animate-bounce animation-delay-2000">🧭</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes blob {
  0% {
    transform: translate(0px, 0px) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
  100% {
    transform: translate(0px, 0px) scale(1);
  }
}

.animate-blob {
  animation: blob 7s infinite;
}

.animation-delay-1000 {
  animation-delay: 1s;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-3000 {
  animation-delay: 3s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}

.rtl\:rotate-180:where([dir="rtl"], [dir="rtl"] *) {
  --tw-rotate: 180deg;
}
</style>