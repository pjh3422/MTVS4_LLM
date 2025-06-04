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
    """LLM 기반 힌트/피드백 및 관련 개념/정의 생성 서비스"""

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

    def generate_hint(self, concept: str, answer: str, stage: int) -> str:
        """
        LLM에게 짧은 힌트 요청.
        - 정답(answer)을 모델에 알려주되, 힌트에는 정답을 포함하지 않도록 지시.
        """
        prompt_text = (
            f"당신은 친절한 튜터입니다.\n"
            f"개념: {concept}\n"
            f"정답(비공개): {answer}\n"
            f"현재 단계: {stage}\n"
            "학생이 정답 단어를 직접 알 수 없도록, "
            "한두 문장으로 간단히 떠올릴 수 있는 힌트를 제공해주세요."
        )
        hint_template = PromptTemplate(
            input_variables=["prompt_text"],
            template="{prompt_text}"
        )
        chain: Runnable = hint_template | self.model | StrOutputParser()
        return chain.invoke({"prompt_text": prompt_text})

    def generate_feedback(self, card: dict, user_answer: str, is_correct: bool) -> str:
        """
        사용자 답안이 맞았는지/틀렸는지에 따라 간단한 피드백 생성.
        - 틀릴 때는 user_answer 기반 힌트, 정답 노출 금지.
        """
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
            return chain_feedback.invoke({"correct_answer": correct_answer})
        else:
            feedback_prompt = PromptTemplate(
                input_variables=["correct_answer", "user_answer"],
                template=(
                    "학생이 오답을 입력했습니다.\n"
                    "정답: {correct_answer}\n"
                    "사용자 답안: {user_answer}\n"
                    "정답을 직접 말하지 말고, 학생이 스스로 떠올릴 수 있게 한두 문장으로 힌트를 제공해주세요."
                )
            )
            chain_feedback: Runnable = feedback_prompt | self.model | StrOutputParser()
            return chain_feedback.invoke({
                "correct_answer": correct_answer,
                "user_answer": user_answer
            })

    def generate_related_concepts(self, concept: str, k: int = 5) -> list[str]:
        """
        주어진 개념과 밀접하게 연관된 한국어 개념 k개를 쉼표로 구분하여 리스트로 반환.
        """
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
        """
        주어진 개념을 한두 문장으로 간결하게 설명한 정의를 반환.
        """
        prompt = PromptTemplate.from_template(
            """
아래 개념을 한국어로 한두 문장(불필요한 예시나 배경 설명 없이)으로 간결 · 정확하게 요약하세요.

개념: {concept}
"""
        )
        chain: Runnable = prompt | self.model | StrOutputParser()
        return chain.invoke({"concept": concept}).strip()
