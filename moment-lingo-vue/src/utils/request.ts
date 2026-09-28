import { type EventSourceMessage, fetchEventSource } from '@microsoft/fetch-event-source';
import { baseUrl, isDev, wsUrl } from '@/config';
import { useUserStore } from '@/store/userStore.ts';
import { TypeChecker } from '@/utils/typeChecker.ts';

interface SseEvents {
  onStart?: Function,
  onProcessing?: Function,
  onEnd?: Function,
  onError?: Function
}

interface SseRequestOptions {
  method: 'GET' | 'POST' | 'DELETE' | 'PUT' | 'HEAD' | 'PATCH' | 'OPTIONS',
  headers?: any
  body?: object
}


function addDefaultErrorEvent(sseEvents: SseEvents) {
  if (typeof sseEvents.onError === 'undefined') {
    sseEvents.onError = () => {
    };
  }
}

function handleSseEvent(e: EventSourceMessage, sseEvents: SseEvents) {
  if (e.event === 'START' && TypeChecker.isNotNullOrUndefined(sseEvents.onStart)) {
    sseEvents.onStart(e);
  }

  if (e.event === 'PROCESSING' && TypeChecker.isNotNullOrUndefined(sseEvents.onProcessing)) {
    sseEvents.onProcessing(e);
  }

  if (e.event === 'END' && TypeChecker.isNotNullOrUndefined(sseEvents.onEnd)) {
    sseEvents.onEnd(e);
  }

  if (e.event === 'ERROR' && TypeChecker.isNotNullOrUndefined(sseEvents.onError)) {
    sseEvents.onError(e);
    console.log(e.data);
  }
}

function getToken() {
  const userStore = useUserStore();
  if (isDev) {
    return 'test-token';
  }

  return userStore.userInfo?.token ?? '';
}


async function sseRequest(url: string, options: SseRequestOptions, sseEvents: SseEvents) {
  addDefaultErrorEvent(sseEvents);
  const controller = new AbortController();

  await fetchEventSource(baseUrl + url, {
    method: options.method,
    headers: {
      'Authorization': `Bearer ${getToken()}`,
      ...options?.headers,
    },
    body: JSON.stringify(options?.body) === 'null' ? null : JSON.stringify(options?.body),
    onmessage: (e) => {
      handleSseEvent(e, sseEvents);
    },
    onerror: err => {
      console.log(err);
      throw err;
    },
    signal: controller.signal
  });

  return controller;
}


async function wsRequest(url: string, sseEvents: SseEvents) {
  const socket = new WebSocket(`${wsUrl}/${url}?token=${getToken()}`);

  socket.onopen = () => {
    console.log('websocket connect');
  };

  socket.onmessage = (messageEvent: MessageEvent) => {
    const resp = JSON.parse(messageEvent.data);
    handleSseEvent(resp, sseEvents);
  };

  socket.onclose = () => {
    console.log('websocket close');
  };

  return {
    send: (data: any) => {
      socket.send(data);
    },
    abort: () => {
      socket.close();
    }
  };
}

export {
  sseRequest,
  wsRequest,
  type SseEvents
};