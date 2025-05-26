import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

function Login() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        login_id: "",
        login_password: "",
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const requestData = {
                login_id: formData.login_id,
                login_password: formData.login_password,
            };

            const apiResponse = await fetch("http://localhost:8080/service1/user/login", {
                method: "POST",
                headers: { 
                    'Content-Type': 'application/json' 
                },
                body: JSON.stringify(requestData)
            });

            if (!apiResponse.ok) {
                const errorData = await apiResponse.json();
                throw new Error(errorData.detail || `서버 오류 (${apiResponse.status}): ${apiResponse.statusText}`);
            }

            const responseData = await apiResponse.json();
            
            if (responseData.success) {
                console.log("로그인 성공:", responseData);
                alert(`${responseData.user_name}님, 환영합니다!`);
                
                // 홈으로 이동
                navigate('/EmotionalDiary');
            } else {
                throw new Error(responseData.error || "로그인에 실패했습니다.");
            }
        } catch (err) {
            console.error("로그인 에러:", err);
            setError(err.message || "알 수 없는 오류가 발생했습니다.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center px-4">
            <div className="w-full max-w-md bg-white shadow-2xl rounded-3xl px-8 py-12">
                <h1 className="text-4xl font-bold text-center text-[#1F2937] mb-10">
                    마음로그
                </h1>

                {/* 에러 메시지 */}
                {error && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                        <p className="text-red-800 text-sm">{error}</p>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <input
                            type="text"
                            name="login_id"
                            value={formData.login_id}
                            onChange={handleChange}
                            placeholder="로그인 아이디를 입력하세요"
                            required
                            className="w-full border border-gray-200 px-5 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4ECDC4]"
                        />
                    </div>

                    <div>
                        <input
                            type="password"
                            name="login_password"
                            value={formData.login_password}
                            onChange={handleChange}
                            placeholder="비밀번호를 입력하세요"
                            required
                            className="w-full border border-gray-200 px-5 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4ECDC4]"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className={`w-full font-bold py-3 rounded-lg transition shadow-md ${
                            loading 
                                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                : 'bg-[#4ECDC4] hover:bg-[#3dc0b3] text-white'
                        }`}
                    >
                        {loading ? '로그인 중...' : '로그인'}
                    </button>
                </form>

                <p className="text-center text-sm text-gray-500 mt-8">
                    아직 회원이 아니신가요?{' '}
                    <Link to="/signup" className="text-[#4ECDC4] font-medium hover:underline">
                        회원가입
                    </Link>
                </p>
            </div>
        </div>
    );
}

export default Login;