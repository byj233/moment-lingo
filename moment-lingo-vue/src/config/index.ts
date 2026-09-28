const isDev = false;




const platform: 'app' | 'web' = 'web';
const version = '0.4.5';

let baseUrl: string, wsUrl: string;

if (isDev) {
  baseUrl = 'http://localhost:8080/moment-lingo';
  wsUrl = 'ws://localhost:8000';
} else {
  baseUrl = 'https://www.momentlingo.cn/api';
  wsUrl = 'wss://www.momentlingo.cn/ws';
}

export {
  baseUrl,
  wsUrl,
  isDev,
  platform,
  version
};
