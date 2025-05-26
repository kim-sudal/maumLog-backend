import React, { useState, useEffect } from "react";
import NavigationBar from "./NavigationBar";
import WriteForm from "./WriteForm";
import AiResponseDisplay from "./AiResponseDisplay";
import DiaryList from "./DiaryList";
import DiaryDetail from "./DiaryDetail";
import DiaryEdit from "./DiaryEdit";

function EmotionalDiary() {
  const [currentPage, setCurrentPage] = useState("write"); // 'write', 'list', 'detail', 'edit'
  const [currentUser] = useState(1); // 임시 사용자 ID
  const [selectedDiary, setSelectedDiary] = useState(null);

  // Write page states
  const [formData, setFormData] = useState({
    content: "",
    condition1: "",
    condition2: "",
    condition3: "감정스코어줘",
    condition4: "분석하고나서 감정코드 골라줘",
  });
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);

  // List page states
  const [diaries, setDiaries] = useState([]);
  const [listLoading, setListLoading] = useState(false);
  const [listError, setListError] = useState(null);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [totalCount, setTotalCount] = useState(0);

  // API Base URL
  const API_BASE = "http://localhost:8080/service1/diaryChat";

  // AI 응답만 받기 (저장하지 않음)
  const handleGetResponse = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const requestData = {
        content: formData.content,
        condition1: formData.condition1 || null,
        condition2: formData.condition2 || null,
        condition3: formData.condition3 || null,
        condition4: formData.condition4 || null,
      };

      console.log("AI 응답 요청 데이터:", requestData);

      const apiResponse = await fetch(`${API_BASE}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestData),
      });

      if (!apiResponse.ok) {
        const errorData = await apiResponse.json();
        throw new Error(
          errorData.detail ||
            `서버 오류 (${apiResponse.status}): ${apiResponse.statusText}`
        );
      }

      const responseData = await apiResponse.json();
      console.log("AI 응답 수신:", responseData);

      setResponse(responseData);
    } catch (err) {
      console.error("API 호출 에러:", err);
      setError(err.message || "알 수 없는 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 감정일기 저장 (AI 응답 생성 + 저장을 한번에)
  const handleSaveDiary = async () => {
    if (!response) {
      alert("먼저 AI 응답을 받아주세요!");
      return;
    }

    setLoading(true);
    try {
      const requestData = {
        user_idx: currentUser,
        content: formData.content,
        condition1: formData.condition1 || null,
        condition2: formData.condition2 || null,
        condition3: formData.condition3 || null,
        condition4: formData.condition4 || null,
      };

      console.log("저장 요청 데이터:", requestData);

      const apiResponse = await fetch(`${API_BASE}/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestData),
      });

      if (!apiResponse.ok) {
        const errorData = await apiResponse.json();
        throw new Error(
          errorData.detail || `저장 실패 (${apiResponse.status})`
        );
      }

      const savedData = await apiResponse.json();
      console.log("저장 완료:", savedData);

      alert(
        `감정일기가 성공적으로 저장되었습니다! (ID: ${savedData.diary_idx})`
      );
      resetForm();
    } catch (err) {
      console.error("저장 에러:", err);
      alert("저장에 실패했습니다: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  // 감정일기 목록 조회
  const loadDiaries = async (pageNum = 1) => {
    setListLoading(true);
    setListError(null);

    try {
      const requestData = {
        user_idx: currentUser,
        page: pageNum,
        page_size: pageSize,
      };

      console.log("목록 조회 요청:", requestData);

      const apiResponse = await fetch(`${API_BASE}/list`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestData),
      });

      if (!apiResponse.ok) {
        const errorData = await apiResponse.json();
        throw new Error(
          errorData.detail || `목록 조회 실패 (${apiResponse.status})`
        );
      }

      const responseData = await apiResponse.json();
      console.log("목록 조회 결과:", responseData);

      setDiaries(responseData.diaries || []);
      setTotalCount(responseData.total_count || 0);
      setPage(pageNum);
    } catch (err) {
      console.error("목록 조회 에러:", err);
      setListError(err.message);
    } finally {
      setListLoading(false);
    }
  };

  // 감정일기 상세 조회
  const loadDiaryDetail = async (diaryIdx) => {
    try {
      const requestData = {
        diary_idx: diaryIdx,
        user_idx: currentUser,
      };

      console.log("상세 조회 요청:", requestData);

      const apiResponse = await fetch(`${API_BASE}/detail`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestData),
      });

      if (!apiResponse.ok) {
        const errorData = await apiResponse.json();
        throw new Error(
          errorData.detail || `상세 조회 실패 (${apiResponse.status})`
        );
      }

      const responseData = await apiResponse.json();
      console.log("상세 조회 결과:", responseData);

      setSelectedDiary(responseData);
      setCurrentPage("detail");
    } catch (err) {
      console.error("상세 조회 에러:", err);
      alert("상세 조회에 실패했습니다: " + err.message);
    }
  };

  // 감정일기 수정
  const handleUpdateDiary = async () => {
    if (!selectedDiary) return;

    setLoading(true);
    try {
      const requestData = {
        diary_idx: selectedDiary.diary_idx,
        user_idx: currentUser,
        content: formData.content,
        condition1: formData.condition1 || null,
        condition2: formData.condition2 || null,
        condition3: "감정스코어줘",
        condition4: "분석하고나서 감정코드 골라줘",
      };

      console.log("수정 요청 데이터:", requestData);

      const apiResponse = await fetch(`${API_BASE}/update`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestData),
      });

      if (!apiResponse.ok) {
        const errorData = await apiResponse.json();
        throw new Error(
          errorData.detail || `수정 실패 (${apiResponse.status})`
        );
      }

      const updatedData = await apiResponse.json();
      console.log("수정 완료:", updatedData);

      alert("감정일기가 성공적으로 수정되었습니다!");
      setSelectedDiary(updatedData);
      setCurrentPage("detail");
    } catch (err) {
      console.error("수정 에러:", err);
      alert("수정에 실패했습니다: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  // 감정일기 삭제
  const handleDeleteDiary = async (diaryIdx) => {
    if (!confirm("정말로 이 감정일기를 삭제하시겠습니까?")) return;

    try {
      const requestData = {
        diary_idx: diaryIdx,
        user_idx: currentUser,
      };

      console.log("삭제 요청:", requestData);

      const apiResponse = await fetch(`${API_BASE}/delete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestData),
      });

      if (!apiResponse.ok) {
        const errorData = await apiResponse.json();
        throw new Error(
          errorData.detail || `삭제 실패 (${apiResponse.status})`
        );
      }

      const deleteResult = await apiResponse.json();
      console.log("삭제 완료:", deleteResult);

      alert("감정일기가 성공적으로 삭제되었습니다!");

      if (currentPage === "detail") {
        setCurrentPage("list");
      }

      loadDiaries(page); // 목록 새로고침
    } catch (err) {
      console.error("삭제 에러:", err);
      alert("삭제에 실패했습니다: " + err.message);
    }
  };

  const resetForm = () => {
    setResponse(null);
    setError(null);
    setFormData({
      content: "",
      condition1: "",
      condition2: "",
      condition3: "감정스코어줘",
      condition4: "분석하고나서 감정코드 골라줘",
    });
  };

  // 페이지 변경 시 데이터 로드
  useEffect(() => {
    if (currentPage === "list") {
      loadDiaries();
    }
  }, [currentPage]);

  // 수정 페이지로 이동 시 폼 데이터 설정
  const goToEditPage = (diary) => {
    setSelectedDiary(diary);
    setFormData({
      content: diary.content || "",
      condition1: diary.condition1 || "",
      condition2: diary.condition2 || "",
      condition3: "감정스코어줘",
      condition4: "분석하고나서 감정코드 골라줘",
    });
    setCurrentPage("edit");
  };

  // 일기 쓰기 페이지 렌더링
  const renderWritePage = () => (
    <div className="flex-1 flex w-full min-h-0">
      <WriteForm
        formData={formData}
        setFormData={setFormData}
        loading={loading}
        handleGetResponse={handleGetResponse}
        handleSaveDiary={handleSaveDiary}
        response={response}
      />
      <AiResponseDisplay
        loading={loading}
        error={error}
        response={response}
        resetForm={resetForm}
        setError={setError}
      />
    </div>
  );

  return (
    <div className="min-h-screen w-screen flex flex-col bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Header */}
      <div className="px-8 py-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white">
        <h1 className="text-4xl font-bold mb-2 text-white">💭 감정일기</h1>
        <p className="text-lg opacity-90 text-white">
          AI와 함께하는 마음의 여행 • 당신의 감정을 소중히 담아드려요
        </p>
      </div>

      {/* Navigation */}
      <NavigationBar
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        resetForm={resetForm}
      />

      {/* Main Content */}
      {currentPage === "write" && renderWritePage()}
      {currentPage === "list" && (
        <DiaryList
          diaries={diaries}
          listLoading={listLoading}
          listError={listError}
          totalCount={totalCount}
          page={page}
          pageSize={pageSize}
          loadDiaries={loadDiaries}
          loadDiaryDetail={loadDiaryDetail}
          goToEditPage={goToEditPage}
          handleDeleteDiary={handleDeleteDiary}
          setCurrentPage={setCurrentPage}
        />
      )}
      {currentPage === "detail" && (
        <DiaryDetail
          selectedDiary={selectedDiary}
          goToEditPage={goToEditPage}
          handleDeleteDiary={handleDeleteDiary}
          setCurrentPage={setCurrentPage}
        />
      )}
      {currentPage === "edit" && (
        <DiaryEdit
          formData={formData}
          setFormData={setFormData}
          loading={loading}
          handleUpdateDiary={handleUpdateDiary}
          setCurrentPage={setCurrentPage}
        />
      )}
    </div>
  );
}

export default EmotionalDiary;
