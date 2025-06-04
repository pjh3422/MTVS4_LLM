// frontend/src/components/CardList.jsx
import React, { useEffect, useState } from "react";
import { fetchCards, deleteCard } from "../services/api";

function CardList() {
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAnswerMap, setShowAnswerMap] = useState({});

  const loadCards = async () => {
    setLoading(true);
    try {
      const data = await fetchCards();
      setCards(data);
      const initialMap = {};
      data.forEach((c) => {
        initialMap[c.card_id] = false;
      });
      setShowAnswerMap(initialMap);
    } catch (error) {
      console.error("카드 불러오기 실패:", error);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadCards();
  }, []);

  const handleDelete = async (card_id) => {
    if (window.confirm("정말 삭제하시겠습니까?")) {
      await deleteCard(card_id);
      loadCards();
    }
  };

  const toggleAnswer = (card_id) => {
    setShowAnswerMap((prev) => ({
      ...prev,
      [card_id]: !prev[card_id]
    }));
  };

  if (loading) {
    return <p>로딩 중...</p>;
  }

  return (
    <div>
      <h3 className="text-xl font-semibold mb-3">기존 카드 목록</h3>
      {cards.length === 0 ? (
        <p>등록된 카드가 없습니다.</p>
      ) : (
        <ul className="space-y-4">
          {cards.map((card) => (
            <li
              key={card.card_id}
              className="bg-white p-4 rounded-lg shadow-sm transition-shadow duration-200 hover:shadow-md"
            >
              <div className="flex justify-between items-start">
                <div className="flex-grow">
                  <p className="font-medium">{card.concept}</p>
                  {showAnswerMap[card.card_id] && (
                    <p className="text-sm text-gray-500 mt-1">정답: {card.answer}</p>
                  )}
                  <button
                    onClick={() => toggleAnswer(card.card_id)}
                    className="text-indigo-600 hover:underline text-sm mt-1"
                  >
                    {showAnswerMap[card.card_id] ? "정답 숨기기" : "정답 보기"}
                  </button>
                  <p className="text-xs text-gray-400 mt-1">
                    단계: {card.stage} | 다음 복습:{" "}
                    {card.next_review
                      ? new Date(card.next_review).toLocaleString("ko-KR")
                      : "-"}
                  </p>
                </div>
                <button
                  onClick={() => handleDelete(card.card_id)}
                  className="text-red-500 hover:text-red-700 text-sm ml-4"
                >
                  삭제
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default CardList;
