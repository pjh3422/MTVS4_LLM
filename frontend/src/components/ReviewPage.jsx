// frontend/src/components/ReviewPage.jsx
import React, { useEffect, useState } from "react";
import { fetchDueCards, fetchHint, reviewCard, createCard } from "../services/api";
import { motion, AnimatePresence } from "framer-motion";
import RelatedConceptModal from "./RelatedConceptModal";

export default function ReviewPage() {
  const [dueCards, setDueCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [testMode, setTestMode] = useState(false);
  const [currentAnswer, setCurrentAnswer] = useState({});
  const [feedbacks, setFeedbacks] = useState({});
  const [submitted, setSubmitted] = useState({});
  const [retryMode, setRetryMode] = useState({});
  const [countdown, setCountdown] = useState({});
  const [loadingCard, setLoadingCard] = useState({});

  const [relatedList, setRelatedList] = useState([]);
  const [selectedCardId, setSelectedCardId] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const loadDueCards = async () => {
    setLoading(true);
    try {
      const data = await fetchDueCards(testMode);
      setDueCards(data);

      const initText = {},
        initFeedback = {},
        initSubmitted = {},
        initRetry = {},
        initCountdown = {},
        initLoading = {};

      data.forEach((c) => {
        initText[c.card_id] = "";
        initFeedback[c.card_id] = "";
        initSubmitted[c.card_id] = false;
        initRetry[c.card_id] = false;
        initCountdown[c.card_id] = 0;
        initLoading[c.card_id] = false;
        c.hint = c.hint || "";
      });

      setCurrentAnswer(initText);
      setFeedbacks(initFeedback);
      setSubmitted(initSubmitted);
      setRetryMode(initRetry);
      setCountdown(initCountdown);
      setLoadingCard(initLoading);

      data.forEach(async (card) => {
        const { card_id, card_type, stage } = card;
        const needHint =
          (card_type === "word" && [3, 4].includes(stage)) ||
          (card_type === "concept" && [2, 3, 4].includes(stage));

        if (needHint) {
          try {
            const hintText = await fetchHint(card_id);
            setDueCards((prev) =>
              prev.map((item) =>
                item.card_id === card_id ? { ...item, hint: hintText } : item
              )
            );
          } catch {
            // 실패 시 빈 문자열 유지
          }
        }
      });
    } catch {
      console.error("복습 카드 로드 실패");
    }
    setLoading(false);
  };

  useEffect(() => {
    loadDueCards();
  }, [testMode]);

  useEffect(() => {
    const intervals = [];
    Object.entries(countdown).forEach(([card_id, timeLeft]) => {
      if (timeLeft > 0) {
        const id = setInterval(() => {
          setCountdown((prev) => ({
            ...prev,
            [card_id]: prev[card_id] - 1
          }));
        }, 1000);
        intervals.push(id);
      } else if (timeLeft === 0 && !retryMode[card_id] && submitted[card_id]) {
        setRetryMode((prev) => ({ ...prev, [card_id]: true }));
        setSubmitted((prev) => ({ ...prev, [card_id]: false }));
      }
    });
    return () => intervals.forEach(clearInterval);
  }, [countdown, retryMode, submitted]);

  const handleChangeAnswer = (card_id, text) => {
    setCurrentAnswer((prev) => ({ ...prev, [card_id]: text }));
  };

  const handleSubmitAnswer = async (card) => {
    const id = card.card_id;
    if ((submitted[id] && !retryMode[id]) || countdown[id] > 0) return;

    setLoadingCard((prev) => ({ ...prev, [id]: true }));
    setSubmitted((prev) => ({ ...prev, [id]: true }));
    setFeedbacks((prev) => ({ ...prev, [id]: "확인 중..." }));

    try {
      const result = await reviewCard(id, currentAnswer[id], testMode, retryMode[id]);
      setFeedbacks((prev) => ({ ...prev, [id]: result.feedback }));

      // 4단계 정답 후 모달
      if (result.completed && result.related_concepts?.length > 0) {
        setRelatedList(result.related_concepts);
        setSelectedCardId(id);
        setIsModalOpen(true);
        return;
      }

      if (result.is_correct) {
        alert("✅ 정답입니다!");
        loadDueCards();
        return;
      }

      if (result.retry_allowed) {
        const wait = testMode ? 5 : 30;
        setCountdown((prev) => ({ ...prev, [id]: wait }));
        setSubmitted((prev) => ({ ...prev, [id]: false }));
        return;
      }

      alert("❌ 오답입니다. 단계가 1로 초기화됩니다.");
      loadDueCards();
    } catch {
      console.error("제출 오류");
    } finally {
      setLoadingCard((prev) => ({ ...prev, [id]: false }));
    }
  };

  const handleSelectRelated = async (concept) => {
    const newCard = await createCard({ concept, answer: "", card_type: "concept" });
    alert(`✅ '${concept}' 카드가 생성되었습니다!\n정의: ${newCard.answer}`);
    setIsModalOpen(false);
    setRelatedList([]);
    setSelectedCardId(null);
    loadDueCards();
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setRelatedList([]);
    setSelectedCardId(null);
  };

  const renderLoadingSkeleton = () => {
    const skeletons = [1, 2, 3];
    return (
      <div className="space-y-6">
        {skeletons.map((i) => (
          <div key={i} className="animate-pulse flex flex-col space-y-2">
            <div className="rounded-md bg-gray-300 h-6 w-3/5 mb-2"></div>
            <div className="rounded-md bg-gray-300 h-6 w-2/5 mb-4"></div>
            <div className="rounded-md bg-gray-300 h-5 w-full mb-2"></div>
            <div className="rounded-md bg-gray-200 h-8 w-full mb-2"></div>
            <div className="rounded-md bg-gray-300 h-8 w-32"></div>
          </div>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="p-4">
        <div className="flex items-center mb-6">
          <h1 className="text-2xl font-semibold flex-grow">복습하기</h1>
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={testMode}
              onChange={() => setTestMode(!testMode)}
              className="form-checkbox h-5 w-5 text-indigo-600"
            />
            <span className="text-sm">테스트 모드</span>
          </label>
        </div>
        {renderLoadingSkeleton()}
      </div>
    );
  }

  return (
    <div className="p-4">
      <div className="flex items-center mb-6">
        <h1 className="text-2xl font-semibold flex-grow">복습하기</h1>
        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={testMode}
            onChange={() => setTestMode(!testMode)}
            className="form-checkbox h-5 w-5 text-indigo-600"
          />
          <span className="text-sm">테스트 모드</span>
        </label>
      </div>

      {dueCards.length === 0 ? (
        <p className="text-center text-gray-500">현재 복습할 카드가 없습니다.</p>
      ) : (
        dueCards.map((card) => {
          const id = card.card_id;
          return (
            <motion.div
              key={id}
              className="bg-white p-6 rounded-lg shadow-md mb-6"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <p className="font-medium text-lg mb-2">문제: {card.concept}</p>
              <p className="text-gray-500 mb-3">
                {card.stage === 1 ? "" : card.hint || "힌트 로딩 중..."}
              </p>

              <input
                type="text"
                value={currentAnswer[id] || ""}
                onChange={(e) => handleChangeAnswer(id, e.target.value)}
                placeholder={
                  countdown[id] > 0
                    ? `대기 중: ${countdown[id]}초`
                    : retryMode[id]
                    ? "재시도하세요"
                    : "정답을 입력하세요"
                }
                disabled={(submitted[id] && !retryMode[id]) || countdown[id] > 0}
                className={`w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400 mb-3 ${
                  (submitted[id] && !retryMode[id]) || countdown[id] > 0
                    ? "bg-gray-100 cursor-not-allowed"
                    : ""
                }`}
              />

              <button
                onClick={() => handleSubmitAnswer(card)}
                disabled={(submitted[id] && !retryMode[id]) || countdown[id] > 0}
                className={`flex items-center justify-center ${
                  (submitted[id] && !retryMode[id]) || countdown[id] > 0
                    ? "bg-gray-400 cursor-not-allowed"
                    : "bg-indigo-600 hover:bg-indigo-700"
                } text-white py-2 px-6 rounded-md transition-colors duration-200`}
              >
                {loadingCard[id] ? (
                  <motion.div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : countdown[id] > 0 ? (
                  `대기 중 (${countdown[id]}초)`
                ) : submitted[id] && !retryMode[id] ? (
                  "제출 완료"
                ) : retryMode[id] ? (
                  "재시도"
                ) : (
                  "제출"
                )}
              </button>

              <AnimatePresence>
                {feedbacks[id] && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="mt-3"
                  >
                    <p className="text-base text-gray-700">피드백: {feedbacks[id]}</p>
                  </motion.div>
                )}
              </AnimatePresence>

              {!testMode && (
                <p className="text-xs text-gray-400 mt-2">
                  현재 단계: {card.stage} | 다음 복습:{" "}
                  {card.next_review
                    ? new Date(card.next_review).toLocaleString("ko-KR")
                    : "-"}
                </p>
              )}
            </motion.div>
          );
        })
      )}

      <RelatedConceptModal
        isOpen={isModalOpen}
        relatedList={relatedList}
        onSelect={handleSelectRelated}
        onClose={handleCloseModal}
      />
    </div>
  );
}
