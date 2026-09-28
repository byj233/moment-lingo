import axios from 'axios';

interface PatchMeReq {
  nickname: string;
  avatarUrl: string;
}


async function getMe() {
  const resp = await axios.get('/user/me');
  return resp.data;
}

async function patchMe(req: PatchMeReq) {
  const resp = await axios.patch('/user/me', req);
  return resp.data;
}

export {
  getMe,
  patchMe
};
