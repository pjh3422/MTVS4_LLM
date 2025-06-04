import React, { useEffect, useState } from "react";
import {
  fetchDueCards,
  fetchHint,
  reviewCard,
  createCard,
  getWebhook,
  setWebhook,
} from "../services/api";
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

  const [webhookUrl, setWebhookUrl] = useState("");
  const [showSaveConfirm, setShowSaveConfirm] = useState(false);

  // 카드 로드
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
            // 힌트 로딩 실패 시 무시
          }
        }
      });
    } catch {
      console.error("복습 카드 로드 실패");
    }
    setLoading(false);
  };

  // 최초 로드: 카드 + Webhook
  useEffect(() => {
    loadDueCards();
    (async () => {
      try {
        const url = await getWebhook();
        setWebhookUrl(url);
      } catch {
        // 무시
      }
    })();
  }, [testMode]);

  // 카운트다운 로직
  useEffect(() => {
    const intervals = [];
    Object.entries(countdown).forEach(([card_id, timeLeft]) => {
      if (timeLeft > 0) {
        const id = setInterval(() => {
          setCountdown((prev) => ({
            ...prev,
            [card_id]: prev[card_id] - 1,
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
      const result = await reviewCard(
        id,
        currentAnswer[id],
        testMode,
        retryMode[id]
      );
      setFeedbacks((prev) => ({ ...prev, [id]: result.feedback }));

      if (result.completed && result.related_concepts?.length > 0) {
        setRelatedList(result.related_concepts);
        setSelectedCardId(id);
        setIsModalOpen(true);
        return;
      }

      if (result.is_correct) {
        setTimeout(() => alert("✅ 정답입니다!"), 50);
        loadDueCards();
        return;
      }

      if (result.retry_allowed) {
        const wait = testMode ? 5 : 30;
        setCountdown((prev) => ({ ...prev, [id]: wait }));
        setSubmitted((prev) => ({ ...prev, [id]: false }));
        return;
      }

      setTimeout(() => alert("❌ 오답입니다. 단계가 1로 초기화됩니다."), 50);
      loadDueCards();
    } catch {
      console.error("제출 오류");
    } finally {
      setLoadingCard((prev) => ({ ...prev, [id]: false }));
    }
  };

  const handleSelectRelated = async (concept) => {
    const newCard = await createCard({
      concept,
      answer: "",
      card_type: "concept",
    });
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

  const saveWebhook = async () => {
    try {
      await setWebhook(webhookUrl);
      setShowSaveConfirm(true);
      setTimeout(() => setShowSaveConfirm(false), 2000);
    } catch {
      console.error("Webhook 저장 실패");
    }
  };

  // 로딩 스켈레톤
  const renderLoadingSkeleton = () => {
    return (
      <div className="space-y-6 mt-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="h-6 bg-gray-300 rounded-lg w-2/5 mb-2"></div>
            <div className="h-5 bg-gray-300 rounded-lg w-3/4 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded-lg w-full mb-4"></div>
          </div>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="p-6 max-w-3xl mx-auto">
        {/* 헤더 */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-semibold text-primary">복습하기</h1>
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={testMode}
              onChange={() => setTestMode(!testMode)}
              className="form-checkbox h-5 w-5 text-primary"
            />
            <span className="text-sm">테스트 모드</span>
          </label>
        </div>

        {/* Webhook 설정 카드 */}
        <motion.div
          className="card-container mb-6"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <p className="font-medium mb-2">Discord Webhook 설정</p>
          <div className="flex flex-col sm:flex-row sm:space-x-4">
            <input
              type="text"
              value={webhookUrl}
              onChange={(e) => setWebhookUrl(e.target.value)}
              placeholder="Webhook URL 입력"
              className="input-field mb-3 sm:mb-0"
            />
            <button onClick={saveWebhook} className="button-primary">
              저장
            </button>
          </div>
          <AnimatePresence>
            {showSaveConfirm && (
              <motion.p
                className="mt-2 text-sm text-green-600"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                Webhook URL이 저장되었습니다.
              </motion.p>
            )}
          </AnimatePresence>
        </motion.div>

        {renderLoadingSkeleton()}
      </div>
    );
  }

  return (
    <div className="p-6 max-w-3xl mx-auto">
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-semibold text-primary">복습하기</h1>
        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={testMode}
            onChange={() => setTestMode(!testMode)}
            className="form-checkbox h-5 w-5 text-primary"
          />
          <span className="text-sm">테스트 모드</span>
        </label>
      </div>

      {/* Webhook 설정 카드 */}
      <motion.div
        className="card-container mb-6"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <p className="font-medium mb-2">Discord Webhook 설정</p>
        <div className="flex flex-col sm:flex-row sm:space-x-4">
          <input
            type="text"
            value={webhookUrl}
            onChange={(e) => setWebhookUrl(e.target.value)}
            placeholder="Webhook URL 입력"
            className="input-field mb-3 sm:mb-0"
          />
          <button onClick={saveWebhook} className="button-primary">
            저장
          </button>
        </div>
        <AnimatePresence>
          {showSaveConfirm && (
            <motion.p
              className="mt-2 text-sm text-green-600"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              Webhook URL이 저장되었습니다.
            </motion.p>
          )}
        </AnimatePresence>
      </motion.div>

      {/* 복습 카드 목록 */}
      {dueCards.length === 0 ? (
        <p className="text-center text-gray-500">현재 복습할 카드가 없습니다.</p>
      ) : (
        dueCards.map((card) => {
          const id = card.card_id;
          return (
            <motion.div
              key={id}
              className="card-container mb-6"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <p className="font-semibold text-lg mb-2">문제: {card.concept}</p>
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
                className="input-field mb-4"
              />

              <button
                onClick={() => handleSubmitAnswer(card)}
                disabled={(submitted[id] && !retryMode[id]) || countdown[id] > 0}
                className={`flex items-center justify-center ${
                  (submitted[id] && !retryMode[id]) || countdown[id] > 0
                    ? "bg-gray-300 cursor-not-allowed"
                    : "button-primary"
                }`}
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
