# backend/services/llm_service.py
from interfaces.llm_interface import ILLMService
from config.settings import LLMConfig

from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class LLMService(ILLMService):
    """LLM 기반 힌트/피드백 및 관련 개념/정의/심화 문제 생성 서비스"""

    def __init__(self):
        cfg: LLMConfig = LLMConfig()
        self.model = ChatOllama(
            model=cfg.model_name,
            temperature=cfg.temperature,
        )
        self.embedder = SentenceTransformer(cfg.embedder_name)
        self.similarity_threshold = cfg.similarity_threshold

    def generate_question(self, card: dict) -> dict:
        return {"question": f"'{card['concept']}'에 대해 설명해보세요."}

    def evaluate_answer(self, card: dict, user_answer: str) -> bool:
        correct_answer = card["answer"]
        vec_correct = self.embedder.encode([correct_answer])
        vec_user = self.embedder.encode([user_answer])
        sim_score = cosine_similarity(vec_correct, vec_user)[0][0]
        return bool(sim_score >= self.similarity_threshold)

    def generate_hint(self, concept: str, answer: str, stage: int, card_type: str) -> str:
        """
        단계별, 카드 타입별로 힌트를 생성
        """
        if card_type == "word":
            if stage == 3:
                template = PromptTemplate(
                    input_variables=["answer"],
                    template=(
                        "학생이 단어를 떠올릴 수 있도록, "
                        "정답 단어를 노출하지 않고 한두 문장으로 짧은 힌트를 제공해주세요.\n"
                        "정답: {answer}"
                    )
                )
            elif stage == 4:
                template = PromptTemplate(
                    input_variables=["answer"],
                    template=(
                        "학생이 단어를 확실히 기억할 수 있도록, "
                        "정답 단어를 노출하지 않고 최대 두 문장 이내로 구체적인 힌트를 제공해주세요.\n"
                        "정답: {answer}"
                    )
                )
            else:
                return ""
            chain: Runnable = template | self.model | StrOutputParser()
            return chain.invoke({"answer": answer}).strip()

        else:  # card_type == "concept"
            if stage in [2, 3]:
                template = PromptTemplate(
                    input_variables=["concept", "answer"],
                    template=(
                        "학생이 개념을 떠올릴 수 있도록, "
                        "정의(정답)를 노출하지 않고 한두 문장으로 짧은 힌트를 제공해주세요.\n"
                        "개념: {concept}\n"
                        "정의: {answer}"
                    )
                )
            elif stage == 4:
                template = PromptTemplate(
                    input_variables=["concept", "answer"],
                    template=(
                        "학생이 개념을 정확히 떠올릴 수 있도록, "
                        "정의(정답)를 노출하지 않고 한두 문장으로 구체적인 힌트를 제공해주세요.\n"
                        "개념: {concept}\n"
                        "정의: {answer}"
                    )
                )
            else:
                return ""
            chain: Runnable = template | self.model | StrOutputParser()
            return chain.invoke({"concept": concept, "answer": answer}).strip()

    def generate_feedback(self, card: dict, user_answer: str, is_correct: bool) -> str:
        correct_answer = card["answer"]
        if is_correct:
            feedback_prompt = PromptTemplate(
                input_variables=["correct_answer"],
                template=(
                    "학생이 정답을 맞혔습니다.\n"
                    "정답: {correct_answer}\n"
                    "간단히 칭찬해 주세요."
                )
            )
            chain_feedback: Runnable = feedback_prompt | self.model | StrOutputParser()
            return chain_feedback.invoke({"correct_answer": correct_answer}).strip()
        else:
            feedback_prompt = PromptTemplate(
                input_variables=["correct_answer", "user_answer"],
                template=(
                    "학생이 오답을 입력했습니다.\n"
                    "정답: {correct_answer}\n"
                    "사용자 답안: {user_answer}\n"
                    "정답을 직접 말하지 말고, 학생이 스스로 떠올릴 수 있도록 한두 문장으로 힌트를 제공해주세요."
                )
            )
            chain_feedback: Runnable = feedback_prompt | self.model | StrOutputParser()
            return chain_feedback.invoke({
                "correct_answer": correct_answer,
                "user_answer": user_answer
            }).strip()

    def generate_related_concepts(self, concept: str, k: int = 5) -> list[str]:
        prompt = PromptTemplate.from_template(
            """
다음 개념과 밀접하게 연관된 한국어 개념 {k}개를 ‘개념1, 개념2, ...’ 형태로 한 줄에 제시하세요.
개념: {concept}
"""
        )
        chain = prompt | self.model | StrOutputParser()
        raw = chain.invoke({"concept": concept, "k": k})
        return [c.strip() for c in raw.split(",") if c.strip()]

    def generate_concept_definition(self, concept: str) -> str:
        prompt = PromptTemplate.from_template(
            """
아래 개념을 한국어로 한두 문장으로 간결 · 정확하게 요약하세요.
개념: {concept}
"""
        )
        chain: Runnable = prompt | self.model | StrOutputParser()
        return chain.invoke({"concept": concept}).strip()

    def generate_advanced_questions(self, concept: str, n: int = 3) -> list[str]:
        """
        주어진 개념에 대해 심화 문제 n개를 한 줄에 하나씩 생성하여 리스트로 반환
        """
        prompt = PromptTemplate.from_template(
            """
주어진 개념과 관련된 심화 문제 {n}개를 한 줄에 하나씩 생성하세요.
개념: {concept}
출력 형식: 문제1, 문제2, ...
"""
        )
        chain: Runnable = prompt | self.model | StrOutputParser()
        raw = chain.invoke({"concept": concept, "n": n})
        return [q.strip() for q in raw.split(",") if q.strip()]
    
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
            """
            두 문자열을 임베딩한 뒤 코사인 유사도를 반환한다.
            반환값은 0.0~1.0 사이 실수.
            """
            embeddings = self.embedder.encode([text1, text2])
            score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

            return round(float(score), 4)
    
    # NEW : 의미 동등성 YES/NO 판정
    def is_equivalent(self, correct_answer: str, user_answer: str) -> bool:
        yesno_prompt = PromptTemplate.from_template(
            """
Determine whether the user's answer means exactly the same as the correct answer.

Correct Answer: {correct_answer}
User Answer: {user_answer}

If their meanings are not completely identical, respond NO.
Respond with one word only: YES or NO (uppercase).
"""
        )
        chain: Runnable = yesno_prompt | self.model | StrOutputParser()
        result = chain.invoke(
            {"correct_answer": correct_answer, "user_answer": user_answer}
        ).strip().upper()
        return result == "YES"