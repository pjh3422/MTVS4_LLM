// frontend/src/components/CardManagementPage.jsx

import React, { useEffect, useState } from "react";
import { fetchCards, createCard, updateCard, deleteCard } from "../services/api";
import { motion, AnimatePresence } from "framer-motion";

// 'word'와 'concept'을 한글로 매핑하는 헬퍼 함수
const mapTypeToKorean = (type) => {
  if (type === "word") return "단어";
  if (type === "concept") return "개념";
  return type;
};

export default function CardManagementPage() {
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({ concept: "", answer: "", card_type: "word" });
  const [editingId, setEditingId] = useState(null);
  const [editData, setEditData] = useState({ concept: "", answer: "", card_type: "" });
  const [showSaveConfirm, setShowSaveConfirm] = useState(false);
  const [revealAnswerMap, setRevealAnswerMap] = useState({}); // 카드별 정답 보이기 상태

  const loadCards = async () => {
    setLoading(true);
    try {
      const data = await fetchCards();
      setCards(data);
      // 초기화: 모든 카드 정답 감춤
      const initReveal = {};
      data.forEach((c) => {
        initReveal[c.card_id] = false;
      });
      setRevealAnswerMap(initReveal);
    } catch {
      console.error("카드 로드 실패");
    }
    setLoading(false);
  };

  useEffect(() => {
    loadCards();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleCreate = async () => {
    if (!formData.concept.trim()) return;
    try {
      await createCard(formData);
      setFormData({ concept: "", answer: "", card_type: "word" });
      setShowSaveConfirm(true);
      setTimeout(() => setShowSaveConfirm(false), 2000);
      loadCards();
    } catch {
      console.error("카드 생성 실패");
    }
  };

  const startEdit = (card) => {
    setEditingId(card.card_id);
    setEditData({ concept: card.concept, answer: card.answer, card_type: card.card_type });
  };

  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditData((prev) => ({ ...prev, [name]: value }));
  };

  const handleUpdate = async (id) => {
    try {
      await updateCard(id, editData);
      setEditingId(null);
      setShowSaveConfirm(true);
      setTimeout(() => setShowSaveConfirm(false), 2000);
      loadCards();
    } catch {
      console.error("카드 수정 실패");
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteCard(id);
      loadCards();
    } catch {
      console.error("카드 삭제 실패");
    }
  };

  const toggleReveal = (card_id) => {
    setRevealAnswerMap((prev) => ({
      ...prev,
      [card_id]: !prev[card_id],
    }));
  };

  const renderSkeleton = () => (
    <div className="space-y-4 mt-4">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="animate-pulse bg-gray-200 h-28 rounded-2xl" />
      ))}
    </div>
  );

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-3xl font-semibold text-primary mb-6">카드 관리</h1>

      {/* 카드 생성 폼 */}
      <motion.div
        className="card-container mb-8"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <p className="font-medium mb-4">새 카드 생성</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <input
            type="text"
            name="concept"
            value={formData.concept}
            onChange={handleInputChange}
            placeholder="개념/단어"
            className="input-field"
          />
          <input
            type="text"
            name="answer"
            value={formData.answer}
            onChange={handleInputChange}
            placeholder="정답"
            className="input-field"
          />
          <select
            name="card_type"
            value={formData.card_type}
            onChange={handleInputChange}
            className="input-field"
          >
            <option value="word">단어</option>
            <option value="concept">개념</option>
          </select>
          <button onClick={handleCreate} className="button-primary">
            저장
          </button>
        </div>
        <AnimatePresence>
          {showSaveConfirm && (
            <motion.p
              className="mt-3 text-sm text-green-600"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              카드가 저장되었습니다.
            </motion.p>
          )}
        </AnimatePresence>
      </motion.div>

      {/* 카드 목록 */}
      {loading
        ? renderSkeleton()
        : cards.map((card) => {
            const isEditing = editingId === card.card_id;
            const revealed = revealAnswerMap[card.card_id];
            return (
              <motion.div
                key={card.card_id}
                className="card-container mb-6"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                {isEditing ? (
                  <>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                      <input
                        type="text"
                        name="concept"
                        value={editData.concept}
                        onChange={handleEditChange}
                        className="input-field"
                      />
                      <input
                        type="text"
                        name="answer"
                        value={editData.answer}
                        onChange={handleEditChange}
                        className="input-field"
                      />
                      <select
                        name="card_type"
                        value={editData.card_type}
                        onChange={handleEditChange}
                        className="input-field"
                      >
                        <option value="word">Word</option>
                        <option value="concept">Concept</option>
                      </select>
                      <button
                        onClick={() => handleUpdate(card.card_id)}
                        className="bg-green-600 text-white rounded-lg px-6 py-2 hover:bg-green-700 transition"
                      >
                        저장
                      </button>
                    </div>
                    <button
                      onClick={() => setEditingId(null)}
                      className="text-sm text-gray-500 hover:underline"
                    >
                      취소
                    </button>
                  </>
                ) : (
                  <>
                    <p className="font-medium text-lg mb-1">문제: {card.concept}</p>
                    <div className="flex items-center mb-2 space-x-2">
                      <button
                        onClick={() => toggleReveal(card.card_id)}
                        className="text-sm text-primary hover:underline"
                      >
                        {revealed ? "정답 숨기기" : "정답 보기"}
                      </button>
                      {revealed && (
                        <span className="text-gray-700 font-medium">
                          {card.answer}
                        </span>
                      )}
                    </div>
                    {/* card_type을 한글로 변환하여 출력 */}
                    <p className="text-xs text-gray-400 mb-1">
                      타입: {mapTypeToKorean(card.card_type)} | 단계: {card.stage}
                    </p>
                    <p className="text-xs text-gray-400 mb-4">
                      다음 복습:{" "}
                      {card.next_review
                        ? new Date(card.next_review).toLocaleString("ko-KR")
                        : "-"}
                    </p>
                    <div className="flex space-x-4">
                      <button
                        onClick={() => startEdit(card)}
                        className="text-primary hover:underline text-sm"
                      >
                        수정
                      </button>
                      <button
                        onClick={() => handleDelete(card.card_id)}
                        className="text-red-500 hover:underline text-sm"
                      >
                        삭제
                      </button>
                    </div>
                  </>
                )}
              </motion.div>
            );
          })}
    </div>
  );
}
