import React, { useState, useEffect } from "react";

// 감정 스코어 파싱 함수
const parseEmotionScore = (scoreText) => {
  if (!scoreText) return null;

  // "7/10", "8 / 10", "5점/10점" 등의 패턴을 찾기
  const patterns = [
    /(\d+)\s*\/\s*(\d+)/, // 7/10 형태
    /(\d+)\s*점?\s*\/\s*(\d+)\s*점?/, // 7점/10점 형태
    /(\d+)\s*out\s*of\s*(\d+)/i, // 7 out of 10 형태
  ];

  for (const pattern of patterns) {
    const match = scoreText.match(pattern);
    if (match) {
      const score = parseInt(match[1]);
      const total = parseInt(match[2]);
      return { score, total, percentage: (score / total) * 100 };
    }
  }

  return null;
};

// 감정 스코어 컴포넌트
const EmotionScoreDisplay = ({ scoreText }) => {
  const [animatedPercentage, setAnimatedPercentage] = useState(0);
  const scoreData = parseEmotionScore(scoreText);

  useEffect(() => {
    if (scoreData) {
      const timer = setTimeout(() => {
        setAnimatedPercentage(scoreData.percentage);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [scoreData]);

  if (!scoreData) {
    return <div className="text-gray-600 text-sm">{scoreText}</div>;
  }

  const getColorClass = (percentage) => {
    if (percentage >= 80) return "bg-green-500";
    if (percentage >= 60) return "bg-yellow-500";
    if (percentage >= 40) return "bg-orange-500";
    return "bg-red-500";
  };

  const getEmoji = (percentage) => {
    if (percentage >= 80) return "😊";
    if (percentage >= 60) return "🙂";
    if (percentage >= 40) return "😐";
    return "😔";
  };

  return (
    <div className="p-4 bg-white rounded-lg border border-gray-200 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-medium text-gray-700">감정 상태</span>
        <span className="text-2xl">{getEmoji(scoreData.percentage)}</span>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex-1">
          <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
            <div
              className={`h-4 rounded-full transition-all duration-1000 ease-out ${getColorClass(
                scoreData.percentage
              )}`}
              style={{ width: `${animatedPercentage}%` }}
            >
              <div className="h-full bg-gradient-to-r from-transparent to-white opacity-30 rounded-full"></div>
            </div>
          </div>
        </div>
        <div className="text-lg font-bold text-gray-800 min-w-0">
          {scoreData.score}/{scoreData.total}
        </div>
      </div>

      <div className="mt-2 text-xs text-gray-500 text-center">
        {scoreData.percentage >= 80 && "매우 좋은 상태예요! ✨"}
        {scoreData.percentage >= 60 &&
          scoreData.percentage < 80 &&
          "괜찮은 상태네요 👍"}
        {scoreData.percentage >= 40 &&
          scoreData.percentage < 60 &&
          "조금 힘든 시간이군요 💪"}
        {scoreData.percentage < 40 && "많이 힘드시겠어요. 응원할게요 🤗"}
      </div>
    </div>
  );
};

export default EmotionScoreDisplay;
export { parseEmotionScore };
