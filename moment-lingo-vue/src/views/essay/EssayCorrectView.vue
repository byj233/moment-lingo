<script lang="ts" setup>
import { onMounted, onUnmounted, reactive, ref, useTemplateRef } from 'vue';
import { Message } from '@arco-design/web-vue';
import { MlMessage, MlNotification } from '@/utils/feedBack.ts';
import { FILE_DIR, Oss } from '@/utils/oss.ts';
import { ocr } from '@/api/ai.ts';
import mammoth from 'mammoth';
import { useRouter } from 'vue-router';
import { getEssayCorrectTask, listEssayCorrect, listEssayCorrectTask, putEssayCorrectTask } from '@/api/essay.ts';
import { createH5UploadLink, getExtensionFromUrl } from '@/utils/common.ts';
import { QrcodeSvg } from 'qrcode.vue';
import { getUploadTask } from '@/api/oss.ts';
import MlNavbar from '@/components/layout/MlNavbar.vue';
import { v4 as uuidv4 } from 'uuid';

const router = useRouter();

interface Correction {
  error: string;
  original: string;
  corrected: string;
  explanation: string;
  anchorAfter: string;
  anchorBefore: string;
}

interface ScoreBreakdown {
  content: string;
  grammar: string;
  vocabulary: string;
  organization: string;
}

interface Score {
  total: string;
  breakdown: ScoreBreakdown;
}

interface Result {
  score: Score;
  feedback: string;
  strengths: string[];
  weaknesses: string[];
  corrections: Correction[];
  suggestions: string[];
}

interface History {
  essayId: string;
  content: string;
  result: Result;
  createdAt: string;
}

enum TaskStatus {
  PENDING = 'PENDING',
  SUCCEED = 'SUCCEED',
  FAILED = 'FAILED'
}

interface Task {
  content: string;
  status: TaskStatus;
  createdAt: string;
  taskId: string;
}

const state = reactive({
  isLoading: false,
  isSubmitted: false,
  activeTab: '0'
});


const essay = ref('');
const historyTableColumns = [
  {
    dataIndex: 'content',
    title: '作文',
    ellipsis: true
  },
  {
    dataIndex: 'createdAt',
    title: '提交时间',
    slotName: 'time',
    width: 200
  },
  {
    dataIndex: 'wordCount',
    title: '字数',
    slotName: 'words',
    width: 80
  },
  {
    dataIndex: 'score',
    title: '得分',
    slotName: 'score'
  },
  {
    dataIndex: 'actions',
    title: '操作',
    slotName: 'actions'
  }
];


const historyList = ref<History[]>([]);
const taskList = ref<Task[]>([]);
const fileInputRef = useTemplateRef('file-input');
const isLoading = ref(false);
const isUploading = ref(false);
const isRecognizing = ref(false);
const modalVisible = ref(false);
const isQrcodeLoading = ref(false);
const qrcodeUrl = ref('');
const isQrcodeExpired = ref(false);
let taskTimer: any, expireTimer: any;
const totalPage = ref(0);
const currentPage = ref(1);
const pollingTasks = ref<Map<string, any>>(new Map());


async function handleScanUploadFile(fileUrl: string) {
  const ext = getExtensionFromUrl(fileUrl)?.toLowerCase();
  if (!ext) {
    MlMessage.error('文件解析失败，请重新上传');
    return;
  }

  if (ext === 'txt') {
    isRecognizing.value = true;
    try {
      const response = await fetch(fileUrl);
      essay.value = await response.text();
      MlMessage.success('文件解析成功');
    } catch (err) {
      console.log(err);
      MlMessage.error('文件读取失败，请稍后再试');
    } finally {
      isRecognizing.value = false;
    }
    return;
  }

  if (ext === 'docx') {
    isRecognizing.value = true;
    try {
      const response = await fetch(fileUrl);
      const arrayBuffer = await response.arrayBuffer();
      const text = await mammoth.extractRawText({ arrayBuffer });
      essay.value = text.value;
      MlMessage.success('文档内容已解析，复杂格式可能需要手动调整');
    } catch (err) {
      console.log(err);
      MlMessage.error('文件读取失败，请稍后再试');
    } finally {
      isRecognizing.value = false;
    }
    return;
  }

  await handelOCR(fileUrl);
}

async function handelOCR(imageUrl: string) {
  const ext = getExtensionFromUrl(imageUrl)?.toLowerCase();
  if (!ext) {
    MlMessage.error('文件解析失败，请重新上传');
    return;
  }

  const extensions = ['jpg', 'jpeg', 'png', 'webp'];
  if (!extensions.includes(ext)) {
    MlMessage.error('仅支持jpg、jpeg、png、webp格式的图片');
    return;
  }

  isRecognizing.value = true;
  essay.value = '';
  return await ocr({ imageUrl }, {
    onProcessing: (e: any) => {
      const data = JSON.parse(e.data);
      essay.value += data.content;
    },
    onError: () => {
      isRecognizing.value = false;
      MlMessage.error('图片识别失败，请稍后再试');
    },
    onEnd: () => {
      isRecognizing.value = false;
      MlMessage.success('图片识别成功');
    }
  });
}

async function fileUpload(event: Event) {
  const target = event.target as HTMLInputElement;
  const files = target.files;

  if (!files || files.length === 0) {
    return;
  }
  const file = files[0]!;
  const fileName = file.name.toLowerCase() ?? '';

  // 检查文件大小（限制5MB）
  if (file.size > 5 * 1024 * 1024) {
    MlMessage.warning('文件大小不能超过5MB');
    return;
  }

  isUploading.value = true;

  if (fileName.endsWith('.txt')) {
    const reader = new FileReader();
    reader.onload = (e) => {
      essay.value = e.target?.result as string;
      isUploading.value = false;
      MlMessage.success('文件上传成功');
    };

    reader.onerror = () => {
      isUploading.value = false;
      MlMessage.error('文件读取失败，请稍后再试');
    };

    reader.readAsText(file, 'UTF-8');
    return;
  }

  if (fileName.endsWith('.docx')) {
    try {
      const text = await mammoth.extractRawText({ arrayBuffer: await file.arrayBuffer() });
      essay.value = text.value;
      MlMessage.success('文档内容已上传，复杂格式可能需要手动调整');
    } catch (err) {
      console.log(err);
      MlMessage.error('文件读取失败，请稍后再试');
    } finally {
      isUploading.value = false;
    }
    return;
  }

  try {
    const imageUrl = await Oss.uploadFile(FILE_DIR.TEMP, file, `${ uuidv4() }-${ fileName }`);
    MlMessage.success('图片已上传，正在识别中');
    isUploading.value = false;

    await handelOCR(imageUrl);
  } catch (err) {
    console.log(err);
    MlMessage.error('文件读取失败，请稍后再试');
  } finally {
    isUploading.value = false;
    isRecognizing.value = false;
  }
}

function onFileUploadClick() {
  fileInputRef.value?.click();
}


async function submitEssay(content: string) {
  try {
    state.isLoading = true;
    state.isSubmitted = true;
    await putEssayCorrectTask({ content });
    await checkAndStartPendingTasks();
    essay.value = '';
    MlMessage.success('作文批改任务已提交');
  } catch (err) {
    console.log(err);
    MlMessage.error('作文批改任务提交失败，请稍后再试');
  } finally {
    state.isLoading = false;
    state.isSubmitted = false;
  }
}

function onSubmit() {
  if (calculateWords(essay.value) < 10) {
    Message.warning('作文内容至少需要10字符');
    return;
  }

  if (calculateWords(essay.value) > 1500) {
    Message.warning('作文内容不得超过1500字符');
    return;
  }
  submitEssay(essay.value);
}

function getScoreLevel(score: number) {
  if (score >= 9) {
    return { level: '优秀', color: 'text-success' };
  }
  if (score >= 8) {
    return { level: '良好', color: 'text-primary' };
  }
  if (score >= 7) {
    return { level: '中等', color: 'text-accent-amber' };
  }
  if (score >= 6) {
    return { level: '及格', color: 'text-warning' };
  }
  return { level: '不及格', color: 'text-error' };
}

function onRegradeEssay(task: Task) {
  submitEssay(task.content);
  listEssayCorrectTask();
}

function calculateWords(content: string) {
  const trimmed = content.trim();
  if (!trimmed) {
    return 0;
  }

  const isAsciiOnly = /^[\x20-\x7E]*$/.test(trimmed);
  if (isAsciiOnly) {
    return trimmed.split(/\s+/).filter(word => word.length > 0).length;
  } else {
    return trimmed.replace(/\s+/g, '').length;
  }
}

interface PollingConfig {
  taskId: string;
  interval?: number;
  onSuccess?: (task: Task) => void;
  onFailed?: (task: Task) => void;
  onPending?: () => void;
}

function startTaskPolling(config: PollingConfig) {
  const { taskId, interval = 3000, onSuccess, onFailed, onPending } = config;

  if (pollingTasks.value.has(taskId)) {
    console.warn(`Task ${ taskId } is already polling`);
    return;
  }

  const checkTask = async () => {
    try {
      const resp = await getEssayCorrectTask(taskId);
      const task = resp.data as Task;

      const taskIndex = taskList.value.findIndex((item: Task) => item.taskId === taskId);
      if (taskIndex !== -1) {
        taskList.value[taskIndex] = task;
      } else {
        taskList.value.unshift(task);
      }

      if (task.status === TaskStatus.SUCCEED) {
        onSuccess?.(task);
        stopTaskPolling(taskId);
      } else if (task.status === TaskStatus.FAILED) {
        onFailed?.(task);
        stopTaskPolling(taskId);
      } else {
        onPending?.();
        const timer = setTimeout(checkTask, interval);
        pollingTasks.value.set(taskId, timer);
      }
    } catch (error) {
      console.error('Error polling task:', error);
      const timer = setTimeout(checkTask, interval);
      pollingTasks.value.set(taskId, timer);
    }
  };

  checkTask();
}

function stopTaskPolling(taskId: string) {
  const timer = pollingTasks.value.get(taskId);
  if (timer) {
    clearTimeout(timer);
    pollingTasks.value.delete(taskId);
  }
}

function stopAllPollingTasks() {
  pollingTasks.value.forEach((timer) => {
    clearTimeout(timer);
  });
  pollingTasks.value.clear();
}


function onPageChange(page: number) {
  currentPage.value = page;
  listHistory();
}

async function listHistory() {
  isLoading.value = true;
  const resp = await listEssayCorrect(currentPage.value, 10);
  const { total, data } = resp.data;
  totalPage.value = total;
  historyList.value = data;
  isLoading.value = false;
}

async function listTasks() {
  isLoading.value = true;
  const resp = await listEssayCorrectTask();
  taskList.value = resp.data;
  isLoading.value = false;
}

async function checkAndStartPendingTasks() {
  await listTasks();
  let pendingTask = 0;
  taskList.value.forEach(item => {
    if (item.status === TaskStatus.PENDING) {
      ++pendingTask;

      startTaskPolling({
        taskId: item.taskId,
        interval: 3000,
        onSuccess: () => {
          MlNotification.success('作文批改', '批改任务已完成');
        },
        onFailed: () => {
          MlNotification.error('作文批改', '批改任务已失败，请稍后再试');
        }
      });
    }
  });

  if (pendingTask > 0) {
    state.activeTab = '2';
    MlNotification.info('作文批改', `有${ pendingTask }个正在进行中的批改任务`);
  }
}

async function onTabChange(e: any) {
  // 历史记录
  if (e === '1') {
    await listHistory();
  }
  // 任务列表
  else if (e === '2') {
    await listTasks();
  }
  changeTab(e);
}

function changeTab(key: string) {
  state.activeTab = key;
  window.scroll({ top: 0, behavior: 'smooth' });
}

function toCorrectEssayDetail(record: History) {
  router.push(`/essay/correct/${ record.essayId }`);
}

async function onScanUploadClick() {
  isQrcodeLoading.value = true;
  const { url, taskId } = await createH5UploadLink();
  qrcodeUrl.value = url;
  isQrcodeLoading.value = false;
  modalVisible.value = true;
  isQrcodeExpired.value = false;

  const check = async () => {
    try {
      const resp = await getUploadTask(taskId);
      if (resp.data.status === TaskStatus.SUCCEED) {
        MlMessage.success('文件上传成功');
        modalVisible.value = false;
        await handleScanUploadFile(resp.data.fileUrl);
      } else if (resp.data.status === TaskStatus.FAILED) {
        MlMessage.error('文件上传失败，请稍后再试');
        modalVisible.value = false;
      } else {
        taskTimer = setTimeout(check, 1500);
      }
    } catch (err) {
      console.log(err);
      MlMessage.error('上传失败，请稍后再试');
      modalVisible.value = false;
    }
  };

  setTimeout(() => {
    check();
  }, 3000);
  // 1分钟后二维码失效
  expireTimer = setTimeout(() => {
    isQrcodeExpired.value = true;
    if (taskTimer) {
      clearTimeout(taskTimer);
      taskTimer = null;
    }
  }, 60000);
}

function onCloseQrcodeModal() {
  modalVisible.value = false;
  if (taskTimer) {
    clearTimeout(taskTimer);
    taskTimer = null;
  }

  if (expireTimer) {
    clearTimeout(expireTimer);
    expireTimer = null;
  }
}

onMounted(async () => {
  await checkAndStartPendingTasks();
});

onUnmounted(() => {
  stopAllPollingTasks();
  if (expireTimer) {
    clearTimeout(expireTimer);
  }
  if (taskTimer) {
    clearTimeout(taskTimer);
  }
});
</script>

<template>
  <div>
    <!-- web -->
    <div class="min-h-screen px-3 py-24 hidden md:block bg-canvas">
      <div class="max-w-4xl mx-auto ">
        <div class="text-center mb-12">
          <div class="relative inline-block">
            <h1 class="font-display text-[48px] leading-[1.1] tracking-[-1px] text-ink mb-3 relative z-10">
              <span class="text-primary">作文批改</span>
            </h1>
            <p class="text-muted text-[16px]">AI智能批改，提升英语写作水平</p>
          </div>
        </div>

        <a-tabs :active-key="state.activeTab" class="rounded-2xl" @change="onTabChange">
          <!-- 作文输入区域 -->
          <a-tab-pane key="0" title="我的作文">
            <div class="bg-surface-card rounded-[8px] p-6 border border-hairline">
              <div class="flex justify-between items-center mb-4">
                <h2 class="text-[18px] font-medium text-ink">我的作文</h2>
              </div>

              <div class="space-y-4">
                <!-- 内容输入区域  -->
                <div
                    class="relative rounded-[6px] border-2 border-hairline focus-within:border-primary/70 transition-colors duration-200">
              <textarea
                  v-model="essay"
                  :disabled="state.isSubmitted || isRecognizing"
                  class="w-full px-4 py-3 rounded-[6px] focus:outline-none resize-y min-h-[300px] transition-all duration-200 ease-out disabled:bg-surface-soft disabled:cursor-not-allowed pl-12 pt-13 placeholder-muted-soft bg-canvas text-ink"
                  placeholder="请输入作文内容，开始您的写作之旅..."
                  rows="15"
              />
                  <!-- 文本区域图标 -->
                  <div class="absolute left-4 top-4 text-muted-soft">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                          d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                          stroke-linecap="round" stroke-linejoin="round"
                          stroke-width="2"/>
                    </svg>
                  </div>

                  <!-- 字数统计 -->
                  <div class="absolute right-4 bottom-3 text-caption text-muted">
                    {{ calculateWords(essay) }} 字符
                  </div>

                  <!-- 文件上传和扫码按钮 -->
                  <div class="absolute top-2 right-3 flex gap-2">
                    <input
                        ref="file-input"
                        accept=".txt,.docx,image/*"
                        class="hidden"
                        type="file"
                        @change="fileUpload"
                    />

                    <button
                        :disabled="state.isSubmitted || isUploading || isRecognizing"
                        class="cursor-pointer flex items-center text-[13px] text-muted hover:text-primary disabled:opacity-50 disabled:cursor-not-allowed px-3 py-1 rounded-[6px] border border-hairline hover:border-primary transition-colors"
                        @click="onFileUploadClick"
                    >
                      <template v-if="isUploading || isRecognizing">
                        <svg class="w-4 h-4 animate-spin mr-1" fill="none"
                             viewBox="0 0 24 24">
                          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                  stroke-width="4"></circle>
                          <path class="opacity-75"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                fill="currentColor"></path>
                        </svg>
                      </template>
                      <template v-else>
                        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                              stroke-linecap="round" stroke-linejoin="round"
                              stroke-width="2"/>
                        </svg>
                      </template>
                      上传文件
                    </button>

                    <button
                        :disabled="state.isSubmitted || isUploading || isRecognizing"
                        class="cursor-pointer flex items-center text-[13px] text-muted hover:text-primary disabled:opacity-50 disabled:cursor-not-allowed px-3 py-1 rounded-[6px] border border-hairline hover:border-primary transition-colors"
                        type="button"
                        @click="onScanUploadClick"
                    >
                      <template v-if="isQrcodeLoading">
                        <svg class="w-4 h-4 animate-spin mr-1" fill="none"
                             viewBox="0 0 24 24">
                          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                  stroke-width="4"></circle>
                          <path class="opacity-75"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                fill="currentColor"></path>
                        </svg>
                      </template>
                      <template v-else>
                        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                              d="M3 7V5C3 4.44772 3.44772 4 4 4H7M3 7V19C3 19.5523 3.44772 20 4 20H20C20.5523 20 21 19.5523 21 19V7M3 7H21M21 7V5C21 4.44772 20.5523 4 20 4H17M12 12H12.01M8 12H8.01M16 12H16.01"
                              stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                        </svg>
                      </template>
                      扫码上传
                    </button>

                    <a-modal :ok-button-props="{status: 'danger',type:'secondary'}" :visible="modalVisible" hide-cancel
                             ok-text="关闭" simple title="请扫码上传作文图片或文档" @ok="onCloseQrcodeModal">
                      <div class="flex flex-col gap-3 items-center justify-center ">
                        <div class="relative">
                          <!-- 二维码 -->
                          <qrcode-svg :class="{'opacity-70': isQrcodeExpired}" :size="150" :value="qrcodeUrl"/>

                          <!-- 过期遮罩层 -->
                          <template v-if="isQrcodeExpired">
                            <div class="absolute inset-0  bg-black/50 flex items-center justify-center">
                              <div class="text-white font-bold text-lg transform -rotate-12">已过期</div>
                            </div>
                          </template>
                        </div>

                        <template v-if="isQrcodeExpired">
                          <p class="text-black font-bold text-lg">二维码已过期，请关闭后重新生成</p>
                        </template>
                      </div>
                    </a-modal>
                  </div>
                </div>

                <!-- 提交按钮  -->
                <div class="flex justify-end pt-2">
                  <div class="flex space-x-3">
                    <button
                        :disabled="state.isLoading || isUploading || isRecognizing"
                        class="cursor-pointer px-6 py-3 bg-primary text-on-primary rounded-[8px]
         disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2
         transition-all duration-200
         not-disabled:hover:bg-primary-active not-disabled:hover:-translate-y-0.5
         not-disabled:active:bg-primary-active"
                        type="button"
                        @click="onSubmit"
                    >
                      <template v-if="state.isLoading">
                        <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                  stroke-width="4"></circle>
                          <path class="opacity-75"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                fill="currentColor"></path>
                        </svg>
                      </template>
                      提交批改
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </a-tab-pane>

          <!-- 历史记录区域 -->
          <a-tab-pane key="1" title="历史记录">
            <div class="bg-surface-card rounded-[8px] p-6 border border-hairline">
              <div class="flex justify-between items-center mb-6">
                <h2 class="text-[18px] font-medium text-ink">历史记录</h2>
                <div class="flex items-center gap-4">
                  <div class="text-caption text-muted">{{ historyList.length }} 条记录</div>
                  <button
                      :disabled="isLoading"
                      class="cursor-pointer flex items-center justify-center w-8 h-8 rounded-full bg-surface-soft text-muted hover:bg-hairline transition-all duration-300"
                      @click="listHistory"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path d="M21 2v6h-6M3 12a9 9 0 0115-6.7L21 8M3 22v-6h6M21 12a9 9 0 01-15 6.7L3 16"
                            stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                    </svg>
                  </button>
                </div>
              </div>
              <a-table :bordered="{cell:true}" :columns="historyTableColumns" :data="historyList" :hoverable="false"
                       :loading="isLoading"
                       :pagination="{total:totalPage,current:currentPage,defaultPageSize:10,hideOnSinglePage:true}"
                       :scroll="{x:800}"
                       :stripe="true" @page-change="onPageChange">
                <template #time="{ record }">
                  <div
                      class="flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-surface-soft text-body">
                 <span>
                  <svg class="w-3 h-3 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                       xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"
                          stroke-width="2"></path>
                  </svg>

              </span>
                    <span>{{ record?.createdAt ?? '' }}</span>
                  </div>
                </template>

                <template #words="{record}">
                  {{ calculateWords(record?.content ?? '') }}
                </template>

                <template #score="{record}">
                  <div class="flex items-center justify-center">
                    <div class="text-xl font-medium text-primary mr-3">
                      {{ record?.result?.score?.total ?? 'N/A' }}
                      <span class="text-sm text-muted">/10</span>
                    </div>
                    <div class="px-2 py-0.5 rounded-full bg-primary/10 text-primary text-sm font-medium">
                      {{ getScoreLevel(parseFloat(record?.result?.score?.total ?? '0')).level }}
                    </div>
                  </div>
                </template>

                <template #actions="{record}">
                  <div class="flex flex-col">
                    <button
                        class="cursor-pointer text-sm text-primary hover:text-primary-active px-3 py-1 rounded-[6px] border border-primary/30 hover:border-primary transition-all duration-300 ease-in-out"
                        @click="toCorrectEssayDetail(record)"
                    >
                      查看详情
                    </button>
                  </div>
                </template>
              </a-table>
            </div>
          </a-tab-pane>

          <!-- 任务列表区域 -->
          <a-tab-pane key="2" title="任务列表">
            <div class="bg-surface-card rounded-[8px] p-6 border border-hairline transition-all duration-300">
              <!-- 标题区域优化 -->
              <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-2">
                <h2 class="text-[18px] font-medium text-ink flex items-center gap-2">
                  任务列表
                  <span class="h-4 w-px bg-hairline"></span>
                  <span class="text-caption text-muted font-normal">实时监控任务进度</span>
                </h2>
                <div class="flex items-center gap-3">
                  <div class="text-caption text-muted bg-surface-soft px-3 py-1.5 rounded-full">
                    正在执行的任务: {{ taskList.filter(t => t.status === TaskStatus.PENDING).length }} 个
                  </div>
                  <button
                      :disabled="isLoading"
                      class="cursor-pointer flex items-center justify-center w-8 h-8 rounded-full bg-surface-soft text-muted hover:bg-hairline transition-all duration-300"
                      @click="listTasks"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path d="M21 2v6h-6M3 12a9 9 0 0115-6.7L21 8M3 22v-6h6M21 12a9 9 0 01-15 6.7L3 16"
                            stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                    </svg>
                  </button>
                </div>
              </div>

              <!-- 任务列表区域 -->
              <div class="space-y-4">
                <template v-if="isLoading">
                  <div class="flex flex-col items-center justify-center py-12 text-muted">
                    <div
                        class="w-8 h-8 border-2 border-hairline border-t-primary rounded-full animate-spin mb-3"></div>
                  </div>
                </template>

                <template v-else>
                  <template
                      v-for="(task, index) in taskList.filter(t => t.status === TaskStatus.PENDING || t.status === TaskStatus.FAILED)"
                      :key="index"
                  >
                    <div
                        :class="{'border-primary border ': task.status === TaskStatus.PENDING,'border-error border ': task.status === TaskStatus.FAILED}"
                        class="rounded-[6px] p-4 transition-all duration-300 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-l-4 bg-canvas"
                    >
                      <div class="flex items-start gap-3 flex-1 min-w-0">
                        <!-- 状态图标 -->
                        <div class="mt-0.5">
                          <div
                              :class="{'bg-primary animate-pulse': task.status === TaskStatus.PENDING,'bg-error': task.status === TaskStatus.FAILED}"
                              class="w-3 h-3 rounded-full"
                          />
                        </div>

                        <div class="min-w-0">
                          <h3 class="font-medium text-ink flex items-center gap-2 cursor-pointer">
                            <span class="text-xs text-muted-soft font-normal">#task{{ index + 1 }}</span>
                            <span
                                class="truncate max-w-[calc(100%-80px)] transition-colors duration-200 hover:text-primary">
                              {{ task.content }}
                            </span>
                          </h3>

                          <p class="text-caption text-muted mt-1.5">
                            <span class="opacity-80">提交时间：</span>{{ task.createdAt }}
                          </p>
                        </div>
                      </div>

                      <div class="flex items-center gap-3 self-end sm:self-auto flex-wrap justify-end">
                        <!-- 状态标签优化 -->
                        <span
                            :class="{'bg-primary/10 text-primary': task.status === TaskStatus.PENDING, 'bg-error/10 text-error': task.status === TaskStatus.FAILED}"
                            class="px-3 py-1 rounded-full text-xs font-medium transition-colors">
                          {{ task.status === TaskStatus.PENDING ? '处理中' : '失败' }}
                        </span>
                        <!-- 操作按钮优化 -->
                        <template v-if="task.status === TaskStatus.FAILED">
                          <a-button
                              class="transition-all hover:shadow-sm"
                              size="small"
                              status="success"
                              type="secondary"
                              @click="onRegradeEssay(task)"
                          >
                            重新执行
                          </a-button>
                        </template>
                      </div>
                    </div>
                  </template>

                  <!-- 无任务提示优化 -->
                  <template
                      v-if="taskList.filter(t => t.status === TaskStatus.PENDING || t.status === TaskStatus.FAILED).length === 0">
                    <div
                        class="text-center py-16 px-4 text-muted bg-canvas rounded-[8px] border border-dashed border-hairline transition-colors"
                    >
                      <div class="mb-3 text-muted-soft">
                        <svg class="h-12 w-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                             xmlns="http://www.w3.org/2000/svg">
                          <path
                              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                              stroke-linecap="round" stroke-linejoin="round"
                              stroke-width="1.5"/>
                        </svg>
                      </div>
                      <h3 class="text-[16px] font-medium mb-1 text-ink">暂无进行中的任务</h3>
                      <p class="text-caption text-muted-soft max-w-md mx-auto">
                        开始创建您的第一篇作文，AI将为您提供专业的批改建议
                      </p>
                    </div>
                  </template>
                </template>
              </div>
            </div>
          </a-tab-pane>
        </a-tabs>


        <div class="mt-8 bg-surface-card rounded-[8px] border border-hairline p-6">
          <h3 class="font-medium text-ink mb-3 flex items-center text-[18px]">
            <svg class="w-5 h-5 mr-2 text-primary" fill="currentColor" viewBox="0 0 20 20">
              <path clip-rule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                    fill-rule="evenodd"/>
            </svg>
            使用说明
          </h3>
          <ul class="grid grid-cols-1 md:grid-cols-3 gap-3 text-body text-[14px]">
            <li class="flex items-start bg-canvas p-3 rounded-[6px] border border-hairline">
              <svg class="w-5 h-5 mr-2 text-primary flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path clip-rule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      fill-rule="evenodd"/>
              </svg>
              <span>作文内容建议在100-500字之间，过短或过长可能影响批改效果</span>
            </li>
            <li class="flex items-start bg-canvas p-3 rounded-[6px] border border-hairline">
              <svg class="w-5 h-5 mr-2 text-primary flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path clip-rule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      fill-rule="evenodd"/>
              </svg>
              <span>支持上传.txt、.docx格式，以及图片识别，文件大小不超过5MB</span>
            </li>
            <li class="flex items-start bg-canvas p-3 rounded-[6px] border border-hairline">
              <svg class="w-5 h-5 mr-2 text-primary flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path clip-rule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      fill-rule="evenodd"/>
              </svg>
              <span>AI会从语法、词汇、句式结构等多个维度进行批改</span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- h5 -->
    <div class="md:hidden h-screen flex flex-col">
      <div class="h-12">
        <ml-navbar title="作文批改"/>
      </div>

      <div class="flex-1">
        <t-tabs v-model:value="state.activeTab" :sticky-props="{offsetTop:48}" class="h-full" sticky theme="line"
                @change="onTabChange">
          <t-tab-panel label="我的作文" value="0">
            <div class="h-[calc(100vh-98px)] overflow-auto p-4 space-y-4">
              <!-- 精致点缀输入区域 -->
              <div>
                <textarea
                    v-model="essay"
                    :disabled="state.isSubmitted || isRecognizing"
                    class="w-full h-80 p-4 border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-400 transition-all duration-200 resize-none"
                    placeholder="在这里输入作文..."
                />

                <!-- 底部栏 -->
                <div class="flex justify-between items-center mt-3 px-1">
                  <div class="flex items-center gap-2">
                    <div
                        :class="{
                        'bg-gray-400': calculateWords(essay) === 0,
                        'bg-blue-400': calculateWords(essay) > 0 && calculateWords(essay) < 10,
                        'bg-green-400': calculateWords(essay) >= 10 && calculateWords(essay) <= 1500,
                        'bg-orange-400': calculateWords(essay) > 1500
                      }"
                        class="w-2 h-2 rounded-full transition-all duration-200"
                    ></div>
                    <span class="text-sm text-gray-500">
                      {{ calculateWords(essay) }} 字
                    </span>
                  </div>

                  <input
                      ref="file-input"
                      accept=".txt,.docx,image/*"
                      class="hidden"
                      type="file"
                      @change="fileUpload"
                  />

                  <button
                      :disabled="state.isSubmitted || isUploading || isRecognizing"
                      class="cursor-pointer flex items-center text-sm text-gray-600 hover:text-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed px-3 py-2 rounded-lg border border-gray-300 hover:border-indigo-300 transition-colors"
                      @click="onFileUploadClick"
                  >
                    <template v-if="isUploading || isRecognizing">
                      <svg class="w-4 h-4 animate-spin mr-1" fill="none"
                           viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                stroke-width="4"></circle>
                        <path class="opacity-75"
                              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                              fill="currentColor"></path>
                      </svg>
                    </template>
                    <template v-else>
                      <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                            stroke-linecap="round" stroke-linejoin="round"
                            stroke-width="2"/>
                      </svg>
                    </template>
                    上传文件
                  </button>
                </div>
              </div>
              <!-- 提交按钮 -->
              <div class="pt-2">
                <button
                    :disabled="state.isLoading || isUploading || isRecognizing"
                    class="flex items-center justify-center gap-2 w-full px-6 py-4 bg-gradient-to-r from-indigo-500 via-indigo-600 to-purple-600 text-white rounded-2xl font-semibold shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98] transition-all duration-200 transform"
                    @click="onSubmit"
                >
                  <template v-if="state.isLoading">
                    <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                              stroke-width="4"></circle>
                      <path class="opacity-75"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                            fill="currentColor"></path>
                    </svg>
                  </template>
                  提交批改
                </button>
              </div>
            </div>
          </t-tab-panel>
          <t-tab-panel label="历史记录" value="1">
            <div class="h-[calc(100vh-98px)] overflow-auto p-4 space-y-4">
              <template v-if="isLoading">
                <div class="flex items-center justify-center py-8">
                  <div class="flex flex-col items-center gap-3">
                    <div class="w-8 h-8 border-2 border-gray-200 border-t-purple-500 rounded-full animate-spin"></div>
                    <span class="text-sm text-gray-500">加载中...</span>
                  </div>
                </div>
              </template>

              <template v-else>
                <template v-if="historyList.length === 0">
                  <div class="text-center py-12 text-gray-500 space-y-4">
                    <div class="mb-6">
                      <div
                          class="w-24 h-24 mx-auto bg-gradient-to-br from-gray-100 to-indigo-100 rounded-full flex items-center justify-center mb-4">
                        <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                              d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                              stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"/>
                        </svg>
                      </div>
                      <h3 class="text-lg font-medium text-gray-600 mb-2">暂无历史记录</h3>
                      <p class="text-sm text-gray-400 max-w-sm mx-auto leading-relaxed mb-4">
                        开始创建您的第一篇作文，AI将为您提供专业的批改建议
                      </p>
                      <button
                          class="px-6 py-2.5 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-medium text-sm shadow-lg hover:shadow-xl active:scale-95 transition-all duration-200"
                          @click="changeTab('0')"
                      >
                        立即写作
                      </button>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <template v-for="history in historyList" :key="history.essayId">
                    <div
                        class="bg-gradient-to-r from-gray-50 to-indigo-50/30 rounded-2xl p-4 border border-gray-200 active:scale-[0.98] transition-all duration-200">
                      <div class="flex items-start gap-3">
                        <div class="flex-1">
                          <p class="text-sm text-gray-700 line-clamp-2 leading-relaxed" v-html="history.content"></p>
                          <div class="mt-3 flex items-center justify-between">
                            <div class="flex items-center gap-3 text-xs text-gray-500">
                              <div class="flex items-center gap-1">
                                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <circle cx="12" cy="12" r="9" stroke-width="1.5"/>
                                  <path d="M12 7v5l3 2" stroke-linecap="round" stroke-linejoin="round"
                                        stroke-width="1.5"/>
                                </svg>
                                <span>{{ history.createdAt }}</span>
                              </div>
                              <div class="flex items-center gap-1">
                                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path
                                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                                      stroke-linecap="round" stroke-linejoin="round"
                                      stroke-width="2"/>
                                </svg>
                                <span>{{ calculateWords(history.content) }}</span>
                              </div>
                            </div>
                            <div class="flex items-center gap-2">
                              <div
                                  class="flex items-center gap-1 px-2 py-1 rounded-full bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-700 text-xs font-medium">
                                {{ getScoreLevel(parseFloat(history?.result?.score?.total ?? '0')).level }}
                              </div>
                              <div class="text-base font-bold text-indigo-600">
                                {{ history?.result?.score?.total ?? 'N/A' }}<span
                                  class="text-xs text-gray-500">/10</span></div>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div class="mt-3 pt-3 border-t border-gray-100/50 flex justify-end">
                        <button
                            class="text-xs px-3 py-1.5 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 text-white active:scale-95 transition-all duration-200"
                            @click="toCorrectEssayDetail(history)">查看详情
                        </button>
                      </div>
                    </div>
                  </template>
                  <div class="mt-4">
                    <a-pagination :current="currentPage" :page-size="10" :total="totalPage" hide-on-single-page
                                  simple @change="onPageChange"/>
                  </div>
                </template>
              </template>
            </div>
          </t-tab-panel>
          <t-tab-panel label="任务列表" value="2">
            <div class="h-[calc(100vh-98px)] overflow-auto p-4 space-y-4">
              <template v-if="isLoading">
                <div class="flex items-center justify-center py-8">
                  <div class="flex flex-col items-center gap-3">
                    <div class="w-8 h-8 border-2 border-gray-200 border-t-purple-500 rounded-full animate-spin"></div>
                    <span class="text-sm text-gray-500">加载中...</span>
                  </div>
                </div>
              </template>
              <template v-else>
                <!-- 处理中和失败的任务 -->
                <template
                    v-for="task in taskList.filter(t => t.status === TaskStatus.PENDING || t.status === TaskStatus.FAILED)">
                  <div
                      class="bg-gradient-to-r from-violet-50 to-red-50/30 rounded-2xl p-4 border border-orange-100/50 active:scale-[0.98] transition-all duration-200">
                    <div class="flex items-start gap-3">
                      <div
                          :class="{'bg-blue-500 animate-pulse': task.status === TaskStatus.PENDING, 'bg-red-500': task.status === TaskStatus.FAILED}"
                          class="w-3 h-3 rounded-full mt-2"></div>
                      <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium text-gray-800 line-clamp-2 leading-relaxed">{{ task.content }}</p>
                        <div class="flex items-center gap-3 text-xs text-gray-500 mt-3">
                          <div class="flex items-center gap-1">
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <circle cx="12" cy="12" r="9" stroke-width="1.5"/>
                              <path d="M12 7v5l3 2" stroke-linecap="round" stroke-linejoin="round"
                                    stroke-width="1.5"/>
                            </svg>
                            <span>{{ task.createdAt }}</span>
                          </div>
                          <div class="flex items-center gap-1">
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path
                                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                                  stroke-linecap="round" stroke-linejoin="round"
                                  stroke-width="2"/>
                            </svg>
                            <span>{{ calculateWords(task.content) }}</span>
                          </div>
                        </div>
                      </div>
                      <div class="flex flex-col items-end gap-2">
                        <span
                            :class="{'bg-blue-100 text-blue-700': task.status === TaskStatus.PENDING, 'bg-red-100 text-red-700': task.status === TaskStatus.FAILED}"
                            class="px-2 py-1 rounded-full text-xs font-medium">
                          {{ task.status === TaskStatus.PENDING ? '处理中' : '失败' }}
                        </span>
                        <button v-if="task.status === TaskStatus.FAILED"
                                class="text-xs px-3 py-1 rounded-full bg-green-500 text-white active:scale-95 transition-all duration-200"
                                @click="onRegradeEssay(task)">重新执行
                        </button>
                      </div>
                    </div>
                  </div>
                </template>
                <!-- 空状态 -->
                <template
                    v-if="taskList.filter(t => t.status === TaskStatus.PENDING || t.status === TaskStatus.FAILED).length === 0">
                  <div class="text-center py-12 text-gray-500">
                    <div class="mb-4">
                      <svg class="h-16 w-16 mx-auto text-gray-300" fill="none" stroke="currentColor"
                           viewBox="0 0 24 24">
                        <path
                            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                            stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"/>
                      </svg>
                    </div>
                    <h3 class="text-base font-medium mb-2">暂无任务记录</h3>
                    <p class="text-sm text-gray-400 max-w-sm mx-auto leading-relaxed">
                      开始创建您的第一篇作文，AI将为您提供专业的批改建议
                    </p>
                  </div>
                </template>
              </template>
            </div>
          </t-tab-panel>
        </t-tabs>
      </div>
    </div>
  </div>
</template>

<style scoped>
:deep(.arco-tabs-tab-active) {
  color: var(--color-primary) !important;
}

:deep(.arco-tabs-nav-ink) {
  background-color: var(--color-primary) !important;
}

:deep(.arco-tabs-tab-title::before) {
  display: none;
}
</style>
