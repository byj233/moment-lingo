import axios from 'axios';

async function listBooks() {
  const res = await axios.get('/book/list');
  return res.data;
}

async function getBook(bookId: number) {
  const res = await axios.get(`/book/${ bookId }`);
  return res.data;
}

async function listBookDetail(bookId: number, page: number, size: number) {
  const res = await axios.get(`/book/detail/${ bookId }?page=${ page }&size=${ size }`);
  return res.data;
}


export {
  listBooks,
  getBook,
  listBookDetail
};