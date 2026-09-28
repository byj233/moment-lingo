import axios from 'axios';

interface SearchVocabularyReq {
  query: string;
  page: number;
  limit: number;
}

async function searchVocabulary(data: SearchVocabularyReq) {
  const resp = await axios.post('/search/vocabulary', data);
  return resp.data;
}

export {
  searchVocabulary
};