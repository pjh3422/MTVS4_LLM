// frontend/src/components/Navbar.jsx
import React from "react";

function Navbar({ currentPage, onNavigate }) {
  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        <h2 className="text-xl font-bold text-indigo-600">복습봇</h2>
        <div className="space-x-4">
          <button
            onClick={() => onNavigate("cards")}
            className={`px-3 py-1 rounded-md ${
              currentPage === "cards"
                ? "bg-indigo-600 text-white"
                : "text-indigo-600 hover:bg-indigo-100"
            }`}
          >
            카드 관리
          </button>
          <button
            onClick={() => onNavigate("review")}
            className={`px-3 py-1 rounded-md ${
              currentPage === "review"
                ? "bg-indigo-600 text-white"
                : "text-indigo-600 hover:bg-indigo-100"
            }`}
          >
            복습하기
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
