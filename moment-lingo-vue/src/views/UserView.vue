<script lang="ts" setup>
import { useUserStore } from '@/store/userStore.ts';
import { useRouter } from 'vue-router';
import { MlMessage } from '@/utils/feedBack.ts';
import MlNavbar from '@/components/layout/MlNavbar.vue';
import { ref, useTemplateRef } from 'vue';
import 'vue-cropper/dist/index.css';
import { VueCropper } from 'vue-cropper';
import { patchMe } from '@/api/user.ts';
import { FILE_DIR, Oss } from '@/utils/oss.ts';
import { useMobileDetector } from '@/utils/mobileDetector.ts';
import MlFooter from '@/components/layout/MlFooter.vue';
import { useTheme } from '@/composables/useTheme.ts';
import { themePresets } from '@/store/themeStore.ts';

const router = useRouter();
const userStore = useUserStore();
const userInfo = userStore.userInfo;
const { isMobile } = useMobileDetector();
const { activeTheme, switchTheme } = useTheme();

const avatarInput = useTemplateRef('avatar-input');
const cropperRef = useTemplateRef('cropper-ref');
const avatarPreviewVisible = ref(false);
const cropperVisible = ref(false);
const editProfileVisible = ref(false);
const themeSettingsVisible = ref(false);
const editNickname = ref(userInfo?.nickname ?? '');
const previewAvatarUrl = ref('');
const isLoading = ref(false);


function base64ToFile(base64: string, filename: string): File {
  const arr = base64.split(',') as string[];
  const mime = arr[0]?.match(/:(.*?);/)?.[1] || 'application/octet-stream';
  const byte_string = atob(arr[1]! || arr[0]!);
  let n = byte_string.length;
  const u8arr = new Uint8Array(n);

  while (n--) {
    u8arr[n] = byte_string.charCodeAt(n);
  }

  return new File([u8arr], filename, { type: mime });
}

function fileToPreviewUrl(file: File) {
  const reader = new FileReader();
  reader.onload = (e) => {
    previewAvatarUrl.value = e.target?.result as string;
  };
  reader.readAsDataURL(file);
}

async function onEditProfileConfirm() {
  try {
    isLoading.value = true;
    const nickname = editNickname.value.trim();
    if (!nickname) {
      MlMessage.error('昵称不能为空');
      return;
    }

    if (nickname.length > 20) {
      MlMessage.error('昵称不能超过20个字符');
      return;
    }

    if (previewAvatarUrl.value) {
      await Oss.uploadFile(FILE_DIR.AVATAR, base64ToFile(previewAvatarUrl.value, `${ userInfo?.userId }.webp`), `${ userInfo?.userId }.webp`);
    }

    await patchMe({ nickname: nickname, avatarUrl: `avatar/${ userInfo?.userId }.webp` });
    await userStore.update();

    editProfileVisible.value = false;
    MlMessage.success('个人资料更新成功');
    if (previewAvatarUrl.value) {
      previewAvatarUrl.value = '';
      MlMessage.info('头像将在审核后生效');
    }
  } catch (err) {
    console.log(err);
  } finally {
    isLoading.value = false;
  }
}

function onEditProfileCancel() {
  editNickname.value = userInfo?.nickname ?? '';
  previewAvatarUrl.value = '';
  editProfileVisible.value = false;
}


function onAvatarChangeTrigger() {
  avatarInput.value?.click();
}

function onAvatarFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]!;
  fileToPreviewUrl(file);
  cropperVisible.value = true;
}

function onCropperConfirm() {
  const cropper: any = cropperRef.value;
  cropper.getCropData((data: any) => {
    const file = base64ToFile(data, `${ userInfo?.userId }.webp`);
    fileToPreviewUrl(file);
    cropperVisible.value = false;
  });
}

function onCropperCancel() {
  previewAvatarUrl.value = '';
  cropperVisible.value = false;
}


function onLogout() {
  userStore.clear();
  MlMessage.success('已退出登录');
  router.push('/');
}

function goToMyCourses() {
  MlMessage.info('我的课程功能开发中');
}

function goToMyEssays() {
  MlMessage.info('我的作文功能开发中');
}

function goToMyVocabulary() {
  MlMessage.info('我的词汇功能开发中');
}

function goToAbout() {
  MlMessage.info('关于我们功能开发中');
}

</script>

<template>
  <div>
    <div class="min-h-screen bg-canvas">
      <div class="pt-20 pb-12">
        <div class="max-w-7xl mx-auto px-4 sm:px-8 lg:px-16">
          <!-- 页面标题 -->
          <div class="mb-8 md:block hidden">
            <div class="text-3xl md:text-4xl font-display font-normal text-ink">
              个人<span class="text-primary">中心</span>
            </div>
            <p class="mt-2 text-muted">管理您的账户信息和学习数据</p>
          </div>

          <div class=" md:hidden">
            <ml-navbar title="个人中心"/>
          </div>

          <!-- 个人中心内容 -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- 左侧：用户信息卡片 -->
            <div class="lg:col-span-1">
              <div class="bg-surface-card rounded-[8px] p-6 border border-hairline sticky top-24">
                <div class="text-center">
                  <div class="relative inline-block">
                    <img
                        :alt="userInfo?.nickname"
                        :src="userInfo?.avatarUrl"
                        class="w-28 h-28 rounded-full object-cover border-4 border-canvas mx-auto"
                        @click="avatarPreviewVisible = true"
                    />
                    <a-image-preview v-model:visible="avatarPreviewVisible" :src="userInfo?.avatarUrl"/>
                  </div>
                  <div class="mt-4 text-xl font-medium text-ink">{{ userInfo?.nickname }}</div>
                  <p class="text-muted text-sm mt-1">ID: {{ userInfo?.userId }}</p>
                  <button
                      class="mt-4 inline-flex items-center text-primary hover:text-primary-active font-medium transition-colors duration-300 group cursor-pointer"
                      @click="editProfileVisible = true"
                  >
                    编辑个人资料
                    <svg class="ml-1 w-4 h-4 transform group-hover:translate-x-1 transition-transform duration-300"
                         fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path d="M14 5l7 7m0 0l-7 7m7-7H3" stroke-linecap="round" stroke-linejoin="round"
                            stroke-width="2"></path>
                    </svg>
                  </button>
                </div>

                <div class="mt-8 pt-6 border-t border-hairline">
                  <button
                      class="w-full inline-flex items-center justify-center px-4 py-2.5 border border-hairline text-sm font-medium rounded-[8px] text-body bg-canvas hover:bg-surface-soft hover:text-error hover:border-error/30 transition-all duration-300 cursor-pointer"
                      @click="onLogout"
                  >
                    <svg class="mr-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                          d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"
                          stroke-linecap="round" stroke-linejoin="round"
                          stroke-width="2"></path>
                    </svg>
                    退出登录
                  </button>
                </div>
              </div>
            </div>

            <!-- 右侧：功能菜单 -->
            <div class="lg:col-span-2 space-y-6">
              <!-- 学习管理 -->
              <div class="bg-surface-card rounded-[8px] p-6 border border-hairline">
                <div class="text-[18px] font-medium text-ink mb-4 flex items-center">
                  <span class="w-1 h-5 bg-primary rounded-full mr-3"></span>
                  学习管理
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div
                      class="group p-5 rounded-[8px] bg-surface-soft hover:bg-surface-cream-strong transition-all duration-300 text-left cursor-pointer border border-hairline"
                      @click="goToMyCourses"
                  >
                    <div
                        class="w-12 h-12 rounded-[6px] bg-primary flex items-center justify-center text-white mb-3 group-hover:scale-110 transition-transform duration-300">
                      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                            stroke-linecap="round" stroke-linejoin="round"
                            stroke-width="2"></path>
                      </svg>
                    </div>
                    <h4 class="font-medium text-ink group-hover:text-primary transition-colors duration-300">
                      我的课程</h4>
                    <p class="text-caption text-muted mt-1">查看学习进度</p>
                  </div>

                  <div
                      class="group p-5 rounded-[8px] bg-surface-soft hover:bg-surface-cream-strong transition-all duration-300 text-left cursor-pointer border border-hairline"
                      @click="goToMyEssays"
                  >
                    <div
                        class="w-12 h-12 rounded-[6px] bg-success flex items-center justify-center text-white mb-3 group-hover:scale-110 transition-transform duration-300">
                      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                            stroke-linecap="round" stroke-linejoin="round"
                            stroke-width="2"></path>
                      </svg>
                    </div>
                    <h4 class="font-medium text-ink group-hover:text-success transition-colors duration-300">
                      我的作文</h4>
                    <p class="text-caption text-muted mt-1">管理作文记录</p>
                  </div>

                  <div
                      class="group p-5 rounded-[8px] bg-surface-soft hover:bg-surface-cream-strong transition-all duration-300 text-left cursor-pointer border border-hairline"
                      @click="goToMyVocabulary"
                  >
                    <div
                        class="w-12 h-12 rounded-[6px] bg-accent-amber flex items-center justify-center text-white mb-3 group-hover:scale-110 transition-transform duration-300">
                      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path d="M13 10V3L4 14h7v7l9-11h-7z" stroke-linecap="round" stroke-linejoin="round"
                              stroke-width="2"></path>
                      </svg>
                    </div>
                    <h4 class="font-medium text-ink group-hover:text-accent-amber transition-colors duration-300">
                      我的词汇</h4>
                    <p class="text-caption text-muted mt-1">查看词汇收藏</p>
                  </div>
                </div>
              </div>

              <!-- 其他功能 -->
              <div class="bg-surface-card rounded-[8px] p-6 border border-hairline">
                <div class="text-[18px] font-medium text-ink mb-4 flex items-center">
                  <span class="w-1 h-5 bg-primary rounded-full mr-3"></span>
                  其他功能
                </div>
                <div class="space-y-3">
                  <div
                      class="w-full flex items-center justify-between p-4 rounded-[8px] hover:bg-surface-soft transition-all duration-300 group cursor-pointer"
                      @click="themeSettingsVisible = true"
                  >
                    <div class="flex items-center">
                      <div
                          class="w-10 h-10 rounded-[6px] bg-surface-soft flex items-center justify-center text-muted group-hover:bg-primary/10 group-hover:text-primary transition-all duration-300">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" stroke-linecap="round" stroke-linejoin="round"
                                stroke-width="2"></path>
                        </svg>
                      </div>
                      <span
                          class="ml-4 font-medium text-body group-hover:text-primary transition-colors duration-300">主题配色</span>
                    </div>
                    <div class="flex items-center gap-3">
                      <div class="flex gap-1">
                        <span :style="{ backgroundColor: themePresets.find(p => p.name === activeTheme)?.colors['--color-primary'] }"
                              class="w-3 h-3 rounded-full border border-hairline shadow-sm"></span>
                        <span :style="{ backgroundColor: themePresets.find(p => p.name === activeTheme)?.colors['--color-accent-light'] }"
                              class="w-3 h-3 rounded-full border border-hairline shadow-sm"></span>
                        <span :style="{ backgroundColor: themePresets.find(p => p.name === activeTheme)?.colors['--color-canvas'] }"
                              class="w-3 h-3 rounded-full border border-hairline shadow-sm"></span>
                      </div>
                      <svg
                          class="w-5 h-5 text-muted-soft group-hover:text-primary group-hover:translate-x-1 transition-all duration-300"
                          fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path d="M9 5l7 7-7 7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                      </svg>
                    </div>
                  </div>

                  <div
                      class="w-full flex items-center justify-between p-4 rounded-[8px] hover:bg-surface-soft transition-all duration-300 group cursor-pointer"
                      @click="goToAbout"
                  >
                    <div class="flex items-center">
                      <div
                          class="w-10 h-10 rounded-[6px] bg-surface-soft flex items-center justify-center text-muted group-hover:bg-accent-amber/10 group-hover:text-accent-amber transition-all duration-300">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"></path>
                        </svg>
                      </div>
                      <span
                          class="ml-4 font-medium text-body group-hover:text-accent-amber transition-colors duration-300">关于我们</span>
                    </div>
                    <svg
                        class="w-5 h-5 text-muted-soft group-hover:text-accent-amber group-hover:translate-x-1 transition-all duration-300"
                        fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path d="M9 5l7 7-7 7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- 图片裁剪上传弹窗 -->
      <template v-if="isMobile">
        <a-modal :simple="true" :visible="cropperVisible"
                 :width="350"
                 @cancel="onCropperCancel"
                 @ok="onCropperConfirm">
          <div class="h-[350px] w-[280px]">
            <vue-cropper
                ref="cropper-ref"
                :auto-crop="true"
                :fixed="true"
                :fixed-number="[1, 1]"
                :img="previewAvatarUrl"
                output-type="webp"
            />
          </div>
        </a-modal>
      </template>
      <template v-else>
        <a-modal :simple="true" :visible="cropperVisible" :width="700" @cancel="onCropperCancel"
                 @ok="onCropperConfirm">
          <div class="h-[500px] w-[600px]">
            <vue-cropper
                ref="cropper-ref"
                :auto-crop="true"
                :fixed="true"
                :fixed-number="[1, 1]"
                :img="previewAvatarUrl"
                output-type="webp"
            />
          </div>
        </a-modal>
      </template>

      <!-- 编辑个人资料弹窗 -->
      <a-modal :ok-loading="isLoading" :simple="true" :visible="editProfileVisible"
               :width="350" @cancel="onEditProfileCancel" @ok="onEditProfileConfirm">
        <div>
          <div class="space-y-6">
            <!-- 头像编辑 -->
            <div class="flex flex-col items-center">
              <img
                  :alt="editNickname"
                  :src="previewAvatarUrl || userInfo?.avatarUrl"
                  class="w-24 h-24 rounded-full object-cover border-4 border-white mx-auto cursor-pointer"
                  @click="onAvatarChangeTrigger"
              />
              <p class="text-gray-500 text-sm mt-2">点击头像进行编辑</p>
              <input
                  ref="avatar-input"
                  accept="image/jpeg,image/png,image/jpg,image/webp"
                  class="hidden"
                  type="file"
                  @change="onAvatarFileChange"
              />
            </div>
          </div>
          <div class="mt-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">昵称</label>
            <a-input
                v-model="editNickname"
                maxlength="20"
                placeholder="请输入昵称"
                type="text"
            />
            <p class="text-gray-400 text-xs mt-1">最多20个字符</p>
          </div>
        </div>
      </a-modal>

      <a-modal :footer="false" :simple="true"
               :visible="themeSettingsVisible" :width="420" @cancel="themeSettingsVisible = false">
        <template #title>
          <div class="text-lg font-medium text-ink">主题设置</div>
        </template>
        <div class="space-y-4 py-2">
          <p class="text-sm text-muted">选择你喜欢的主题配色方案</p>
          <div class="grid grid-cols-1 gap-3">
            <div
                v-for="preset in themePresets"
                :key="preset.name"
                :class="activeTheme === preset.name
                ? 'border-primary bg-surface-soft shadow-sm'
                : 'border-hairline hover:border-primary/40 hover:bg-surface-soft'"
                class="flex items-center gap-4 p-4 rounded-[8px] border cursor-pointer transition-all duration-300"
                @click="switchTheme(preset.name); themeSettingsVisible = false"
            >
              <div class="flex gap-1.5 shrink-0">
                <span
                    :style="{ backgroundColor: preset.colors['--color-primary'] }"
                    class="w-5 h-5 rounded-full border border-white/20 shadow-sm"
                ></span>
                <span
                    :style="{ backgroundColor: preset.colors['--color-accent-light'] }"
                    class="w-5 h-5 rounded-full border border-white/20 shadow-sm"
                ></span>
                <span
                    :style="{ backgroundColor: preset.colors['--color-canvas'] }"
                    class="w-5 h-5 rounded-full border border-white/20 shadow-sm"
                ></span>
              </div>
              <span class="flex-1 font-medium text-body">{{ preset.label }}</span>
              <svg
                  v-if="activeTheme === preset.name"
                  class="w-5 h-5 text-primary shrink-0"
                  fill="none" stroke="currentColor" viewBox="0 0 24 24"
              >
                <path d="M5 13l4 4L19 7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
              </svg>
            </div>
          </div>
        </div>
      </a-modal>
    </div>
    <ml-footer/>
  </div>
</template>