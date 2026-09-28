import axios from 'axios';

interface PutEssayCorrectTaskReq {
  content: string;
}

async function putEssayCorrectTask(data: PutEssayCorrectTaskReq) {
  const res = await axios.post('/essay/correct/task', data);
  return res.data;
}


async function listEssayCorrectTask() {
  const res = await axios.get('/essay/correct/task/list');
  return res.data;
}

async function getEssayCorrectTask(taskId: string) {
  const res = await axios.get(`/essay/correct/task/${ taskId }`);
  return res.data;
}

async function listEssayCorrect(page: number = 1, size: number = 10) {
  const res = await axios.get('/essay/correct/list', { params: { page, size } });
  return res.data;
}

async function getEssayCorrect(essayId: string) {
  const res = await axios.get(`/essay/correct/${ essayId }`);
  return res.data;
}


export {
  putEssayCorrectTask,
  getEssayCorrectTask,
  listEssayCorrectTask,
  listEssayCorrect,
  getEssayCorrect
};