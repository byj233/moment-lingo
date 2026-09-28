<script lang="ts" setup>
import { onMounted, reactive, ref } from 'vue';
import { register, sendCaptcha } from '@/api/auth.ts';
import { getAccountType, validatePasscode } from '@/utils/common.ts';
import { useUserStore } from '@/store/userStore.ts';
import { useRouter } from 'vue-router';
import { MlMessage } from '@/utils/feedBack.ts';
import MlSplitText from '@/components/MlSplitText.vue';

const router = useRouter();
const userStore = useUserStore();
const isLoading = ref(false);
const isSendingCode = ref(false);

const registerForm = reactive({
  nickname: '',
  account: '',
  passcode: '',
  confirmPasscode: '',
  code: ''
});

// 验证码倒计时
const countDown = ref(0);

async function onSendCaptcha() {
  if (countDown.value > 0) {
    return;
  }

  const type = getAccountType(registerForm.account);
  if (type === -1) {
    MlMessage.warning('账号格式错误');
    return;
  }

  isSendingCode.value = true;
  try {
    await sendCaptcha({
      account: registerForm.account,
      scene: 'register',
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

async function onRegister() {
  const type = getAccountType(registerForm.account);
  if (type === -1) {
    MlMessage.warning('账号格式错误');
    return;
  }


  if (!registerForm.nickname) {
    MlMessage.info('请输入昵称');
    return;
  }

  if (!registerForm.account || !registerForm.passcode || !registerForm.confirmPasscode) {
    MlMessage.info('请输入账号、密码和确认密码');
    return;
  }

  if (!validatePasscode(registerForm.passcode)) {
    return;
  }

  if (registerForm.passcode !== registerForm.confirmPasscode) {
    MlMessage.info('两次输入的密码不一致');
    return;
  }

  if (!registerForm.code) {
    MlMessage.info('请输入验证码');
    return;
  }

  isLoading.value = true;
  try {
    const resp = await register({
      nickname: registerForm.nickname.trim(),
      account: registerForm.account.trim(),
      passcode: registerForm.passcode.trim(),
      code: registerForm.code.trim()
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
  MlMessage.success('注册成功');
}

onMounted(() => {
  if (userStore.isLogin()) {
    MlMessage.success('已登录，3s后将返回');
    setTimeout(() => {
      router.replace('/');
    }, 3000);
  }
});
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4 bg-canvas">
    <div class="w-full max-w-md bg-surface-card rounded-[8px] border border-hairline overflow-hidden">
      <div class="p-6 sm:p-8">
        <div class="text-center mb-6 sm:mb-8">
          <div class="text-2xl sm:text-3xl font-display font-normal text-ink mb-2">
            <ml-split-text :delay="200" text="创建账户"/>
          </div>
          <p class="text-muted">欢迎加入我们，请填写以下信息</p>
        </div>

        <form @submit.prevent="onRegister">
          <div class="mb-4">
            <label class="block text-body text-sm font-medium mb-2" for="register-nickname">
              昵称
            </label>
            <input
                id="register-nickname"
                v-model="registerForm.nickname"
                autocomplete="nickname"
                class="input-field"
                placeholder="请输入昵称"
                type="text"
            />
          </div>

          <div class="mb-4">
            <label class="block text-body text-sm font-medium mb-2" for="register-account">
              账号
            </label>
            <input
                id="register-account"
                v-model="registerForm.account"
                autocomplete="username"
                class="input-field"
                placeholder="请输入手机号或邮箱"
                type="text"
            />
          </div>

          <div class="mb-4">
            <label class="block text-body text-sm font-medium mb-2" for="register-password">
              密码
            </label>
            <input
                id="register-password"
                v-model="registerForm.passcode"
                autocomplete="new-password"
                class="input-field"
                placeholder="请输入密码"
                type="password"
            />
          </div>

          <div class="mb-4">
            <label class="block text-body text-sm font-medium mb-2" for="confirm-password">
              确认密码
            </label>
            <input
                id="confirm-password"
                v-model="registerForm.confirmPasscode"
                autocomplete="new-password"
                class="input-field"
                placeholder="请再次输入密码"
                type="password"
            />
          </div>

          <div class="mb-4">
            <label class="block text-body text-sm font-medium mb-2" for="register-code">
              验证码
            </label>
            <div class="flex gap-3">
              <input
                  id="register-code"
                  v-model="registerForm.code"
                  autocomplete="one-time-code"
                  class="input-field flex-1"
                  placeholder="请输入验证码"
                  type="text"
              />
              <button
                  :class="[
                  'px-3 sm:px-4 py-3 rounded-[6px] font-medium text-sm focus:outline-none transition flex items-center justify-center whitespace-nowrap',
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

          <button
              :disabled="isLoading"
              class="w-full bg-primary text-on-primary py-3 px-4 rounded-[8px] hover:bg-primary-active focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center cursor-pointer"
              type="submit"
          >
            <template v-if="isLoading">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      fill="currentColor"></path>
              </svg>
              注册中...
            </template>
            <template v-else>
              注册
            </template>
          </button>
        </form>

        <div class="mt-6 text-center">
          <p class="text-muted text-sm">
            已有账户？
            <router-link class="font-medium text-primary hover:text-primary-active" to="/auth/login">
              立即登录
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>


<style scoped>
/* 输入框样式 */
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

/* 移动端优化 */
@media (max-width: 640px) {
  .input-field {
    padding: 10px 14px;
    font-size: 0.9375rem;
  }

  /* 验证码按钮在小屏幕上的优化 */
  .input-field.flex-1 {
    min-width: 0;
  }
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