import axios from 'axios';
import { type SseEvents, sseRequest } from '@/utils/request.ts';

interface TtsData {
  content: string;
  model: string;
  voiceKey: string;
}

async function listVoices() {
  const resp = await axios.get('/tts/voices/list');
  return resp.data;
}

function ttsStream(data: TtsData, events: SseEvents) {
  return sseRequest('/tts/stream', { method: 'POST', body: data }, events);
}


export {
  listVoices,
  ttsStream
};