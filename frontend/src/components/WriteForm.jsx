import React from "react";

const WriteForm = ({
  formData,
  setFormData,
  loading,
  handleGetResponse,
  handleSaveDiary,
  response,
}) => {
  const handleChange = (e) => {
    const { name, value } = e.target;
    // condition3는 항상 "감정스코어줘"로 고정
    if (name === "condition3") return;

    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const activeConditions = [
    formData.condition1 && { label: formData.condition1, color: "primary" },
    formData.condition2 && { label: formData.condition2, color: "success" },
    formData.condition3 && { label: "감정 스코어 분석", color: "secondary" },
    formData.condition4 && { label: "감정 코드 선정", color: "secondary" },
  ].filter(Boolean);

  return (
    <div className="w-1/2 h-full p-6 flex flex-col">
      <div className="h-full flex flex-col bg-white rounded-lg shadow-lg">
        {/* Header */}
        <div className="p-4 bg-gradient-to-r from-orange-500 to-orange-600 text-white">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-orange-700 rounded-full flex items-center justify-center">
              ✏️
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">감정일기 작성</h2>
              <p className="text-sm opacity-80 text-white">
                오늘의 마음을 자유롭게 적어보세요
              </p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 p-4 flex flex-col min-h-0">
          <div className="h-full flex flex-col">
            {/* 일기 내용 */}
            <div className="flex-1 mb-4">
              <h3 className="text-lg font-medium mb-2 text-black">
                📝 오늘은 어떤 하루였나요?
              </h3>
              <textarea
                name="content"
                value={formData.content}
                onChange={handleChange}
                placeholder="마음속 깊은 이야기를 자유롭게 써보세요..."
                required
                className="w-full h-full p-4 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50 hover:bg-gray-100 focus:bg-white text-lg leading-relaxed text-black"
              />
            </div>

            {/* 조건 설정 */}
            <div className="p-4 mb-4 bg-blue-50 rounded-lg border border-blue-100">
              <h3 className="text-lg font-bold mb-3 flex items-center text-blue-800">
                <span className="mr-2">✨</span>
                AI 응답 조건 설정
              </h3>

              <div className="space-y-3">
                <div>
                  {/* MBTI 태그 선택 */}
                  <div className="mt-2">
                    <p className="text-xs text-gray-600 mb-2">
                      💡 MBTI별 맞춤 응원:
                    </p>
                    <div className="grid grid-cols-4 gap-2">
                      {[
                        "INTJ",
                        "INTP",
                        "ENTJ",
                        "ENTP",
                        "INFJ",
                        "INFP",
                        "ENFJ",
                        "ENFP",
                        "ISTJ",
                        "ISFJ",
                        "ESTJ",
                        "ESFJ",
                        "ISTP",
                        "ISFP",
                        "ESTP",
                        "ESFP",
                      ].map((mbti) => (
                        <button
                          key={mbti}
                          type="button"
                          onClick={() =>
                            setFormData((prev) => ({
                              ...prev,
                              condition1: `#maum ${mbti} 대로 응원 한마디 말해줘`,
                            }))
                          }
                          className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors border border-blue-200"
                        >
                          {mbti}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                <div>
                  {/* 노래 장르 태그 선택 */}
                  <div className="mt-2">
                    <p className="text-xs text-gray-600 mb-2">
                      🎵 음악 장르별 노래 추천:
                    </p>
                    <div className="grid grid-cols-3 gap-2">
                      {[
                        "K-POP (한국 대중음악)",
                        "J-POP (일본 대중음악)",
                        "Pop (영미권 대중음악)",
                        "Electronic (유럽 일렉트로닉 포함)",
                        "OST (영화·드라마 삽입곡)",
                        "Latin (레게톤, 살사 등 라틴 음악)",
                      ].map((genre) => (
                        <button
                          key={genre}
                          type="button"
                          onClick={() =>
                            setFormData((prev) => ({
                              ...prev,
                              condition2: `${genre} 장르 노래 추천해줘`,
                            }))
                          }
                          className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors border border-green-200"
                        >
                          {genre}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* 조건 미리보기 */}
              {activeConditions.length > 0 && (
                <div className="mt-3 p-3 bg-white rounded-md border border-gray-200">
                  <p className="text-xs font-bold mb-2 text-gray-600">
                    ✨ 설정된 조건들:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {activeConditions.map((condition, index) => (
                      <span
                        key={index}
                        className={`px-2 py-1 text-xs rounded-full border ${
                          condition.color === "primary"
                            ? "bg-blue-100 text-blue-800 border-blue-300"
                            : condition.color === "success"
                            ? "bg-green-100 text-green-800 border-green-300"
                            : "bg-purple-100 text-purple-800 border-purple-300"
                        }`}
                      >
                        {condition.label}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Buttons */}
            <div className="space-y-3">
              <button
                onClick={handleGetResponse}
                disabled={loading || !formData.content.trim()}
                className={`w-full py-3 rounded-lg font-bold text-lg transition-all duration-200 ${
                  loading || !formData.content.trim()
                    ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                    : "bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700 transform hover:scale-105 shadow-lg hover:shadow-xl"
                }`}
              >
                {loading ? "💭 AI가 생각중..." : "💕 AI와 대화하기"}
              </button>

              {response && (
                <button
                  onClick={handleSaveDiary}
                  disabled={loading}
                  className={`w-full py-3 rounded-lg font-bold text-lg transition-all duration-200 ${
                    loading
                      ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                      : "bg-gradient-to-r from-yellow-500 to-orange-600 text-white hover:from-yellow-600 hover:to-orange-700 transform hover:scale-105 shadow-lg hover:shadow-xl"
                  }`}
                >
                  💾 현재 응답 저장하기
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WriteForm;