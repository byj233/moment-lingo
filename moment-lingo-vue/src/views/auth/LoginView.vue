<script lang="ts" setup>
import { onMounted, reactive, ref } from 'vue';
import { login, sendCaptcha } from '@/api/auth.ts';
import { getAccountType } from '@/utils/common.ts';
import { useUserStore } from '@/store/userStore.ts';
import { useRouter } from 'vue-router';
import { MlMessage } from '@/utils/feedBack.ts';
import MlSplitText from '@/components/MlSplitText.vue';

const router = useRouter();
const userStore = useUserStore();
const loginMode = ref<'pwd' | 'sms'>('sms');
const isLoading = ref(false);
const isSendingCode = ref(false);
const passcodeForm = reactive({
  account: '',
  passcode: ''
});
const smsForm = reactive({
  account: '',
  code: ''
});

// 验证码倒计时
const countDown = ref(0);
const tooltipVisible = ref(true);


function onSwitchLoginMode(mode: 'pwd' | 'sms') {
  if (isLoading.value) {
    return;
  }
  loginMode.value = mode;
}


async function onSendCaptcha() {
  if (countDown.value > 0) {
    return;
  }

  const type = getAccountType(smsForm.account);
  if (type === -1) {
    MlMessage.warning('账号格式错误');
    return;
  }

  isSendingCode.value = true;
  try {
    await sendCaptcha({
      account: smsForm.account,
      scene: 'login'
    });

    MlMessage.success('验证码发送成功');
    countDown.value = 60;
    const interval = setInterval(() => {
      countDown.value--;
      if (countDown.value <= 0) {
        clearInterval(interval);
      }
    }, 1000);
  } catch (err) {
    console.log(err);
  } finally {
    isSendingCode.value = false;
  }
}

async function onPwdLogin() {
  const type = getAccountType(passcodeForm.account);
  if (type === -1) {
    MlMessage.warning('账号格式错误');
    return;
  }

  if (!passcodeForm.passcode.trim()) {
    MlMessage.info('请输入密码');
    return;
  }

  isLoading.value = true;
  try {
    const resp = await login({
      account: passcodeForm.account.trim(),
      passcode: passcodeForm.passcode.trim(),
      scene: 'pwd'
    });

    userStore.save(resp.data);
    toIndex();
  } catch (err) {
    console.log(err);
  } finally {
    isLoading.value = false;
  }
}

async function onSmsLogin() {
  const type = getAccountType(smsForm.account);
  if (type === -1) {
    MlMessage.warning('账号格式错误');
    return;
  }

  if (!smsForm.code.trim()) {
    MlMessage.info('请输入验证码');
    return;
  }

  isLoading.value = true;
  try {
    const resp = await login({
      account: smsForm.account.trim(),
      captcha: smsForm.code.trim(),
      scene: 'sms'
    });

    userStore.save(resp.data);
    toIndex();
  } catch (err) {
    console.log(err);
  } finally {
    isLoading.value = false;
  }
}

function toIndex() {
  router.push('/');
  MlMessage.success('登录成功');
}

onMounted(() => {
  if (userStore.isLogin()) {
    MlMessage.success('已登录，3s后将返回');
    setTimeout(() => {
      router.replace('/');
    }, 3000);
  }

  setTimeout(() => {
    tooltipVisible.value = false;
  }, 2000);
});
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4 md:p-8 bg-canvas">
    <!-- 主容器 - 在小屏幕占满宽度，大屏幕限制最大宽度并添加阴影 -->
    <div
        class="w-full max-w-md bg-surface-card rounded-[8px] border border-hairline overflow-hidden transition-all duration-300">
      <div class="p-6 sm:p-8">
        <!-- 标题区域 - 响应式调整间距和字体大小 -->
        <div class="text-center mb-6 sm:mb-8">
          <div class="text-2xl sm:text-3xl font-display font-normal text-ink mb-2">
            <ml-split-text :delay="200" text="欢迎回来"/>
          </div>
          <p class="text-muted text-sm sm:text-base">请登录您的账户</p>
        </div>

        <!-- 登录方式切换 -->
        <div class="flex bg-surface-soft rounded-[6px] p-1 mb-5 sm:mb-6 relative">
          <!-- 滑动指示器 -->
          <div
              :class="{'translate-x-[calc(100%+4px)]': loginMode === 'sms'}"
              class="absolute top-1 bottom-1 w-[calc(50%-6px)] bg-canvas border border-hairline rounded-[4px] transition-all duration-400 ease-in-out"
          ></div>
          <button
              :class="[
              loginMode === 'pwd'
                ? 'text-primary'
                : isLoading ? 'text-muted cursor-not-allowed' : 'text-muted hover:text-ink'
            ]"
              :disabled="isLoading"
              class="flex-1 py-2 px-3 text-xs sm:text-sm font-medium transition-colors duration-200 relative z-10"
              @click="onSwitchLoginMode('pwd')"
          >
            密码登录
          </button>
          <button
              :class="[
              loginMode === 'sms'
                ? 'text-primary'
                : isLoading ? 'text-muted cursor-not-allowed' : 'text-muted hover:text-ink'
            ]"
              :disabled="isLoading"
              class="flex-1 py-2 px-3 text-xs sm:text-sm font-medium transition-colors duration-200 relative z-10"
              @click="onSwitchLoginMode('sms')"
          >
            验证码登录
          </button>
        </div>

        <transition mode="out-in" name="fade">
          <!-- 密码登录表单 -->
          <template v-if="loginMode === 'pwd'">
            <form @submit.prevent="onPwdLogin">
              <div class="mb-3 sm:mb-4">
                <label class="block text-body text-xs sm:text-sm font-medium mb-1.5 sm:mb-2" for="username">
                  账号
                </label>
                <input
                    id="username"
                    v-model="passcodeForm.account"
                    class="input-field"
                    placeholder="请输入手机号或邮箱"
                    type="text"
                />
              </div>

              <div class="mb-3 sm:mb-4">
                <label class="block text-body text-xs sm:text-sm font-medium mb-1.5 sm:mb-2" for="password">
                  密码
                </label>
                <input
                    id="password"
                    v-model="passcodeForm.passcode"
                    class="input-field"
                    placeholder="请输入密码"
                    type="password"
                />
              </div>

              <div class="flex justify-end mb-3 sm:mb-4">
                <div class="text-xs sm:text-sm">
                  <a class="font-medium text-primary hover:text-primary-active" href="#">
                    忘记密码?
                  </a>
                </div>
              </div>

              <button
                  :disabled="isLoading"
                  class="w-full bg-primary text-on-primary py-2.5 sm:py-3 px-4 rounded-[8px] hover:bg-primary-active focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center cursor-pointer"
                  type="submit"
              >
                <template v-if="isLoading">
                  <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                          fill="currentColor"></path>
                  </svg>
                  登录中...
                </template>
                <template v-else>
                  登录
                </template>
              </button>
            </form>
          </template>

          <!-- 验证码登录表单 -->
          <template v-else>
            <form @submit.prevent="onSmsLogin">
              <div class="mb-3 sm:mb-4">
                <label class="block text-body text-xs sm:text-sm font-medium mb-1.5 sm:mb-2" for="phone">
                  账号
                </label>
                <input
                    id="phone"
                    v-model="smsForm.account"
                    class="input-field"
                    placeholder="请输入手机号或邮箱"
                    type="tel"
                />
              </div>

              <div class="mb-3 sm:mb-4">
                <label class="block text-body text-xs sm:text-sm font-medium mb-1.5 sm:mb-2" for="code">
                  验证码
                </label>
                <div class="flex gap-2 sm:gap-3">
                  <input
                      id="code"
                      v-model="smsForm.code"
                      class="input-field flex-1"
                      placeholder="请输入验证码"
                      type="text"
                  />
                  <button
                      :class="[
                      'px-3 sm:px-4 py-2.5 sm:py-3 rounded-[6px] font-medium text-xs sm:text-sm focus:outline-none transition flex items-center justify-center',
                      countDown > 0 || isSendingCode
                        ? 'bg-surface-soft text-muted cursor-not-allowed'
                        : 'bg-primary/10 text-primary hover:bg-primary/20'
                    ]"
                      :disabled="countDown > 0 || isSendingCode"
                      type="button"
                      @click="onSendCaptcha"
                  >
                    <template v-if="isSendingCode">
                      <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-current" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                stroke-width="4"></circle>
                        <path class="opacity-75"
                              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                              fill="currentColor"></path>
                      </svg>
                      发送中...
                    </template>
                    <template v-else>
                      {{ countDown > 0 ? `${ countDown }s后重发` : '发送验证码' }}
                    </template>
                  </button>
                </div>
              </div>

              <div class="flex justify-end mb-3 sm:mb-4">
                <div class="text-xs sm:text-sm">
              <span class="font-medium text-muted-soft">
                首次登录将直接注册
              </span>
                </div>
              </div>

              <button
                  :disabled="isLoading"
                  class="w-full bg-primary text-on-primary py-2.5 sm:py-3 px-4 rounded-[8px] hover:bg-primary-active focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center cursor-pointer"
                  type="submit"
              >
                <template v-if="isLoading">
                  <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                          fill="currentColor"></path>
                  </svg>
                  登录中...
                </template>
                <template v-else>
                  登录
                </template>
              </button>
            </form>
          </template>
        </transition>

        <!-- 注册链接 -->
        <div class="mt-5 sm:mt-6 text-center">
          <p class="text-muted text-xs sm:text-sm">
            还没有账户？
            <router-link class="font-medium text-primary hover:text-primary-active" to="/auth/register">
              立即注册
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.input-field {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--color-hairline);
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.25s ease;
  background-color: var(--color-canvas);
  color: var(--color-ink);
}

.input-field::placeholder {
  color: var(--color-muted-soft);
  transition: color 0.25s ease;
  font-size: 14px;
}


.input-field:hover:not(:focus):not(:disabled) {
  border-color: var(--color-primary);
}

.input-field:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(204, 120, 92, 0.15);
}

.input-field:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  background-color: var(--color-surface-soft);
  border-color: var(--color-hairline);
}
</style>
