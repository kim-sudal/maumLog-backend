import React from "react";

const NavigationBar = ({ currentPage, setCurrentPage, resetForm }) => {
  const handleWriteClick = () => {
    setCurrentPage("write");
    resetForm();
  };

  return (
    <div className="px-8 py-4 bg-white border-b border-gray-200">
      <div className="flex gap-4">
        <button
          onClick={handleWriteClick}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            currentPage === "write"
              ? "bg-blue-500 text-white"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
        >
          ✏️ 일기 쓰기
        </button>
        <button
          onClick={() => setCurrentPage("list")}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            currentPage === "list"
              ? "bg-blue-500 text-white"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
        >
          📋 일기 목록
        </button>
      </div>
    </div>
  );
};

export default NavigationBar;