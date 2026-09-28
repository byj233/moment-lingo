<script lang="ts" setup>
import { onMounted, ref } from 'vue';
import ScrollReveal from 'scrollreveal';
import MlFooter from '@/components/layout/MlFooter.vue';

const stats = ref([
  { value: 100, target: 100000, label: '活跃用户' },
  { value: 100, target: 500000, label: '学习会话' },
  { value: 100, target: 98, label: '用户满意度', suffix: '%' },
  { value: 100, target: 20, label: '支持语言', suffix: '+' }
]);


const techHighlights = [
  {
    title: '个人知识-大模型双引擎',
    description: '大语言模型驱动个人知识库动态进化，通过Prompt Tuning实现私人化知识适配与精准调用',
    icon: '🔄'
  },
  {
    title: '情境感知智能体',
    description: '结合个人知识图谱与实时场景数据，驱动智能体自主规划任务，调用大模型生成个性化行动方案',
    icon: '🤖'
  },
  {
    title: '知识边界拓展系统',
    description: '智能体联动大模型，以个人知识库为锚点，从海量数据中挖掘关联知识并验证整合',
    icon: '🌐'
  },
  {
    title: '闭环学习进化机制',
    description: '大模型处理交互反馈，智能体优化知识更新策略，形成个人知识与海量数据的动态平衡闭环',
    icon: '♻️'
  }
];


onMounted(() => {
  const revealOptions = {
    origin: 'bottom',
    distance: '50px',
    duration: 800,
    easing: 'ease-out',
    reset: false,
    threshold: 0.4, // 元素露出多少比例时触发动画 百分比
    viewOffset: {
      top: 0,
      bottom: 130
    }
  };

  const sr = ScrollReveal();
  // 获取所有需要动画的元素
  const elements = document.querySelectorAll('.animate-on-scroll');

  elements.forEach((ele: any) => {
    // 从 data-delay 读取数值，默认 0
    const delay = Number(ele.getAttribute('data-delay') ?? 0);
    // 为每个元素单独配置延迟并应用动画
    sr.reveal(ele, {
      ...revealOptions,
      delay
    });
  });
});
</script>

<template>
  <div>
    <div class="min-h-screen">
      <!-- Hero 区域 -->
      <section class="relative min-h-screen flex items-center justify-center overflow-hidden">
        <div
            class="absolute top-10 md:top-20 left-2 md:left-10 w-40 h-40 md:w-72 md:h-72 bg-primary/15 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
        <div
            class="absolute top-24 md:top-40 right-2 md:right-10 w-36 h-36 md:w-72 md:h-72 bg-accent-amber/20 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
        <div
            class="absolute bottom-10 md:bottom-20 left-1/2 transform -translate-x-1/2 w-32 h-32 md:w-72 md:h-72 bg-accent-teal/15 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>

        <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-20 text-center">
          <h1 class="text-4xl md:text-[64px] font-display font-normal text-ink mb-6 space-y-3 leading-[1.05] tracking-[-1.5px]">
            <span class="text-primary">智能化英语学习</span>
            <br>
            <span>随时随地</span>
          </h1>
          <p class="text-xl text-muted mb-8 max-w-3xl mx-auto leading-relaxed">
            通过AI驱动的词汇管理、智能搜索和作文批改功能，让语言学习变得更加高效和有趣
          </p>
          <router-link to="/auth">
            <span class="inline-block px-8 py-3 text-button font-medium text-on-primary bg-primary rounded-[8px] hover:bg-primary-active transition-colors duration-300 cursor-pointer">
              免费注册
            </span>
          </router-link>
        </div>
      </section>

      <!-- 统计数据 -->
      <section class="py-16 bg-surface-card">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div class="animate-on-scroll" data-delay="100">
              <div class="text-4xl md:text-5xl font-display font-normal text-primary mb-2">
                {{ stats[0]?.value }}
              </div>
              <div class="text-muted text-caption">
                {{ stats[0]?.label }}
              </div>
            </div>
            <div class="animate-on-scroll" data-delay="200">
              <div class="text-4xl md:text-5xl font-display font-normal text-primary mb-2">
                {{ stats[1]?.value }}
              </div>
              <div class="text-muted text-caption">
                {{ stats[1]?.label }}
              </div>
            </div>
            <div class="animate-on-scroll" data-delay="300">
              <div class="text-4xl md:text-5xl font-display font-normal text-primary mb-2">
                {{ stats[2]?.value }}{{ stats[2]?.suffix }}
              </div>
              <div class="text-muted text-caption">
                {{ stats[2]?.label }}
              </div>
            </div>
            <div class="animate-on-scroll" data-delay="400">
              <div class="text-4xl md:text-5xl font-display font-normal text-primary mb-2">
                {{ stats[3]?.value }}{{ stats[3]?.suffix }}
              </div>
              <div class="text-muted text-caption">
                {{ stats[3]?.label }}
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 功能特性 -->
      <section class="py-20 min-h-screen bg-canvas">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="text-center mb-16 animate-on-scroll">
            <h2 class="text-3xl md:text-[48px] font-display font-normal text-ink mb-4 leading-[1.1] tracking-[-1px]">
              强大的<span class="text-primary">AI功能</span>
            </h2>
            <p class="max-w-2xl mx-auto text-xl text-muted">
              我们的AI技术让语言学习变得更加智能、高效和个性化
            </p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <router-link to="/ai-call">
              <div
                  class="group bg-surface-card rounded-[12px] p-8 shadow-sm hover:shadow-md transition-all duration-500 ease-in-out hover:-translate-y-2 border border-hairline animate-on-scroll"
                  data-delay="100">
                <div
                    class="w-16 h-16 bg-surface-soft rounded-[8px] flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-500 ease-in-out">
                  <div class="text-3xl">🎙️</div>
                </div>
                <h3 class="text-xl font-medium text-ink mb-3">AI口语陪练</h3>
                <p class="text-body text-[14px] mb-4 leading-[1.55]">
                  提供真实语境模拟，实时语音交互，纠正发音与语法，助你流利说英语。
                </p>
                <div
                    class="flex items-center text-primary font-medium group-hover:text-primary-active transition-colors duration-300">
                  <span>了解更多</span>
                  <svg class="ml-2 h-5 w-5 transform group-hover:translate-x-1 transition-transform duration-300"
                       fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M17 8l4 4m0 0l-4 4m4-4H3" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                  </svg>
                </div>
              </div>
            </router-link>

            <router-link to="/search">
              <div
                  class="group bg-surface-card rounded-[12px] p-8 shadow-sm hover:shadow-md transition-all duration-500 ease-in-out hover:-translate-y-2 border border-hairline animate-on-scroll"
                  data-delay="300">
                <div
                    class="w-16 h-16 bg-surface-soft rounded-[8px] flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-500 ease-in-out">
                  <div class="text-3xl">🔍</div>
                </div>
                <h3 class="text-xl font-medium text-ink mb-3">AI搜索翻译</h3>
                <p class="text-body text-[14px] mb-4 leading-[1.55]">
                  强大的AI翻译引擎，支持多种语言互译，理解上下文语境，提供精准的翻译结果和专业术语解释。
                </p>
                <div
                    class="flex items-center text-primary font-medium group-hover:text-primary-active transition-colors duration-300">
                  <span>了解更多</span>
                  <svg class="ml-2 h-5 w-5 transform group-hover:translate-x-1 transition-transform duration-300"
                       fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M17 8l4 4m0 0l-4 4m4-4H3" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                  </svg>
                </div>
              </div>
            </router-link>

            <router-link to="/essay">
              <div
                  class="group bg-surface-card rounded-[12px] p-8 shadow-sm hover:shadow-md transition-all duration-500 ease-in-out hover:-translate-y-2 border border-hairline animate-on-scroll"
                  data-delay="500">
                <div
                    class="w-16 h-16 bg-surface-soft rounded-[8px] flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-500 ease-in-out">
                  <div class="text-3xl">📝</div>
                </div>
                <h3 class="text-xl font-medium text-ink mb-3">智能作文批改</h3>
                <p class="text-body text-[14px] mb-4 leading-[1.55]">
                  AI驱动的写作助手，实时检测语法错误、拼写错误，提供风格建议和优化方案，提升写作质量。
                </p>
                <div
                    class="flex items-center text-primary font-medium group-hover:text-primary-active transition-colors duration-300">
                  <span>了解更多</span>
                  <svg class="ml-2 h-5 w-5 transform group-hover:translate-x-1 transition-transform duration-300"
                       fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M17 8l4 4m0 0l-4 4m4-4H3" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                  </svg>
                </div>
              </div>
            </router-link>
          </div>
        </div>
      </section>


      <!-- AI技术亮点 -->
      <section class="py-20 bg-surface-card">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="text-center mb-16 animate-on-scroll">
            <h2 class="text-3xl md:text-[48px] font-display font-normal text-ink mb-4 leading-[1.1] tracking-[-1px]">
              先进的<span class="text-primary">AI技术</span>
            </h2>
            <p class="max-w-2xl mx-auto text-xl text-muted">
              我们采用业界领先的人工智能技术，为您提供卓越的语言学习体验
            </p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div v-for="(highlight, index) in techHighlights" :key="index"
                 :data-delay="(index + 1) * 100"
                 class="bg-canvas rounded-[12px] p-6 border border-hairline shadow-sm hover:shadow-md transition-all duration-500 ease-in-out animate-on-scroll hover:-translate-y-1">
              <div class="text-4xl mb-4">{{ highlight.icon }}</div>
              <h3 class="text-lg font-medium text-ink mb-2">{{ highlight.title }}</h3>
              <p class="text-body text-[14px] leading-[1.55]">{{ highlight.description }}</p>
            </div>
          </div>

          <!-- 技术架构图 -->
          <div class="mt-20 relative animate-on-scroll">
            <div
                class="absolute inset-0 bg-primary/5 rounded-[12px] transform -rotate-1 scale-105"></div>
            <div class="relative bg-surface-card p-8 md:p-12 rounded-[12px] border border-hairline shadow-sm">
              <h3 class="text-2xl font-display font-normal text-center text-ink mb-8">AI学习引擎架构</h3>
              <div class="flex flex-col md:flex-row items-center justify-around gap-8">
                <div
                    class="w-full md:w-1/4 bg-canvas p-6 rounded-[8px] text-center border border-hairline shadow-sm transition-all duration-500 ease-in-out">
                  <h4 class="font-medium text-ink mb-2">数据采集层</h4>
                  <p class="text-body text-[13px]">收集用户学习行为和进度数据</p>
                </div>
                <div class="hidden md:block text-muted-soft">
                  <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M14 5l7 7m0 0l-7 7m7-7H3" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                  </svg>
                </div>
                <div
                    class="w-full md:w-1/4 bg-canvas p-6 rounded-[8px] text-center border border-hairline shadow-sm transition-all duration-500 ease-in-out">
                  <h4 class="font-medium text-ink mb-2">分析处理层</h4>
                  <p class="text-body text-[13px]">AI算法分析用户数据和学习模式</p>
                </div>
                <div class="hidden md:block text-muted-soft">
                  <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M14 5l7 7m0 0l-7 7m7-7H3" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                  </svg>
                </div>
                <div
                    class="w-full md:w-1/4 bg-canvas p-6 rounded-[8px] text-center border border-hairline shadow-sm transition-all duration-500 ease-in-out">
                  <h4 class="font-medium text-ink mb-2">个性化推荐层</h4>
                  <p class="text-body text-[13px]">生成个性化学习路径和内容</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA 区域 -->
      <section class="py-12 md:py-20 bg-surface-dark">
        <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center animate-on-scroll">
          <h2 class="text-3xl md:text-[48px] font-display font-normal text-on-dark mb-6 leading-[1.1] tracking-[-1px]">
            开始您的AI语言学习之旅
          </h2>
          <p class="text-xl text-on-dark-soft mb-8">
            加入成千上万已经通过Moment Lingo提升语言能力的用户
          </p>
          <div class="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            <router-link to="/auth">
              <div
                  class="px-8 py-3 text-button font-medium text-on-primary bg-primary rounded-[8px] hover:bg-primary-active transition-colors duration-300 inline-block cursor-pointer">
                免费注册
              </div>
            </router-link>
          </div>
        </div>
      </section>
    </div>
    <ml-footer/>
  </div>
</template>
