import axios from 'axios';

async function getDetailVocabulary(vocabularyId: string) {
  const resp = await axios.get(`/vocabulary/detail/${ vocabularyId }`);
  return resp.data;
}

async function getBriefVocabulary(vocabularyId: string) {
  const resp = await axios.get(`/vocabulary/brief/${ vocabularyId }`);
  return resp.data;
}

async function getVocabulary(vocabulary: string) {
  const resp = await axios.get(`/vocabulary/${ vocabulary }`);
  return resp.data;
}


export {
  getDetailVocabulary,
  getBriefVocabulary,
  getVocabulary
};