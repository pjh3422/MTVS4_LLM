// frontend/src/components/CardForm.jsx
import React, { useState } from "react";
import { createCard } from "../services/api";

function CardForm() {
  const [concept, setConcept] = useState("");
  const [answer, setAnswer] = useState("");
  const [cardType, setCardType] = useState("word");
  const [creating, setCreating] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!concept.trim() || !answer.trim()) {
      alert("개념과 정답을 입력해주세요.");
      return;
    }
    setCreating(true);
    try {
      await createCard({ concept, answer, card_type: cardType });
      setConcept("");
      setAnswer("");
      setCardType("word");
      window.location.reload();
    } catch (error) {
      console.error("카드 생성 실패:", error);
      alert("카드 생성 중 오류가 발생했습니다.");
    }
    setCreating(false);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-xl font-semibold mb-4">새 카드 생성</h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">개념</label>
          <input
            type="text"
            value={concept}
            onChange={(e) => setConcept(e.target.value)}
            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="예: Python 리스트"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">정답</label>
          <input
            type="text"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="예: 순서대로 데이터를 저장하는 자료구조"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">카드 유형</label>
          <select
            value={cardType}
            onChange={(e) => setCardType(e.target.value)}
            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="word">단어형</option>
            <option value="concept">개념형</option>
          </select>
        </div>
        <button
          type="submit"
          disabled={creating}
          className="w-full bg-indigo-600 text-white py-2 rounded-md hover:bg-indigo-700 transition-colors"
        >
          {creating ? "생성 중..." : "카드 생성"}
        </button>
      </form>
    </div>
  );
}

export default CardForm;
