import React from "react";
import { motion } from "framer-motion";

export default function RelatedConceptModal({ isOpen, relatedList, onSelect, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <motion.div
        className="bg-white rounded-2xl shadow-xl p-6 w-80 max-w-full"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        transition={{ duration: 0.2 }}
      >
        <h2 className="text-xl font-medium mb-4">연관 개념 생성</h2>
        <p className="text-gray-600 mb-4">다음 중 카드로 생성할 개념을 선택하세요.</p>
        <div className="space-y-2 mb-6">
          {relatedList.map((concept) => (
            <button
              key={concept}
              onClick={() => onSelect(concept)}
              className="w-full text-left px-4 py-2 bg-background hover:bg-gray-100 rounded-lg transition"
            >
              {concept}
            </button>
          ))}
        </div>
        <button
          onClick={onClose}
          className="mt-2 w-full bg-red-500 text-white py-2 rounded-lg hover:bg-red-600 transition"
        >
          닫기
        </button>
      </motion.div>
    </div>
  );
}
