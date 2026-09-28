<template>
  <div class="min-h-screen bg-gray-950 text-white overflow-x-hidden selection:bg-cyan-500/30 font-sans">
    <!-- 固定的炫酷背景光晕 (全屏背景动画) -->
    <div class="fixed top-[-10%] left-[-10%] w-96 h-96 bg-purple-600 rounded-full mix-blend-screen filter blur-[120px] opacity-30 animate-blob pointer-events-none"></div>
    <div class="fixed top-[30%] right-[-10%] w-96 h-96 bg-cyan-600 rounded-full mix-blend-screen filter blur-[120px] opacity-30 animate-blob animation-delay-2000 pointer-events-none"></div>
    <div class="fixed bottom-[-10%] left-[20%] w-96 h-96 bg-blue-600 rounded-full mix-blend-screen filter blur-[120px] opacity-30 animate-blob animation-delay-4000 pointer-events-none"></div>

    <!-- 顶部导航头 -->
    <header class="relative z-50 flex justify-between items-center py-6 px-6 md:px-12 max-w-7xl mx-auto animate-fade-in-down">
      <div class="text-3xl font-black tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-500">
        LINGO
      </div>
      <router-link to="/auth" class="px-6 py-2.5 rounded-full bg-white/5 backdrop-blur-md border border-white/10 hover:bg-white/10 transition-all font-medium text-sm md:text-base">
        登录 / 注册
      </router-link>
    </header>

    <main class="relative z-10 flex flex-col items-center w-full">
      <!-- 1. Hero 核心标语区域 -->
      <section class="w-full max-w-7xl mx-auto px-6 py-20 md:py-32 flex flex-col items-center text-center">
        <h1 class="text-5xl md:text-7xl lg:text-8xl font-extrabold leading-tight tracking-tight mb-6">
          <span class="block text-white mb-2">智能化英语学习</span>
          <span class="block text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-cyan-400 to-blue-500 animate-gradient-x pb-2">
            随时随地
          </span>
        </h1>
        <p class="text-gray-400 text-lg md:text-2xl max-w-3xl mb-12 leading-relaxed">
          通过AI驱动的词汇管理、智能搜索和作文批改功能，让语言学习变得更加高效和有趣。
        </p>
        <div class="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
          <router-link to="/auth" class="group relative px-8 py-4 bg-white text-gray-900 rounded-full font-bold text-lg overflow-hidden shadow-[0_0_20px_rgba(34,211,238,0.3)] hover:shadow-[0_0_40px_rgba(34,211,238,0.5)] transition-all">
            <div class="absolute inset-0 w-full h-full bg-gradient-to-r from-cyan-300 via-purple-300 to-pink-300 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <span class="relative z-10 group-hover:text-gray-900">免费开始学习</span>
          </router-link>
          <a href="#features" class="px-8 py-4 rounded-full bg-white/5 border border-white/10 hover:bg-white/10 transition-all text-lg font-medium backdrop-blur-sm text-white">
            了解更多功能
          </a>
        </div>
      </section>

      <!-- 2. 统计数据 -->
      <section class="w-full max-w-7xl mx-auto px-6 py-12">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div v-for="(stat, index) in stats" :key="index" class="animate-on-scroll p-6 rounded-3xl bg-gray-900/50 border border-gray-800 backdrop-blur-lg hover:border-gray-700 transition-colors" :data-delay="index * 100">
            <div class="text-4xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-500 mb-2">
              {{ stat.target }}{{ stat.suffix }}
            </div>
            <div class="text-gray-400 font-medium text-sm md:text-base">
              {{ stat.label }}
            </div>
          </div>
        </div>
      </section>

      <!-- 3. AI 功能特性 (响应式卡片) -->
      <section id="features" class="w-full max-w-7xl mx-auto px-6 py-24">
        <div class="text-center mb-16 animate-on-scroll">
          <h2 class="text-4xl md:text-5xl font-bold mb-4">
            强大的 <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-500">AI功能</span>
          </h2>
          <p class="text-gray-400 text-lg md:text-xl max-w-2xl mx-auto">我们的AI技术让语言学习变得更加智能、高效和个性化</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <!-- 功能卡片 1 -->
          <router-link to="/ai-call" class="group animate-on-scroll block h-full" data-delay="100">
            <div class="h-full relative p-[1px] rounded-3xl bg-gradient-to-b from-white/10 to-transparent hover:from-cyan-500/50 hover:to-purple-500/50 transition-all duration-500">
              <div class="absolute inset-0 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-3xl blur-xl opacity-0 group-hover:opacity-20 transition duration-500"></div>
              <div class="relative h-full bg-gray-900/90 backdrop-blur-xl p-8 rounded-3xl flex flex-col">
                <div class="w-16 h-16 bg-cyan-500/10 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 group-hover:bg-cyan-500/20 transition-all duration-300 text-3xl">
                  🎙️
                </div>
                <h3 class="text-2xl font-bold text-white mb-3">AI口语陪练</h3>
                <p class="text-gray-400 mb-8 flex-1 leading-relaxed">提供真实语境模拟，实时语音交互，纠正发音与语法，助你流利说英语。</p>
                <div class="flex items-center text-cyan-400 font-medium mt-auto group-hover:text-cyan-300">
                  <span>开始对话</span>
                  <svg class="ml-2 h-5 w-5 transform group-hover:translate-x-2 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
                </div>
              </div>
            </div>
          </router-link>

          <!-- 功能卡片 2 -->
          <router-link to="/search" class="group animate-on-scroll block h-full" data-delay="200">
            <div class="h-full relative p-[1px] rounded-3xl bg-gradient-to-b from-white/10 to-transparent hover:from-purple-500/50 hover:to-pink-500/50 transition-all duration-500">
              <div class="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-3xl blur-xl opacity-0 group-hover:opacity-20 transition duration-500"></div>
              <div class="relative h-full bg-gray-900/90 backdrop-blur-xl p-8 rounded-3xl flex flex-col">
                <div class="w-16 h-16 bg-purple-500/10 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 group-hover:bg-purple-500/20 transition-all duration-300 text-3xl">
                  🔍
                </div>
                <h3 class="text-2xl font-bold text-white mb-3">AI搜索翻译</h3>
                <p class="text-gray-400 mb-8 flex-1 leading-relaxed">强大的AI翻译引擎，支持多种语言互译，理解上下文语境，提供精准结果。</p>
                <div class="flex items-center text-purple-400 font-medium mt-auto group-hover:text-purple-300">
                  <span>立即翻译</span>
                  <svg class="ml-2 h-5 w-5 transform group-hover:translate-x-2 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
                </div>
              </div>
            </div>
          </router-link>

          <!-- 功能卡片 3 -->
          <router-link to="/essay" class="group animate-on-scroll block h-full" data-delay="300">
            <div class="h-full relative p-[1px] rounded-3xl bg-gradient-to-b from-white/10 to-transparent hover:from-pink-500/50 hover:to-rose-500/50 transition-all duration-500">
              <div class="absolute inset-0 bg-gradient-to-r from-pink-500 to-rose-500 rounded-3xl blur-xl opacity-0 group-hover:opacity-20 transition duration-500"></div>
              <div class="relative h-full bg-gray-900/90 backdrop-blur-xl p-8 rounded-3xl flex flex-col">
                <div class="w-16 h-16 bg-pink-500/10 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 group-hover:bg-pink-500/20 transition-all duration-300 text-3xl">
                  📝
                </div>
                <h3 class="text-2xl font-bold text-white mb-3">智能作文批改</h3>
                <p class="text-gray-400 mb-8 flex-1 leading-relaxed">AI驱动写作助手，实时检测语法拼写错误，提供风格建议和优化方案。</p>
                <div class="flex items-center text-pink-400 font-medium mt-auto group-hover:text-pink-300">
                  <span>开始写作</span>
                  <svg class="ml-2 h-5 w-5 transform group-hover:translate-x-2 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
                </div>
              </div>
            </div>
          </router-link>
        </div>
      </section>

      <!-- 4. AI 技术亮点 -->
      <section class="w-full max-w-7xl mx-auto px-6 py-24">
        <div class="text-center mb-16 animate-on-scroll">
          <h2 class="text-4xl md:text-5xl font-bold mb-4">
            先进的 <span class="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500">AI技术</span>
          </h2>
          <p class="text-gray-400 text-lg md:text-xl max-w-2xl mx-auto">采用业界领先的人工智能技术，提供卓越的学习体验</p>
        </div>

        <!-- 亮点卡片 -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-20">
          <div v-for="(highlight, index) in techHighlights" :key="index" :data-delay="index * 100" class="animate-on-scroll group bg-gray-900/50 backdrop-blur-sm border border-gray-800 hover:border-purple-500/50 rounded-3xl p-6 transition-all duration-300 hover:-translate-y-2">
            <div class="text-4xl mb-5 group-hover:scale-110 transition-transform origin-left inline-block">{{ highlight.icon }}</div>
            <h3 class="text-xl font-bold text-white mb-3">{{ highlight.title }}</h3>
            <p class="text-gray-400 text-sm leading-relaxed">{{ highlight.description }}</p>
          </div>
        </div>

        <!-- 架构图 (暗黑酷炫版) -->
        <div class="relative animate-on-scroll">
          <div class="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-[2.5rem] blur-xl transform -rotate-1 scale-[1.02]"></div>
          <div class="relative bg-gray-900/90 backdrop-blur-xl border border-gray-800 p-8 md:p-12 rounded-[2.5rem] shadow-2xl">
            <h3 class="text-2xl md:text-3xl font-bold text-center text-white mb-10 tracking-wide">AI学习引擎架构</h3>
            <div class="flex flex-col md:flex-row items-center justify-around gap-6">
              <!-- 数据采集层 -->
              <div class="w-full md:w-1/3 bg-gray-800/50 border border-gray-700/50 p-6 md:p-8 rounded-2xl text-center hover:bg-gray-800 transition-colors">
                <div class="w-12 h-12 bg-cyan-500/20 rounded-full flex items-center justify-center mx-auto mb-4 text-cyan-400">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"></path></svg>
                </div>
                <h4 class="font-bold text-cyan-400 mb-2 text-lg">数据采集层</h4>
                <p class="text-gray-400 text-sm">收集用户行为与进度数据</p>
              </div>
              
              <!-- 箭头 -->
              <div class="hidden md:flex text-gray-600">
                <svg class="w-8 h-8 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
              </div>
              
              <!-- 分析处理层 -->
              <div class="w-full md:w-1/3 bg-gray-800/50 border border-gray-700/50 p-6 md:p-8 rounded-2xl text-center hover:bg-gray-800 transition-colors">
                <div class="w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-4 text-purple-400">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"></path></svg>
                </div>
                <h4 class="font-bold text-purple-400 mb-2 text-lg">分析处理层</h4>
                <p class="text-gray-400 text-sm">AI算法分析用户模式</p>
              </div>

              <!-- 箭头 -->
              <div class="hidden md:flex text-gray-600">
                <svg class="w-8 h-8 animate-pulse animation-delay-2000" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
              </div>
              
              <!-- 个性化推荐层 -->
              <div class="w-full md:w-1/3 bg-gray-800/50 border border-gray-700/50 p-6 md:p-8 rounded-2xl text-center hover:bg-gray-800 transition-colors">
                <div class="w-12 h-12 bg-pink-500/20 rounded-full flex items-center justify-center mx-auto mb-4 text-pink-400">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                </div>
                <h4 class="font-bold text-pink-400 mb-2 text-lg">个性化推荐层</h4>
                <p class="text-gray-400 text-sm">生成个性化学习路径</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 5. 底部 CTA -->
      <section class="w-full relative py-24 mt-12 overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-r from-cyan-600/10 via-purple-600/10 to-pink-600/10 backdrop-blur-3xl border-t border-white/5"></div>
        <div class="relative max-w-4xl mx-auto px-6 text-center animate-on-scroll">
          <h2 class="text-4xl md:text-5xl font-bold text-white mb-6">准备好开始了吗？</h2>
          <p class="text-xl text-gray-400 mb-10">加入成千上万已经通过 Moment Lingo 提升语言能力的用户</p>
          <router-link to="/auth" class="inline-block px-10 py-4 rounded-full bg-white text-gray-900 font-bold text-lg shadow-[0_0_30px_rgba(255,255,255,0.2)] hover:shadow-[0_0_50px_rgba(255,255,255,0.4)] hover:scale-105 transition-all duration-300">
            免费注册开始学习
          </router-link>
        </div>
      </section>
    </main>
    
    <!-- 6. 引入原有页脚 (在暗黑背景上加透明度层兼容) -->
    <div class="relative z-10 w-full bg-black/60 border-t border-gray-800">
      <ml-footer class="dark-footer-override" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import ScrollReveal from 'scrollreveal'
import MlFooter from '@/components/layout/MlFooter.vue'

// V1 迁移来的统计数据，使用更美观的展示值
const stats = ref([
  { target: '10W', label: '活跃用户', suffix: '+' },
  { target: '50W', label: '学习会话', suffix: '+' },
  { target: '98', label: '用户满意度', suffix: '%' },
  { target: '20', label: '支持语言', suffix: '+' }
])

// V1 迁移来的技术亮点数据
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
]

onMounted(() => {
  // 集成 ScrollReveal 滚动触发动画，配置参考原版
  const revealOptions = {
    origin: 'bottom',
    distance: '40px',
    duration: 800,
    easing: 'ease-out',
    reset: false,
    threshold: 0.2, // 减少触发阈值，使动画更容易在移动端出现
    viewOffset: {
      top: 0,
      bottom: 50
    }
  }

  const sr = ScrollReveal()
  const elements = document.querySelectorAll('.animate-on-scroll')

  elements.forEach((ele: any) => {
    const delay = Number(ele.getAttribute('data-delay') ?? 0)
    sr.reveal(ele, {
      ...revealOptions,
      delay
    })
  })
})
</script>

<style scoped>
/* 悬浮呼吸发光动画 */
@keyframes blob {
  0% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(40px, -50px) scale(1.1); }
  66% { transform: translate(-30px, 30px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}

.animate-blob {
  animation: blob 8s infinite ease-in-out;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}

/* 文字流光横扫动画 */
@keyframes gradient-x {
  0%, 100% { background-size: 200% 200%; background-position: left center; }
  50% { background-size: 200% 200%; background-position: right center; }
}

.animate-gradient-x {
  animation: gradient-x 3s ease infinite;
}

/* 头部进入动画 */
@keyframes fade-in-down {
  0% { opacity: 0; transform: translateY(-20px); }
  100% { opacity: 1; transform: translateY(0); }
}

.animate-fade-in-down {
  animation: fade-in-down 0.8s ease-out forwards;
}

/* 简单处理原有 MlFooter 在深色模式下的字体颜色显示问题 */
:deep(.dark-footer-override) {
  color: #9ca3af; /* Tailwind gray-400 */
}
:deep(.dark-footer-override h3), 
:deep(.dark-footer-override h4), 
:deep(.dark-footer-override .text-gray-900) {
  color: #f3f4f6 !important; /* 强制覆盖原有黑色文字为亮色 */
}
:deep(.dark-footer-override a:hover) {
  color: #22d3ee;
}
:deep(.dark-footer-override .bg-gray-100) {
  background-color: #1f2937 !important; /* 调整页脚内的浅色背景区块 */
  border: 1px solid #374151;
}
</style>
