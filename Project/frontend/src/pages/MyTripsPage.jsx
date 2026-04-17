import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function MyTripsPage() {
  const navigate = useNavigate()
  const [trips, setTrips] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchTrips = async () => {
      try {
        setLoading(true)
        setError('')

        const user = localStorage.getItem('user')

        if (!user) {
          alert('로그인이 필요합니다.')
          navigate('/login')
          return
        }

        let parsedUser
        try {
          parsedUser = JSON.parse(user)
        } catch (parseError) {
          console.error('user parse error:', parseError)
          localStorage.removeItem('user')
          alert('로그인 정보가 올바르지 않습니다. 다시 로그인해주세요.')
          navigate('/login')
          return
        }

        if (!parsedUser?.id) {
          localStorage.removeItem('user')
          alert('사용자 정보가 올바르지 않습니다. 다시 로그인해주세요.')
          navigate('/login')
          return
        }

        const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
        const res = await fetch(`${apiBase}/api/trips/${parsedUser.id}`)

        let data
        try {
          data = await res.json()
        } catch (jsonError) {
          console.error('response json parse error:', jsonError)
          throw new Error('서버 응답 형식이 올바르지 않습니다.')
        }

        if (!res.ok || !data.success) {
          throw new Error(data.message || '보관함을 불러오지 못했습니다.')
        }

        setTrips(Array.isArray(data.trips) ? data.trips : [])
      } catch (err) {
        console.error('MyTripsPage error:', err)
        setError(err.message || '보관함 조회 중 오류가 발생했습니다.')
      } finally {
        setLoading(false)
      }
    }

    fetchTrips()
  }, [navigate])

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-5 sm:px-6 lg:px-8">
          <div>
            <p className="text-xl font-black tracking-tight text-blue-700">Seoul Like Local</p>
            <p className="text-xs text-slate-500">내 여행 보관함</p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/')}
              className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
            >
              메인으로
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <section className="mb-8">
          <div className="rounded-[32px] bg-gradient-to-r from-blue-600 via-indigo-600 to-pink-500 px-6 py-10 text-white sm:px-10">
            <p className="inline-flex rounded-full bg-white/15 px-4 py-2 text-sm font-semibold backdrop-blur">
              My Trips
            </p>
            <h1 className="mt-4 text-3xl font-black tracking-tight sm:text-4xl">내 여행 보관함</h1>
            <p className="mt-3 max-w-2xl text-white/85">
              지금까지 추천받은 서울 코스를 다시 확인하고, 마음에 드는 여행을 다시 열어볼 수 있어요.
            </p>
          </div>
        </section>

        {loading && (
          <div className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
            <p className="text-lg font-bold text-slate-900">보관함을 불러오는 중입니다...</p>
            <p className="mt-2 text-slate-600">저장된 추천 코스를 정리하고 있어요.</p>
          </div>
        )}

        {!loading && error && (
          <div className="rounded-[28px] border border-red-200 bg-red-50 p-6">
            <p className="text-lg font-bold text-red-700">불러오기 실패</p>
            <p className="mt-2 text-red-600">{error}</p>
            <button
              onClick={() => navigate('/')}
              className="mt-5 rounded-2xl bg-blue-600 px-6 py-3 font-bold text-white transition hover:bg-blue-700"
            >
              메인으로 돌아가기
            </button>
          </div>
        )}

        {!loading && !error && trips.length === 0 && (
          <div className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
            <p className="text-lg font-bold text-slate-900">아직 저장된 여행이 없습니다.</p>
            <p className="mt-2 text-slate-600">메인 페이지에서 코스를 추천받으면 이곳에 저장됩니다.</p>
            <button
              onClick={() => navigate('/')}
              className="mt-6 rounded-2xl bg-blue-600 px-6 py-4 font-bold text-white transition hover:bg-blue-700"
            >
              추천받으러 가기
            </button>
          </div>
        )}

        {!loading && !error && trips.length > 0 && (
          <section className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
            {trips.map((trip) => (
              <button
                key={trip.id}
                type="button"
                onClick={() => navigate(`/trip/${trip.id}`)}
                className="overflow-hidden rounded-[28px] bg-white p-6 text-left shadow-sm ring-1 ring-slate-200 transition hover:-translate-y-1 hover:shadow-lg"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-blue-600">
                      Saved Trip
                    </p>
                    <h2 className="mt-3 text-2xl font-black tracking-tight text-slate-900">
                      {trip.title || '서울 추천 코스'}
                    </h2>
                  </div>

                  <div className="rounded-2xl bg-blue-50 px-3 py-2 text-xs font-bold text-blue-700">
                    #{trip.id}
                  </div>
                </div>

                <div className="mt-5 grid gap-3 sm:grid-cols-2">
                  <div className="rounded-2xl bg-slate-50 p-4 ring-1 ring-slate-200">
                    <p className="text-xs font-semibold text-slate-500">여행 유형</p>
                    <p className="mt-2 text-sm font-bold text-slate-900">{trip.travel_type || '-'}</p>
                  </div>

                  <div className="rounded-2xl bg-slate-50 p-4 ring-1 ring-slate-200">
                    <p className="text-xs font-semibold text-slate-500">일정</p>
                    <p className="mt-2 text-sm font-bold text-slate-900">{trip.duration || '-'}</p>
                  </div>

                  <div className="rounded-2xl bg-slate-50 p-4 ring-1 ring-slate-200">
                    <p className="text-xs font-semibold text-slate-500">예산</p>
                    <p className="mt-2 text-sm font-bold text-slate-900">
                      {Number(trip.budget || 0).toLocaleString()}원
                    </p>
                  </div>

                  <div className="rounded-2xl bg-slate-50 p-4 ring-1 ring-slate-200">
                    <p className="text-xs font-semibold text-slate-500">생성일</p>
                    <p className="mt-2 text-sm font-bold text-slate-900">{trip.created_at || '-'}</p>
                  </div>
                </div>

                <div className="mt-5 rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-4">
                  <p className="text-xs font-semibold text-slate-500">취향 입력</p>
                  <p className="mt-2 line-clamp-3 text-sm leading-6 text-slate-700">
                    {trip.query_text || '-'}
                  </p>
                </div>

                <div className="mt-5 inline-flex items-center rounded-full bg-slate-900 px-4 py-2 text-sm font-semibold text-white">
                  상세 보기 →
                </div>
              </button>
            ))}
          </section>
        )}
      </main>
    </div>
  )
}