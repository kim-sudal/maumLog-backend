import React from "react";
import EmotionScoreDisplay from "./EmotionScoreDisplay";

const DiaryDetail = ({
  selectedDiary,
  goToEditPage,
  handleDeleteDiary,
  setCurrentPage,
}) => {
  if (!selectedDiary) return null;

  return (
    <div className="flex-1 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg">
          <div className="p-6 bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-t-lg">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold">📖 감정일기 상세보기</h2>
                {selectedDiary?.reg_date && (
                  <p className="mt-2 opacity-90">
                    {new Date(selectedDiary.reg_date).toLocaleDateString(
                      "ko-KR",
                      {
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      }
                    )}
                  </p>
                )}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => goToEditPage(selectedDiary)}
                  className="px-4 py-2 bg-white bg-opacity-20 text-white rounded-lg hover:bg-opacity-30 transition-colors"
                >
                  ✏️ 수정
                </button>
                <button
                  onClick={() => handleDeleteDiary(selectedDiary?.diary_idx)}
                  className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                >
                  🗑️ 삭제
                </button>
                <button
                  onClick={() => setCurrentPage("list")}
                  className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                >
                  📋 목록으로
                </button>
              </div>
            </div>
          </div>

          <div className="p-6 space-y-6">
            {/* 원본 일기 내용 */}
            <div>
              <h3 className="text-lg font-bold mb-3 text-gray-800">
                📝 나의 감정일기
              </h3>
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <pre className="whitespace-pre-wrap font-sans text-gray-800 leading-relaxed">
                  {selectedDiary.content}
                </pre>
              </div>
            </div>

            {/* AI 기본 응답 */}
            {selectedDiary.ai_response && (
              <div>
                <h3 className="text-lg font-bold mb-3 text-gray-800">
                  🤖 AI의 따뜻한 응답
                </h3>
                <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
                  <pre className="whitespace-pre-wrap font-sans text-gray-800 leading-relaxed">
                    {selectedDiary.ai_response}
                  </pre>
                </div>
              </div>
            )}

            {/* 조건별 AI 응답들 */}
            {(selectedDiary.condition1_response ||
              selectedDiary.condition2_response ||
              selectedDiary.condition3_response ||
              selectedDiary.condition4_response) && (
              <div>
                <h3 className="text-lg font-bold mb-3 text-gray-800">
                  🎯 맞춤 분석 결과
                </h3>
                <div className="space-y-3">
                  {selectedDiary.condition1_response && (
                    <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
                      <div className="text-sm font-medium text-blue-800 mb-2">
                        💡 MBTI 맞춤 응원:
                      </div>
                      <div className="text-gray-800">
                        {selectedDiary.condition1_response}
                      </div>
                    </div>
                  )}
                  {selectedDiary.condition2_response && (
                    <div className="p-4 bg-green-50 rounded-lg border border-green-100">
                      <div className="text-sm font-medium text-green-800 mb-2">
                        🎵 추천 노래:
                      </div>
                      <div className="text-gray-800">
                        {selectedDiary.condition2_response}
                      </div>
                    </div>
                  )}
                  {selectedDiary.condition3_response && (
                    <div className="p-4 bg-purple-50 rounded-lg border border-purple-100">
                      <div className="text-sm font-medium text-purple-800 mb-2">
                        📊 감정 상태 분석:
                      </div>
                      <EmotionScoreDisplay
                        scoreText={selectedDiary.condition3_response}
                      />
                    </div>
                  )}
                  {selectedDiary.condition4_response && (
                    <div className="p-4 bg-green-50 rounded-lg border border-green-100">
                      <div className="text-sm font-medium text-green-800 mb-2">
                        🎵 분석 감정:
                      </div>
                      <div className="text-gray-800">
                        {selectedDiary.condition4_response}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* 메타데이터 */}
            <div>
              <h3 className="text-lg font-bold mb-3 text-gray-800">
                ℹ️ 상세 정보
              </h3>
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-600">
                      일기 번호:
                    </span>
                    <span className="ml-2 text-gray-800">
                      {selectedDiary.diary_idx}
                    </span>
                  </div>
                  {selectedDiary.ai_model && (
                    <div>
                      <span className="font-medium text-gray-600">
                        AI 모델:
                      </span>
                      <span className="ml-2 text-gray-800">
                        {selectedDiary.ai_model || selectedDiary.model}
                      </span>
                    </div>
                  )}
                  <div>
                    <span className="font-medium text-gray-600">작성일:</span>
                    <span className="ml-2 text-gray-800">
                      {new Date(selectedDiary.reg_date).toLocaleString("ko-KR")}
                    </span>
                  </div>
                  {selectedDiary.update_date && (
                    <div>
                      <span className="font-medium text-gray-600">수정일:</span>
                      <span className="ml-2 text-gray-800">
                        {new Date(selectedDiary.update_date).toLocaleString(
                          "ko-KR"
                        )}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiaryDetail;