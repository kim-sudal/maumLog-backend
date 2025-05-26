import React, { useState, useEffect, useRef } from 'react';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';

function Home() {
    const [date, setDate] = useState(new Date());
    const diarySectionRef = useRef(null);

    // 샘플 일기 데이터 (실제 구현 시 API 연동 예정)
    const diaryEntries = [
        { date: '2024-05-15', content: '오늘은 친구들과 즐거운 하루를 보냈다.' },
        { date: '2024-05-16', content: '비가 와서 살짝 우울했지만 따뜻한 커피로 위로 받았다.' },
        { date: '2024-05-20', content: '마음로그 프로젝트 회의가 있었던 날!' },
    ];

    const handleVoiceDiary = () => {
        alert("🎙️ 음성 녹음을 시작합니다...\n(녹음된 내용은 ChatGPT를 통해 정리된 후 일기로 저장될 예정.)");

        // TODO:
        // 1. Web Speech API로 음성 인식 시작
        // 2. 인식된 텍스트를 OpenAI API에 전달해 자연스럽게 다듬기
        // 3. 가공된 결과를 선택한 날짜에 일기로 저장 (ex: setDiaryEntries or 서버 전송)
    };

    const scrollToDate = (targetDate) => {
        setDate(new Date(targetDate));
        diarySectionRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    return (
        <div className="min-h-screen bg-[#F8FAFC] flex flex-col items-center px-4 py-10">
            <h1 className="text-4xl font-bold text-[#1F2937] mb-4">마음로그 📝</h1>
            <p className="text-gray-600 text-lg mb-8">오늘의 감정을 AI와 함께 기록해보세요</p>

            <Calendar
                onChange={setDate}
                value={date}
                className="rounded-lg shadow-md p-4 bg-white mb-6"
            />

            <div ref={diarySectionRef} className="w-full max-w-2xl bg-white shadow rounded-lg p-6 mb-10 overflow-y-auto max-h-[300px]">
                <h2 className="text-xl font-semibold mb-4 text-[#1F2937]">일기 목록</h2>
                {diaryEntries.length > 0 ? (
                    diaryEntries.map((entry, idx) => (
                        <div key={idx} className="mb-6 cursor-pointer" onClick={() => scrollToDate(entry.date)}>
                            <p className="text-sm text-gray-400 mb-1">{entry.date}</p>
                            <p className="text-gray-700">{entry.content}</p>
                            <hr className="my-4" />
                        </div>
                    ))
                ) : (
                    <p className="text-gray-400">작성된 일기가 없습니다.</p>
                )}
            </div>

            <button
                onClick={handleVoiceDiary}
                className="bg-[#4ECDC4] hover:bg-[#3dc0b3] text-white font-semibold px-6 py-3 rounded-lg shadow-md transition"
            >
                새 일기 작성하기 (🎤 AI 음성 인식 & GPT 정리)
            </button>
        </div>
    );
}

export default Home;