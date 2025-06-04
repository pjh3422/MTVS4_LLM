import React from "react";
import { BrowserRouter as Router, Routes, Route, NavLink } from "react-router-dom";
import ReviewPage from "./components/ReviewPage";
import CardManagementPage from "./components/CardManagementPage";

export default function App() {
  return (
    <Router>
      {/* 상단 내비게이션 */}
      <nav className="bg-white shadow-md mb-6">
        <div className="max-w-3xl mx-auto flex items-center justify-between px-6 py-4">
          <h1 className="text-2xl font-semibold text-primary">버디 봇</h1>
          <div className="flex space-x-6">
            <NavLink
              to="/review"
              className={({ isActive }) =>
                isActive
                  ? "text-primary border-b-2 border-primary pb-1 font-medium"
                  : "text-gray-600 hover:text-primary transition"
              }
            >
              복습하기
            </NavLink>
            <NavLink
              to="/manage"
              className={({ isActive }) =>
                isActive
                  ? "text-primary border-b-2 border-primary pb-1 font-medium"
                  : "text-gray-600 hover:text-primary transition"
              }
            >
              카드관리
            </NavLink>
          </div>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<ReviewPage />} />
        <Route path="/review" element={<ReviewPage />} />
        <Route path="/manage" element={<CardManagementPage />} />
      </Routes>
    </Router>
  );
}
