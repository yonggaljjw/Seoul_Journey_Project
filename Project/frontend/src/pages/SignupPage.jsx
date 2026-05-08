import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

export default function SignupPage() {
  const navigate = useNavigate()

  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  })

  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')

    if (!form.name || !form.email || !form.password || !form.confirmPassword) {
      setError('모든 항목을 입력해주세요.')
      return
    }

    if (form.password.length < 8) {
      setError('비밀번호는 8자 이상이어야 합니다.')
      return
    }

    if (form.password !== form.confirmPassword) {
      setError('비밀번호 확인이 일치하지 않습니다.')
      return
    }

    try {
      setLoading(true)

      const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: form.name,
          email: form.email,
          password: form.password,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.message || '회원가입 중 오류가 발생했습니다.')
        return
      }

      setMessage(data.message || '회원가입이 완료되었습니다.')

      setTimeout(() => {
        navigate('/')
      }, 1200)
    } catch (err) {
      setError('서버 연결에 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }
// 커밋
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="mx-auto flex min-h-screen max-w-7xl items-center justify-center px-4 py-10 sm:px-6 lg:px-8">
        <div className="grid w-full max-w-6xl overflow-hidden rounded-[32px] bg-white shadow-xl ring-1 ring-slate-200 lg:grid-cols-2">
          <div className="hidden lg:flex flex-col justify-between bg-gradient-to-br from-blue-600 via-indigo-600 to-pink-500 p-10 text-white">
            <div>
              <p className="text-sm font-bold uppercase tracking-[0.2em] text-white/70">
                Seoul Like Local
              </p>
              <h1 className="mt-6 text-5xl font-black leading-tight">
                회원가입하고
                <br />
                나만의 서울을
                <br />
                시작하세요
              </h1>
              <p className="mt-6 max-w-md text-white/85">
                취향 기반 서울 로컬 관광 추천, 일정 저장, 맞춤형 여행 코스 기능을 이용하려면
                먼저 가입해주세요.
              </p>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="rounded-2xl bg-white/10 p-4 backdrop-blur">
                <p className="text-xl font-black">AI</p>
                <p className="mt-1 text-sm text-white/80">취향 분석</p>
              </div>
              <div className="rounded-2xl bg-white/10 p-4 backdrop-blur">
                <p className="text-xl font-black">저장</p>
                <p className="mt-1 text-sm text-white/80">일정 관리</p>
              </div>
              <div className="rounded-2xl bg-white/10 p-4 backdrop-blur">
                <p className="text-xl font-black">추천</p>
                <p className="mt-1 text-sm text-white/80">맞춤 코스</p>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-center p-6 sm:p-10">
            <div className="w-full max-w-md">
              <div className="mb-8">
                <Link
                  to="/"
                  className="text-sm font-semibold text-blue-600 hover:text-blue-700"
                >
                  ← 메인으로 돌아가기
                </Link>
                <h2 className="mt-4 text-3xl font-black tracking-tight text-slate-900">
                  회원가입
                </h2>
                <p className="mt-2 text-slate-500">
                  기본 정보를 입력해 계정을 생성하세요.
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="mb-2 block text-sm font-semibold text-slate-700">
                    이름
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={form.name}
                    onChange={handleChange}
                    placeholder="이름을 입력하세요"
                    className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="mb-2 block text-sm font-semibold text-slate-700">
                    이메일
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={form.email}
                    onChange={handleChange}
                    placeholder="example@email.com"
                    className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="mb-2 block text-sm font-semibold text-slate-700">
                    비밀번호
                  </label>
                  <input
                    type="password"
                    name="password"
                    value={form.password}
                    onChange={handleChange}
                    placeholder="8자 이상 입력하세요"
                    className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="mb-2 block text-sm font-semibold text-slate-700">
                    비밀번호 확인
                  </label>
                  <input
                    type="password"
                    name="confirmPassword"
                    value={form.confirmPassword}
                    onChange={handleChange}
                    placeholder="비밀번호를 다시 입력하세요"
                    className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-blue-500"
                  />
                </div>

                {error && (
                  <div className="rounded-2xl bg-red-50 px-4 py-3 text-sm font-medium text-red-600">
                    {error}
                  </div>
                )}

                {message && (
                  <div className="rounded-2xl bg-green-50 px-4 py-3 text-sm font-medium text-green-600">
                    {message}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full rounded-2xl bg-blue-600 px-4 py-3 font-bold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
                >
                  {loading ? '가입 중...' : '회원가입'}
                </button>
              </form>

              <p className="mt-6 text-center text-sm text-slate-500">
  이미 계정이 있으신가요?{' '}
  <Link to="/login" className="font-semibold text-blue-600 hover:text-blue-700">
    로그인
  </Link>
</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}