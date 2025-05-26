import React from "react";
import { parseEmotionScore } from "./EmotionScoreDisplay";

const DiaryList = ({
  diaries,
  listLoading,
  listError,
  totalCount,
  page,
  pageSize,
  loadDiaries,
  loadDiaryDetail,
  goToEditPage,
  handleDeleteDiary,
  setCurrentPage,
}) => {
  if (listLoading) {
    return (
      <div className="flex-1 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg">
            <div className="p-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-t-lg">
              <h2 className="text-2xl font-bold">📋 나의 감정일기</h2>
              <p className="mt-2 opacity-90">
                지금까지 작성한 감정일기들을 확인해보세요
              </p>
            </div>
            <div className="p-6">
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                <p className="mt-4 text-gray-600">
                  일기 목록을 불러오고 있습니다...
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (listError) {
    return (
      <div className="flex-1 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg">
            <div className="p-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-t-lg">
              <h2 className="text-2xl font-bold">📋 나의 감정일기</h2>
              <p className="mt-2 opacity-90">
                지금까지 작성한 감정일기들을 확인해보세요
              </p>
            </div>
            <div className="p-6">
              <div className="text-center py-8">
                <div className="text-red-600 mb-4">❌ {listError}</div>
                <button
                  onClick={() => loadDiaries()}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                >
                  다시 시도
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg">
          <div className="p-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-t-lg">
            <h2 className="text-2xl font-bold">📋 나의 감정일기</h2>
            <p className="mt-2 opacity-90">
              지금까지 작성한 감정일기들을 확인해보세요
            </p>
          </div>

          <div className="p-6">
            {diaries.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📝</div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">
                  아직 작성한 일기가 없어요
                </h3>
                <p className="text-gray-600 mb-6">
                  첫 번째 감정일기를 작성해보세요!
                </p>
                <button
                  onClick={() => setCurrentPage("write")}
                  className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 font-medium"
                >
                  ✏️ 일기 쓰러 가기
                </button>
              </div>
            ) : (
              <>
                <div className="mb-6">
                  <p className="text-gray-600">
                    총 {totalCount}개의 일기 • 페이지 {page}
                  </p>
                </div>

                <div className="grid gap-4">
                  {diaries.map((diary) => (
                    <div
                      key={diary.diary_idx}
                      className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                    >
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex-1">
                          <div className="text-sm text-gray-500 mb-1">
                            {new Date(diary.reg_date).toLocaleDateString(
                              "ko-KR",
                              {
                                year: "numeric",
                                month: "long",
                                day: "numeric",
                                hour: "2-digit",
                                minute: "2-digit",
                              }
                            )}
                          </div>
                          <div className="text-gray-800 line-clamp-3 mb-2">
                            {diary.content?.substring(0, 150)}
                            {(diary.content?.length || 0) > 150 ? "..." : ""}
                          </div>
                          {diary.ai_response && (
                            <div className="text-sm text-blue-600 bg-blue-50 p-2 rounded border border-blue-100">
                              💬 AI: {diary.ai_response?.substring(0, 100)}
                              {(diary.ai_response?.length || 0) > 100
                                ? "..."
                                : ""}
                            </div>
                          )}

                          {/* 조건들 표시 */}
                          <div className="mt-2 flex flex-wrap gap-1">
                            {diary.condition1 && (
                              <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                                MBTI 응원
                              </span>
                            )}
                            {diary.condition2 && (
                              <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                                노래 추천
                              </span>
                            )}
                            {diary.condition3_response && (
                              <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
                                감정 스코어:{" "}
                                {parseEmotionScore(diary.condition3_response)
                                  ?.score || "?"}
                                /10
                              </span>
                            )}
                            {diary.condition4 && (
                              <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                                감정 코드
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="flex gap-2 ml-4">
                          <button
                            onClick={() => loadDiaryDetail(diary.diary_idx)}
                            className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                          >
                            상세보기
                          </button>
                          <button
                            onClick={() => goToEditPage(diary)}
                            className="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600"
                          >
                            수정
                          </button>
                          <button
                            onClick={() => handleDeleteDiary(diary.diary_idx)}
                            className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600"
                          >
                            삭제
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* 페이지네이션 */}
                {totalCount > pageSize && (
                  <div className="mt-6 flex justify-center gap-2">
                    <button
                      onClick={() => loadDiaries(page - 1)}
                      disabled={page <= 1}
                      className="px-3 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      이전
                    </button>
                    <span className="px-4 py-2 text-sm font-medium">
                      {page} / {Math.ceil(totalCount / pageSize)}
                    </span>
                    <button
                      onClick={() => loadDiaries(page + 1)}
                      disabled={page >= Math.ceil(totalCount / pageSize)}
                      className="px-3 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      다음
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiaryList;
