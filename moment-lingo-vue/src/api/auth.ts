import axios from 'axios';

interface CaptchaReq {
  account: string;
  scene: 'login' | 'register' | 'modify';
}

interface LoginReq {
  account: string;
  scene: 'sms' | 'pwd';
  passcode?: string;
  captcha?: string;
}

interface RegisterReq {
  nickname: string;
  passcode: string;
  account: string;
  code: string;
}

async function sendCaptcha(data: CaptchaReq) {
  const resp = await axios.post('/auth/captcha/send', data);
  return resp.data;
}

async function login(data: LoginReq) {
  const resp = await axios.post('/auth/login', data);
  return resp.data;
}

async function register(data: RegisterReq) {
  const resp = await axios.post('/auth/register', data);
  return resp.data;
}

async function options() {
  const resp = await axios.get('/auth/options');
  return resp.data;
}

export {
  sendCaptcha,
  login,
  register,
  options
};