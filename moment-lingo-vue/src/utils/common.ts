import { MlMessage } from '@/utils/feedBack.ts';
import { useUserStore } from '@/store/userStore.ts';
import { putUploadTask } from '@/api/oss.ts';

function getAccountType(val: string): 1 | 2 | -1 {
  val = val.trim();
  if (val === '') {
    return -1;
  }

  // 邮箱正则：验证标准邮箱格式
  const emailReg = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  if (emailReg.test(val)) {
    return 1;
  }

  // 手机号正则：支持国内11位手机号，以1开头
  const phoneReg = /^1[3-9]\d{9}$/;
  if (phoneReg.test(val)) {
    return 2;
  }

  return -1;
}


function validatePasscode(passcode: string) {
  passcode = passcode.trim();
  if (passcode.length < 8) {
    MlMessage.info('密码长度至少为8位，需包含英文字母和数字');
    return false;
  }

  const hasLetter = /[a-zA-Z]/.test(passcode);
  const hasNumber = /\d/.test(passcode);

  if (!hasLetter) {
    MlMessage.warning('密码必须包含英文字母');
    return false;
  }

  if (!hasNumber) {
    MlMessage.info('密码必须包含数字');
    return false;
  }

  return true;
}

async function createH5UploadLink() {
  const userStore = useUserStore();
  const resp = await putUploadTask({});
  return {
    taskId: resp.data.taskId,
    url: `https://www.momentlingo.cn/h5-upload?token=${ userStore.userInfo?.token }&taskId=${ resp.data.taskId }`
  };
}

// 从预览url中提取文件扩展名
function getExtensionFromUrl(url: string): string | null {
  try {
    const parsedUrl = new URL(url);

    const pathname = parsedUrl.pathname;

    const filename = pathname.split('/').pop() || '';

    const lastDotIndex = filename.lastIndexOf('.');

    if (lastDotIndex <= 0) {
      return null;
    }

    return filename.slice(lastDotIndex + 1).toLowerCase();
  } catch (error) {
    console.error('解析URL错误 ', error);
    return null;
  }
}

function b64ToUint8Array(b64String: string) {
  const binaryString = atob(b64String);
  return new Uint8Array(binaryString.split('').map(char => char.charCodeAt(0)));
}

function uint8ArrayToB64(uint8Arr: Uint8Array) {
  let binary = '';
  const len = uint8Arr.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(uint8Arr[i]!);
  }
  return btoa(binary);
}


function delay(ms: number) {
  return new Promise((resolve: any) => {
    setTimeout(() => {
      resolve();
    }, ms);
  });
}


export {
  getAccountType,
  validatePasscode,
  createH5UploadLink,
  getExtensionFromUrl,
  b64ToUint8Array,
  uint8ArrayToB64,
  delay
};