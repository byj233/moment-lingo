import axios from 'axios';
import { useUserStore } from '@/store/userStore.ts';
import JSONbig from 'json-bigint';
import { baseUrl, isDev } from '@/config';
import { MlMessage } from '@/utils/feedBack.ts';
import router from '@/router';

axios.defaults.baseURL = baseUrl;

const jsonBig = JSONbig({ storeAsString: true });

axios.defaults.transformResponse = [(data: any) => {
  try {
    return jsonBig.parse(data);
  } catch (err) {
    return data;
  }
}];


// 请求拦截器
axios.interceptors.request.use((config: any) => {
  const userStore = useUserStore();
  if (isDev) {
    config.headers['Authorization'] = 'Bearer test-token';
  } else {
    config.headers['Authorization'] = `Bearer ${ userStore.userInfo?.token ?? '' }`;
  }
  return config;
}, (err: any) => {
  return Promise.reject(err);
});

// 响应拦截器
axios.interceptors.response.use(async (resp: any) => {
  await errorHandler(resp.data);
  return resp;
}, (err) => {
  console.log(err);
  return Promise.reject(err);
});


async function errorHandler(resp: any) {
  const code = resp.code;
  if (code === 200) {
    return;
  }

  if (code === 401) {
    useUserStore().clear();
    await router.push('/auth');
  }

  console.log(resp);
  MlMessage.error(resp.msg);
  throw new Error(resp.msg);
}

export {
  errorHandler
};