import OSS from 'ali-oss';
import { getStsToken, presign } from '@/api/oss.ts';
import { errorHandler } from '@/api';
import { baseUrl } from '@/config';

const FILE_DIR = {
  TEMP: 'temp/',
  AVATAR: 'avatar/'
} as const;

type FILE_DIR_TYPE = typeof FILE_DIR[keyof typeof FILE_DIR]
type CallBack = (p: number) => void;

const OSS_CONFIG: OSS.Options = {
  accessKeyId: '',
  accessKeySecret: '',
  stsToken: '',
  region: 'oss-cn-hangzhou',
  bucket: 'moment-lingo',
  secure: true
};

async function upload(client: OSS, fileDir: FILE_DIR_TYPE, file: File, fileName: string, progress?: CallBack) {
  const uploadName = fileDir + fileName;
  await client.multipartUpload(uploadName, file, { progress });
  const resp = await presign(uploadName);
  return resp.data;
}

class Oss {
  static async uploadFile(fileDir: FILE_DIR_TYPE, file: File, fileName: string, progress?: CallBack) {
    let resp = await getStsToken();

    const client = new OSS({ ...OSS_CONFIG, ...resp.data });
    return await upload(client, fileDir, file, fileName, progress);
  }

  static async h5Upload(token: string, fileDir: FILE_DIR_TYPE, file: File, fileName: string, progress?: CallBack) {
    let resp = await fetch(`${ baseUrl }/oss/sts-token`, {
      method: 'GET',
      headers: { Authorization: `Bearer ${ token }` }
    }).then(resp => resp.json());

    if (resp.code !== 200) {
      await errorHandler(resp);
      return Promise.reject();
    }

    const client = new OSS({ ...OSS_CONFIG, ...resp.data });
    return upload(client, fileDir, file, fileName, progress);
  }
}


export { FILE_DIR, type FILE_DIR_TYPE, Oss };
