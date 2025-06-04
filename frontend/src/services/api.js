// frontend/src/services/api.js
import axios from "axios";

const API_URL = "http://localhost:8000";

export const fetchCards = async () => {
  const response = await axios.get(`${API_URL}/cards`);
  return response.data;
};

export const createCard = async (card) => {
  const response = await axios.post(`${API_URL}/cards`, card);
  return response.data;
};

export const updateCard = async (card_id, card) => {
  const response = await axios.put(`${API_URL}/cards/${card_id}`, card);
  return response.data;
};

export const deleteCard = async (card_id) => {
  await axios.delete(`${API_URL}/cards/${card_id}`);
};

export const fetchDueCards = async (testMode = false) => {
  const response = await axios.get(`${API_URL}/cards/due`, {
    params: { test: testMode }
  });
  return response.data;
};

// 신규: hint를 가져오는 함수
export const fetchHint = async (card_id) => {
  const response = await axios.get(`${API_URL}/cards/${card_id}/hint`);
  return response.data.hint;
};

export const reviewCard = async (card_id, user_answer, testMode = false, retry = false) => {
  const response = await axios.post(
    `${API_URL}/cards/${card_id}/review`,
    { user_answer },
    { params: { test: testMode, retry } }
  );
  return response.data;
};
