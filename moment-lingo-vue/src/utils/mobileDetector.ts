import { computed, onMounted, onUnmounted, ref } from 'vue';

// 推荐解包，避免在模板中使用 computed 属性
function useMobileDetector(breakpoint = 768) {
  const screenWidth = ref(window.innerWidth);

  const handleResize = () => {
    screenWidth.value = window.innerWidth;
  };

  onMounted(() => {
    window.addEventListener('resize', handleResize);
  });

  onUnmounted(() => {
    window.removeEventListener('resize', handleResize);
  });

  // 通过计算属性实时返回判断结果
  const isMobile = computed(() => screenWidth.value < breakpoint);

  return {
    screenWidth,
    isMobile
  };
}

export {
  useMobileDetector
};
