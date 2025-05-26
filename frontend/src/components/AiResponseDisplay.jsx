import React from "react";
import EmotionScoreDisplay from "./EmotionScoreDisplay";

const AiResponseDisplay = ({
  loading,
  error,
  response,
  resetForm,
  setError,
}) => {
  return (
    <div className="w-1/2 h-full p-6 flex flex-col">
      <div className="h-full flex flex-col bg-white rounded-lg shadow-lg">
        {/* Loading State */}
        {loading && (
          <div className="h-full flex flex-col">
            <div className="p-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-700 rounded-full flex items-center justify-center">
                  🤔
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">
                    AI가 생각하고 있어요
                  </h2>
                  <p className="text-sm opacity-80 text-white">
                    당신의 마음을 깊이 이해하려고 해요
                  </p>
                </div>
              </div>
            </div>
            <div className="flex-1 p-6 flex flex-col justify-center items-center">
              <div className="text-center">
                <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-6 mx-auto animate-pulse">
                  <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                  </div>
                </div>
                <h3 className="text-2xl font-bold mb-4 text-gray-800">
                  마음을 읽어보고 있어요...
                </h3>
                <p className="text-gray-500 mt-6 text-sm">
                  잠깐만 기다려주세요. 좋은 답변을 준비하고 있어요! ✨
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="h-full flex flex-col">
            <div className="p-4 bg-gradient-to-r from-red-500 to-pink-600 text-white">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-red-700 rounded-full flex items-center justify-center">
                  😔
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">
                    문제가 발생했어요
                  </h2>
                </div>
              </div>
            </div>
            <div className="flex-1 p-6 flex flex-col justify-center">
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg mb-4">
                <div className="flex items-center">
                  <div className="w-6 h-6 bg-red-500 rounded-full flex items-center justify-center mr-3">
                    <span className="text-white text-sm">!</span>
                  </div>
                  <p className="text-red-800 text-black">{error}</p>
                </div>
              </div>
              <button
                onClick={() => setError(null)}
                className="self-start px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
              >
                🔄 다시 시도하기
              </button>
            </div>
          </div>
        )}

        {/* Success State */}
        {response && !error && !loading && (
          <div className="h-full flex flex-col">
            <div className="p-4 bg-gradient-to-r from-green-500 to-blue-500 text-white">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-green-700 rounded-full flex items-center justify-center">
                  🤖
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">
                    AI의 따뜻한 응답
                  </h2>
                  <p className="text-sm opacity-80 text-white">
                    {response.diary_idx
                      ? `저장 완료 (ID: ${response.diary_idx})`
                      : "당신의 마음에 공감하며 작성했어요"}
                  </p>
                </div>
              </div>
            </div>
            <div className="flex-1 p-4 flex flex-col min-h-0">
              <div className="flex-1 p-4 mb-4 bg-gray-50 rounded-lg border border-gray-200 overflow-auto">
                <pre className="text-base leading-relaxed whitespace-pre-wrap font-sans text-black">
                  {response.ai_response ||
                    response.content ||
                    "응답을 처리하는 중입니다..."}
                </pre>
              </div>

              {/* 각 조건별 응답 표시 */}
              {(response.condition1_response ||
                response.condition2_response ||
                response.condition3_response) && (
                <div className="mb-4 space-y-2">
                  {response.condition1_response && (
                    <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
                      <div className="text-sm font-medium text-blue-800 mb-1">
                        MBTI 맞춤 응원:
                      </div>
                      <div className="text-black">
                        {response.condition1_response}
                      </div>
                    </div>
                  )}
                  {response.condition2_response && (
                    <div className="p-3 bg-green-50 rounded-lg border border-green-100">
                      <div className="text-sm font-medium text-green-800 mb-1">
                        노래 추천:
                      </div>
                      <div className="text-black">
                        {response.condition2_response}
                      </div>
                    </div>
                  )}
                  {response.condition3_response && (
                    <div className="p-3 bg-purple-50 rounded-lg border border-purple-100">
                      <div className="text-sm font-medium text-purple-800 mb-1">
                        감정 상태 분석:
                      </div>
                      <EmotionScoreDisplay
                        scoreText={response.condition3_response}
                      />
                    </div>
                  )}
                  {response.condition4_response && (
                    <div className="p-3 bg-purple-50 rounded-lg border border-purple-100">
                      <div className="text-sm font-medium text-purple-800 mb-1">
                        감정 분석 코드:
                      </div>
                      <EmotionScoreDisplay
                        scoreText={response.condition4_response}
                      />
                    </div>
                  )}
                </div>
              )}

              <div className="space-y-2">
                {response.diary_idx && (
                  <div className="p-2 bg-green-100 border border-green-200 rounded-lg text-center">
                    <span className="text-green-800 font-medium">
                      ✅ 데이터베이스에 저장됨 (ID: {response.diary_idx})
                    </span>
                  </div>
                )}

                <button
                  onClick={resetForm}
                  className="w-full py-3 bg-gray-600 text-white rounded-lg font-bold hover:bg-gray-700 transition-colors"
                >
                  🆕 새로운 일기 쓰기
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Default State */}
        {!response && !error && !loading && (
          <div className="h-full flex flex-col">
            <div className="p-4 bg-gradient-to-r from-purple-500 to-pink-600 text-white">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-purple-700 rounded-full flex items-center justify-center">
                  🌟
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">
                    AI가 기다리고 있어요
                  </h2>
                  <p className="text-sm opacity-80 text-white">
                    당신의 이야기를 들려주세요
                  </p>
                </div>
              </div>
            </div>
            <div className="flex-1 p-6 flex flex-col justify-center items-center text-center">
              <div className="text-6xl mb-4">🌱</div>
              <h3 className="text-3xl font-bold mb-4 text-gray-800">
                마음을 나눠주세요
              </h3>
              <p className="text-lg text-gray-600 mb-6 leading-relaxed">
                왼쪽에 오늘의 감정을 솔직하게 적어주시면,
                <br />
                AI가 당신의 마음을 이해하고 따뜻한 위로를 전해드릴게요.
              </p>

              <div className="space-y-3 w-full max-w-sm">
                <div className="p-3 bg-gray-100 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-sm font-medium text-gray-700">
                      localhost:8080 연결됨
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AiResponseDisplay;
