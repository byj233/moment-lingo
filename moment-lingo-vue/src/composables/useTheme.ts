import { useThemeStore } from '@/store/themeStore';
import { onMounted, computed } from 'vue';

export function useTheme() {
  const themeStore = useThemeStore();

  const applyTheme = () => {
    const root = document.documentElement;
    const colors = themeStore.currentPreset.colors;

    Object.entries(colors).forEach(([key, value]) => {
      root.style.setProperty(key, value);
    });
  };

  const switchTheme = (name: string) => {
    themeStore.setTheme(name);
    applyTheme();
  };

  onMounted(() => {
    applyTheme();
  });

  return {
    activeTheme: computed(() => themeStore.activeTheme),
    currentPreset: computed(() => themeStore.currentPreset),
    switchTheme,
    applyTheme,
  };
}
