import { type SseEvents, sseRequest } from '@/utils/request.ts';
import axios from 'axios';


interface OcrData {
  imageUrl: string;
}

interface AIWriteData {
  content: string;
  corrections: any[];
}

function ocr(data: OcrData, events: SseEvents) {
  return sseRequest('/ai/ocr', { method: 'POST', body: data }, events);
}


async function AIWrite(data: AIWriteData) {
  const resp = await axios.post('/ai/write', data);
  return resp.data;
}

export {
  ocr,
  AIWrite
};