import axios from 'axios';

interface PutUploadTaskReq {
  taskId?: string;
  fileUrl?: string;
}

async function getStsToken() {
  const resp = await axios.get('/oss/sts-token');
  return resp.data;
}

async function presign(object: string) {
  const resp = await axios.get(`/oss/presign?objectName=${object}`);
  return resp.data;
}

async function putUploadTask(req: PutUploadTaskReq) {
  const resp = await axios.post('/oss/upload/task', req);
  return resp.data;
}

async function getUploadTask(taskId: string) {
  const resp = await axios.get(`/oss/upload/task/${taskId}`);
  return resp.data;
}

export {
  getStsToken,
  presign,
  putUploadTask,
  getUploadTask
};