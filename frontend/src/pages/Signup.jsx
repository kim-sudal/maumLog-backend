import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Visibility, VisibilityOff } from "@mui/icons-material";

function Signup() {
  const [formData, setFormData] = useState({
    login_id: "",
    login_password: "",
    password_confirm: "",
    user_name: "",
    birth_date: "",
    email: "",
  });
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);

  // 비밀번호 표시/숨김 상태
  const [showPassword, setShowPassword] = useState(false);
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // 날짜 형식 변환 (YYYY-MM-DD -> YYYYMMDD)
  const formatBirthDate = (dateString) => {
    if (!dateString) return "";
    return dateString.replace(/-/g, "");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const requestData = {
        login_id: formData.login_id,
        login_password: formData.login_password,
        password_confirm: formData.password_confirm,
        user_name: formData.user_name,
        birth_date: formatBirthDate(formData.birth_date),
        email: formData.email || null,
      };

      const apiResponse = await fetch(
        "http://localhost:8080/service1/user/signup",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(requestData),
        }
      );

      if (!apiResponse.ok) {
        const errorData = await apiResponse.json();
        throw new Error(
          errorData.detail ||
            `서버 오류 (${apiResponse.status}): ${apiResponse.statusText}`
        );
      }

      const responseData = await apiResponse.json();
      setResponse(responseData);
    } catch (err) {
      console.error("회원가입 에러:", err);
      setError(err.message || "알 수 없는 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 성공 시 로그인 페이지로 리다이렉트
  if (response && response.success) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center px-4">
        <div className="w-full max-w-md bg-white shadow-2xl rounded-3xl px-8 py-12 text-center">
          <div className="text-6xl mb-4">🎉</div>
          <h1 className="text-3xl font-bold text-[#1F2937] mb-4">
            회원가입 완료!
          </h1>
          <p className="text-lg text-gray-600 mb-6">{response.message}</p>
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg mb-6">
            <p className="text-green-800 font-medium">
              회원번호: {response.user_idx}
            </p>
          </div>
          <Link
            to="/"
            className="w-full bg-[#4ECDC4] hover:bg-[#3dc0b3] text-white font-bold py-3 rounded-lg transition shadow-md block"
          >
            로그인 하러 가기
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center px-4">
      <div className="w-full max-w-md bg-white shadow-2xl rounded-3xl px-8 py-12">
        <h1 className="text-4xl font-bold text-center text-[#1F2937] mb-10">
          회원가입
        </h1>

        {/* 에러 메시지 */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <input
            type="text"
            name="login_id"
            value={formData.login_id}
            onChange={handleChange}
            placeholder="로그인 아이디"
            required
            className="w-full border border-gray-200 px-5 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4ECDC4]"
          />

          {/* 비밀번호 필드 - 토글 버튼 포함 */}
          <div className="relative">
            <input
              type={showPassword ? "text" : "password"}
              name="login_password"
              value={formData.login_password}
              onChange={handleChange}
              placeholder="비밀번호"
              required
              className="w-full border border-gray-200 px-5 py-3 pr-12 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4ECDC4]"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 focus:outline-none"
            >
              {showPassword ? <VisibilityOff /> : <Visibility />}
            </button>
          </div>

          {/* 비밀번호 확인 필드 - 토글 버튼 포함 */}
          <div className="relative">
            <input
              type={showPasswordConfirm ? "text" : "password"}
              name="password_confirm"
              value={formData.password_confirm}
              onChange={handleChange}
              placeholder="비밀번호 확인"
              required
              className="w-full border border-gray-200 px-5 py-3 pr-12 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4ECDC4]"
            />
            <button
              type="button"
              onClick={() => setShowPasswordConfirm(!showPasswordConfirm)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 focus:outline-none"
            >
              {showPasswordConfirm ? <VisibilityOff /> : <Visibility />}
            </button>
          </div>

          <input
            type="text"
            name="user_name"
            value={formData.user_name}
            onChange={handleChange}
            placeholder="이름"
            required
            className="w-full border border-gray-200 px-5 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4ECDC4]"
          />

          <input
            type="date"
            name="birth_date"
            value={formData.birth_date}
            onChange={handleChange}
            placeholder="생년월일"
            className="w-full border border-gray-200 px-5 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4ECDC4]"
          />

          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="이메일 (선택사항)"
            className="w-full border border-gray-200 px-5 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4ECDC4]"
          />

          <button
            type="submit"
            disabled={loading}
            className={`w-full font-bold py-3 rounded-lg transition shadow-md ${
              loading
                ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                : "bg-[#4ECDC4] hover:bg-[#3dc0b3] text-white"
            }`}
          >
            {loading ? "처리중..." : "회원가입 완료"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-8">
          이미 계정이 있으신가요?{" "}
          <Link to="/" className="text-[#4ECDC4] font-medium hover:underline">
            로그인 하기
          </Link>
        </p>
      </div>
    </div>
  );
}

export default Signup;
