import React from "react";

const DiaryEdit = ({
  formData,
  setFormData,
  loading,
  handleUpdateDiary,
  setCurrentPage,
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

  return (
    <div className="flex-1 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg">
          <div className="p-6 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-t-lg">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold">✏️ 감정일기 수정</h2>
                <p className="mt-2 opacity-90">
                  일기를 수정하면 새로운 AI 응답을 받게 됩니다
                </p>
              </div>
              <button
                onClick={() => setCurrentPage("detail")}
                className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
              >
                취소
              </button>
            </div>
          </div>

          <div className="p-6">
            <div className="space-y-6">
              {/* 일기 내용 수정 */}
              <div>
                <label className="block text-lg font-medium mb-2 text-gray-800">
                  📝 일기 내용
                </label>
                <textarea
                  name="content"
                  value={formData.content}
                  onChange={handleChange}
                  placeholder="마음속 깊은 이야기를 자유롭게 써보세요..."
                  required
                  rows={10}
                  className="w-full p-4 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent bg-gray-50 hover:bg-gray-100 focus:bg-white text-lg leading-relaxed text-black"
                />
              </div>

              {/* 조건 설정 수정 */}
              <div className="p-4 bg-orange-50 rounded-lg border border-orange-100">
                <h3 className="text-lg font-bold mb-3 flex items-center text-orange-800">
                  <span className="mr-2">✨</span>
                  AI 응답 조건 설정
                </h3>

                <div className="space-y-3">
                  <div>
                    <label className="flex items-center mb-1 text-sm font-medium text-gray-700">
                      <span className="w-5 h-5 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs mr-2">
                        1
                      </span>
                      MBTI 맞춤 응원
                    </label>
                    <input
                      name="condition1"
                      value={formData.condition1}
                      onChange={handleChange}
                      placeholder="MBTI 태그를 선택하거나 직접 입력하세요"
                      className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent bg-white text-black mb-2"
                    />

                    {/* MBTI 태그 선택 (수정 페이지) */}
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
                            className="px-2 py-1 text-xs bg-orange-100 text-orange-700 rounded hover:bg-orange-200 transition-colors border border-orange-200"
                          >
                            {mbti}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="flex items-center mb-1 text-sm font-medium text-gray-700">
                      <span className="w-5 h-5 bg-green-500 text-white rounded-full flex items-center justify-center text-xs mr-2">
                        2
                      </span>
                      음악 추천
                    </label>
                    <input
                      name="condition2"
                      value={formData.condition2}
                      onChange={handleChange}
                      placeholder="장르 태그를 선택하거나 직접 입력하세요"
                      className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent bg-white text-black mb-2"
                    />

                    {/* 노래 장르 태그 선택 (수정 페이지) */}
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
              </div>

              {/* 수정 버튼 */}
              <div className="flex gap-3">
                <button
                  onClick={handleUpdateDiary}
                  disabled={loading || !formData.content.trim()}
                  className={`flex-1 py-3 rounded-lg font-bold text-lg transition-all duration-200 ${
                    loading || !formData.content.trim()
                      ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                      : "bg-gradient-to-r from-orange-500 to-red-500 text-white hover:from-orange-600 hover:to-red-600 transform hover:scale-105 shadow-lg hover:shadow-xl"
                  }`}
                >
                  {loading ? "수정 중..." : "💾 일기 수정하기"}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiaryEdit;
