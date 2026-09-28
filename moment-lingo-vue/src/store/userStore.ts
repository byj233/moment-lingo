import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { TypeChecker } from '@/utils/typeChecker.ts';
import { getMe } from '@/api/user.ts';

interface User {
  avatarUrl: string;
  nickname: string;
  token: string;
  userId: string;
}

const useUserStore = defineStore('userStore', () => {
  const refUserInfo = ref<User | null>(null);
  // 只读版本
  const userInfo = computed(() => refUserInfo.value);

  const save = (user: User) => {
    refUserInfo.value = user;
  };

  const clear = () => {
    refUserInfo.value = null;
  };

  const isLogin = () => {
    return TypeChecker.isNotNullOrUndefined(refUserInfo.value?.token ?? null);
  };

  const update = async () => {
    if (!isLogin()) {
      return;
    }
    const resp = await getMe();
    const user = resp.data;

    if (userInfo.value) {
      userInfo.value.nickname = user.nickname;
      userInfo.value.avatarUrl = user.avatarUrl;
    }
  };

  return {
    refUserInfo,
    userInfo,
    save,
    update,
    clear,
    isLogin
  };
}, { persist: true });

export {
  useUserStore
};