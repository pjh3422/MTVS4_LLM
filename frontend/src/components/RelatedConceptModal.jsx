// frontend/src/components/RelatedConceptModal.jsx
import React from "react";
import { motion } from "framer-motion";
import PropTypes from "prop-types";

const backdropVariants = {
  visible: { opacity: 1 },
  hidden: { opacity: 0 },
};

const modalVariants = {
  hidden: { y: "-100vh", opacity: 0 },
  visible: { y: "0", opacity: 1, transition: { delay: 0.1 } },
};

export default function RelatedConceptModal({
  isOpen,
  relatedList,
  onSelect,
  onClose
}) {
  if (!isOpen) return null;

  return (
    <motion.div
      className="fixed top-0 left-0 w-full h-full bg-black bg-opacity-50 flex justify-center items-center z-50"
      variants={backdropVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.div
        className="bg-white rounded-lg p-6 w-80 max-w-full mx-4"
        variants={modalVariants}
      >
        <h2 className="text-xl font-semibold mb-4">🔗 연결 카드를 생성하시겠습니까?</h2>
        <p className="text-sm mb-4">연관된 개념들:</p>
        <ul className="max-h-60 overflow-auto space-y-2 mb-4">
          {relatedList.map((concept, idx) => (
            <li
              key={idx}
              className="p-2 border rounded hover:bg-indigo-100 cursor-pointer transition"
              onClick={() => onSelect(concept)}
            >
              {concept}
            </li>
          ))}
        </ul>
        <button
          onClick={onClose}
          className="mt-2 w-full bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium py-2 px-4 rounded transition"
        >
          아니요, 생략
        </button>
      </motion.div>
    </motion.div>
  );
}

RelatedConceptModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  relatedList: PropTypes.arrayOf(PropTypes.string).isRequired,
  onSelect: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired
};
