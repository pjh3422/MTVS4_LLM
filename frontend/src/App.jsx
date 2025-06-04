// frontend/src/App.jsx
import React, { useState } from "react";
import Navbar from "./components/Navbar";
import CardList from "./components/CardList";
import CardForm from "./components/CardForm";
import ReviewPage from "./components/ReviewPage";

function App() {
  const [page, setPage] = useState("cards");

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar currentPage={page} onNavigate={setPage} />
      <main className="flex-grow container mx-auto px-4 py-6">
        {page === "cards" && (
          <>
            <h1 className="text-2xl font-semibold mb-4">암기 카드 관리</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <CardForm />
              <CardList />
            </div>
          </>
        )}
        {page === "review" && <ReviewPage />}
      </main>
    </div>
  );
}

export default App;
