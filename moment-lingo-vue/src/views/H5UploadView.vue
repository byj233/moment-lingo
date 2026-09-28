<script lang="ts" setup>
import { computed, onMounted, ref, useTemplateRef } from 'vue';
import { FILE_DIR, Oss } from '@/utils/oss.ts';
import { MlMessage } from '@/utils/feedBack.ts';
import { v4 as uuidv4 } from 'uuid';
import { useRoute } from 'vue-router';
import { baseUrl } from '@/config';
import { errorHandler } from '@/api';

const route = useRoute();
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const MAX_FILE_COUNT = 5;
let canUpload = false;

interface UploadFile {
  id: string;
  file: File;
  name: string;
  size: string;
  type: string;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  url?: string;
}

const files = ref<UploadFile[]>([]);
const fileInputRef = useTemplateRef('file-input');

function formatFileSize(bytes: number): string {
  if (bytes === 0) {
    return '0 B';
  }
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function getFileIcon(type: string): string {
  if (type.includes('image')) {
    return '🖼️';
  }
  if (type.includes('video')) {
    return '🎬';
  }
  if (type.includes('audio')) {
    return '🎵';
  }
  if (type.includes('pdf')) {
    return '📄';
  }
  if (type.includes('zip') || type.includes('rar')) {
    return '📦';
  }
  if (type.includes('text') || type.includes('document')) {
    return '📝';
  }
  return '📎';
}

function fileUpload(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    addFiles(Array.from(target.files));
  }
}

function onFileUploadClick() {
  if (!canUpload) {
    MlMessage.error('上传任务不存在');
    return;
  }
  fileInputRef.value?.click();
}

function addFiles(newFiles: File[]) {
  if (files.value.length + newFiles.length > MAX_FILE_COUNT) {
    MlMessage.warning(`最多只能上传 ${ MAX_FILE_COUNT } 个文件`);
    newFiles = newFiles.slice(0, MAX_FILE_COUNT);
  }

  newFiles.forEach(file => {
    if (file.size > MAX_FILE_SIZE) {
      MlMessage.warning(`文件 ${ file.name } 大小超过 5MB，已忽略`);
      return;
    }

    files.value.push({
      id: uuidv4(),
      file,
      name: file.name,
      size: formatFileSize(file.size),
      type: file.type,
      progress: 0,
      status: 'pending'
    });
  });
}


async function uploadFile(fileItem: UploadFile) {
  await getUploadTask();

  if (!canUpload) {
    MlMessage.error('上传任务不存在');
    return;
  }
  fileItem.status = 'uploading';

  const { token, taskId } = route.query;
  try {
    const resp = await Oss.h5Upload(token as string, FILE_DIR.TEMP, fileItem.file, `${ uuidv4() }-${ fileItem.name }`, (p: number) => {
      fileItem.progress = Math.floor(p * 100);
      if (fileItem.progress >= 100) {
        fileItem.progress = 100;
        fileItem.status = 'success';
        // 生成预览URL（仅限图片和视频）
        if (fileItem.file.type.includes('image') || fileItem.file.type.includes('video')) {
          fileItem.url = URL.createObjectURL(fileItem.file);
        }
      }
    });

    await fetch(`${ baseUrl }/oss/upload/task`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${ token }` },
      body: JSON.stringify({
        taskId: taskId,
        fileUrl: resp
      })
    }).then(resp => resp.json());

    MlMessage.success('上传成功');
  } catch (err) {
    console.log(err);
    fileItem.status = 'error';
    MlMessage.error('上传失败，请稍后重试~');
  }
}

function startUpload() {
  files.value.forEach(file => {
    if (file.status === 'pending') {
      uploadFile(file);
    }
  });
}

function removeFile(fileId: string) {
  const index = files.value.findIndex(f => f.id === fileId);
  if (index !== -1) {
    // 释放对象URL
    if (files.value[index]?.url) {
      URL.revokeObjectURL(files.value[index]?.url);
    }
    files.value = files.value.filter(f => f.id !== fileId);
  }
}

function clearAllFiles() {
  files.value.forEach(file => {
    if (file.url) {
      URL.revokeObjectURL(file.url);
    }
  });
  files.value = [];
}

const uploadStats = computed(() => {
  const total = files.value.length;
  const completed = files.value.filter(f => f.status === 'success').length;
  const uploading = files.value.filter(f => f.status === 'uploading').length;
  const pending = files.value.filter(f => f.status === 'pending').length;
  return { total, completed, uploading, pending };
});

async function getUploadTask() {
  const { token, taskId } = route.query;
  const resp = await fetch(`${ baseUrl }/oss/upload/task/${ taskId }`, {
    method: 'GET',
    headers: { Authorization: `Bearer ${ token }` }
  }).then(resp => resp.json());

  if (resp.code === 200) {
    canUpload = resp.data.status !== 'FAILED';
  } else {
    await errorHandler(resp);
    canUpload = false;
  }
}

onMounted(() => {
  getUploadTask();
});
</script>

<template>
  <div class="h-screen bg-canvas flex flex-col p-3">
    <!-- 顶部导航栏 -->
    <div class="h-12 flex-shrink-0">
      <t-navbar title="文件上传"/>
    </div>
    <!-- 主内容区域 -->
    <div class="flex-1 overflow-hidden">
      <!-- 首页 - 上传界面 -->
      <transition mode="out-in" name="fade-scale">
        <template v-if="files.length === 0">
          <div class="flex flex-col items-center justify-center h-full">
            <div class="text-center mb-8">
              <div
                  class="w-20 h-20 bg-primary rounded-[8px] flex items-center justify-center mb-4 mx-auto">
                <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                        stroke-linecap="round" stroke-linejoin="round"
                        stroke-width="2"/>
                </svg>
              </div>
              <h2 class="text-xl font-medium text-ink mb-2">上传文件</h2>
              <p class="text-muted text-sm">支持图片、视频、文档等多种格式，文件不得超过5MB</p>
            </div>

            <!-- 上传按钮 -->
            <div class="w-full max-w-sm">
              <input
                  ref="file-input"
                  accept="*/*"
                  class="hidden"
                  multiple
                  type="file"
                  @change="fileUpload"
              />
              <div
                  class="bg-primary text-on-primary py-4 px-6 rounded-[8px] font-medium text-center active:bg-primary-active transition-colors"
                  @click="onFileUploadClick">
                <div class="flex items-center justify-center space-x-2">
                  <span>选择文件</span>
                </div>
              </div>
            </div>

            <!-- 快捷操作提示 -->
            <div class="mt-8 text-center">
              <p class="text-muted-soft text-xs">点击上方按钮选择文件进行上传</p>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="px-2 pt-2  h-full">
            <!-- 文件列表页面 -->
            <div class="flex flex-col gap-2 h-full">
              <!-- 上传统计 -->
              <div class="bg-surface-soft h-20 rounded-[8px] p-4 flex-shrink-0">
                <div class="grid grid-cols-4 gap-2 text-center">
                  <div>
                    <div class="text-lg font-medium text-ink">{{ uploadStats.total }}</div>
                    <div class="text-xs text-muted">总文件</div>
                  </div>
                  <div>
                    <div class="text-lg font-medium text-success">{{ uploadStats.completed }}</div>
                    <div class="text-xs text-muted">已完成</div>
                  </div>
                  <div>
                    <div class="text-lg font-medium text-primary">{{ uploadStats.uploading }}</div>
                    <div class="text-xs text-muted">上传中</div>
                  </div>
                  <div>
                    <div class="text-lg font-medium text-warning">{{ uploadStats.pending }}</div>
                    <div class="text-xs text-muted">等待中</div>
                  </div>
                </div>
              </div>
              <!-- 文件列表 -->
              <div class=" space-y-2  overflow-auto flex-1 ">
                <transition-group name="list">
                  <template v-for="file in files" :key="file.id">
                    <div class="bg-surface-card border border-hairline rounded-[8px] p-3">
                      <div class="flex items-center space-x-3">
                        <!-- 文件图标 -->
                        <div class="w-10 h-10 bg-surface-soft rounded-[6px] flex items-center justify-center">
                          <span class="text-lg">{{ getFileIcon(file.type) }}</span>
                        </div>

                        <!-- 文件信息 -->
                        <div class="flex-1 min-w-0">
                          <p class="text-sm font-medium text-ink truncate">{{ file.name }}</p>
                          <p class="text-xs text-muted">{{ file.size }}</p>

                          <!-- 进度条 -->
                          <template v-if="file.status === 'uploading'">
                            <div class="mt-2">
                              <div class="flex justify-between text-xs text-muted mb-1">
                                <span>上传中</span>
                                <span>{{ Math.round(file.progress) }}%</span>
                              </div>
                              <div class="w-full bg-hairline rounded-full h-1.5">
                                <div
                                    :style="{ width: file.progress + '%' }"
                                    class="bg-primary h-1.5 rounded-full transition-all duration-300"
                                ></div>
                              </div>
                            </div>
                          </template>
                          <!-- 状态标签 -->
                          <template v-else>
                            <div class="mt-1">
                      <span
                          :class="[
                          'text-xs font-medium px-2 py-0.5 rounded-full',
                          file.status === 'pending' && 'bg-warning/10 text-warning',
                          file.status === 'success' && 'bg-success/10 text-success',
                          file.status === 'error' && 'bg-error/10 text-error'
                        ]">
                        {{
                          file.status === 'pending' ? '等待上传' : file.status === 'success' ? '上传完成' : '上传失败'
                        }}
                      </span>
                            </div>
                          </template>
                        </div>

                        <!-- 操作按钮 -->
                        <button
                            class="p-2 text-muted-soft hover:text-error transition-colors active:scale-95"
                            @click="removeFile(file.id)"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path d="M6 18L18 6M6 6l12 12" stroke-linecap="round" stroke-linejoin="round"
                                  stroke-width="2"/>
                          </svg>
                        </button>
                      </div>

                      <!-- 预览区域 -->
                      <template v-if="file.url && (file.type.includes('image') || file.type.includes('video'))">
                        <div class="mt-3">
                          <template v-if="file.type.includes('image')">
                            <div class="rounded-lg overflow-hidden border">
                              <img :alt="file.name" :src="file.url" class="w-full h-24 object-cover">
                            </div>
                          </template>
                          <template v-if="file.type.includes('video')">
                            <div class="rounded-lg overflow-hidden bg-black border">
                              <video :src="file.url" class="w-full h-24" controls></video>
                            </div>
                          </template>
                        </div>
                      </template>
                    </div>
                  </template>
                </transition-group>
              </div>
            </div>
            <!-- 底部操作栏 -->
            <div
                class="fixed bottom-0 left-0 right-0 h-20 rounded-t-md bg-surface-card border-t border-hairline p-4">
              <div class="flex gap-5">
                <button
                    :class="[
            'flex-1 py-3 rounded-[8px] font-medium transition-colors',
            uploadStats.pending === 0
              ? 'bg-surface-soft text-muted cursor-not-allowed'
              : 'bg-primary text-on-primary active:bg-primary-active'
          ]"
                    :disabled="uploadStats.pending === 0"
                    @click="startUpload"
                >
                  开始上传
                </button>
                <button
                    class="flex-1 py-3 bg-surface-soft text-body rounded-[8px] font-medium hover:bg-hairline active:bg-surface-cream-strong transition-colors"
                    @click="clearAllFiles"
                >
                  清空全部
                </button>
              </div>
            </div>
          </div>
        </template>
      </transition>
    </div>
  </div>
</template>

<style scoped>
/* 基础过渡设置 */
.list-move,
.list-enter-active,
.list-leave-active {
  transition: all 0.4s cubic-bezier(0.25, 0.1, 0.25, 1);
}

/* 入场/退场初始状态 */
.list-enter-from {
  opacity: 0;
  transform: translateX(10px);
}

/* 优化删除动画：向右淡出并缩小 */
.list-leave-from {
  /* 保留删除前的原始状态作为过渡起点 */
  opacity: 1;
  transform: translateX(0) scale(1);
}

.list-leave-to {
  opacity: 0;
  transform: translateX(20px) scale(0.95); /* 向右移动更远并轻微缩小 */
}

/* 关键优化：删除时脱离文档流但保持占位，避免其他元素瞬移 */
.list-leave-active {
  position: absolute;
  /* 固定宽度防止布局抖动 */
  width: calc(100% - 20px); /* 根据实际内边距调整 */
  pointer-events: none; /* 避免删除过程中触发交互 */
}

/* 移动动画优化：其他元素填补空位时更平滑 */
.list-move {
  transition-delay: 0.05s; /* 等待删除动画开始后再移动 */
}
</style>
