import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

export default function TripDetailPage() {
  const navigate = useNavigate()
  const { id } = useParams()
  const [trip, setTrip] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const openMap = (place) => {
    const query = encodeURIComponent(place)
    window.open(`https://map.naver.com/v5/search/${query}`, '_blank')
  }

  useEffect(() => {
    const fetchTripDetail = async () => {
      try {
        setLoading(true)
        setError('')

        const apiBase = import.meta.env.VITE_API_BASE_URL || ''
        const res = await fetch(`${apiBase}/api/trip/${id}`)
        const data = await res.json()

        if (!res.ok || !data.success) {
          throw new Error(data.message || '여행 상세 정보를 불러오지 못했습니다.')
        }

        setTrip(data.trip)
      } catch (err) {
        console.error('TripDetailPage error:', err)
        setError(err.message || '상세 조회 중 오류가 발생했습니다.')
      } finally {
        setLoading(false)
      }
    }

    if (id) {
      fetchTripDetail()
    }
  }, [id])

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-5 sm:px-6 lg:px-8">
          <div>
            <p className="text-xl font-black tracking-tight text-blue-700">Seoul Like Local</p>
            <p className="text-xs text-slate-500">여행 상세 보기</p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/my-trips')}
              className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
            >
              보관함으로
            </button>
            <button
              onClick={() => navigate('/')}
              className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
            >
              메인으로
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
        {loading && (
          <div className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
            <p className="text-lg font-bold text-slate-900">여행 정보를 불러오는 중입니다...</p>
          </div>
        )}

        {!loading && error && (
          <div className="rounded-[28px] border border-red-200 bg-red-50 p-6">
            <p className="text-lg font-bold text-red-700">불러오기 실패</p>
            <p className="mt-2 text-red-600">{error}</p>
          </div>
        )}

        {!loading && !error && trip && (
          <div className="space-y-6">
            <section className="rounded-[32px] bg-gradient-to-r from-blue-600 via-indigo-600 to-pink-500 px-6 py-10 text-white sm:px-10">
              <p className="inline-flex rounded-full bg-white/15 px-4 py-2 text-sm font-semibold backdrop-blur">
                Trip Detail
              </p>
              <h1 className="mt-4 text-3xl font-black tracking-tight sm:text-4xl">
                {trip.title || '서울 추천 코스'}
              </h1>
              <p className="mt-3 text-white/85">생성일: {trip.created_at || '-'}</p>
            </section>

            {trip.result?.summary && (
              <section className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
                <p className="text-sm font-bold uppercase tracking-[0.2em] text-blue-600">요약</p>
                <p className="mt-3 text-lg font-semibold text-slate-900">{trip.result.summary}</p>
              </section>
            )}

            {trip.result?.travel_style && (
              <section className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
                <p className="text-sm font-bold uppercase tracking-[0.2em] text-blue-600">여행 스타일</p>
                <p className="mt-3 text-slate-700">{trip.result.travel_style}</p>
              </section>
            )}

            {Array.isArray(trip.result?.itinerary) && trip.result.itinerary.length > 0 && (
              <section className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
                <p className="text-sm font-bold uppercase tracking-[0.2em] text-blue-600">추천 일정</p>

                <div className="mt-6 space-y-4">
                  {trip.result.itinerary.map((item, index) => (
                    <div key={index} className="rounded-2xl bg-slate-50 p-5 ring-1 ring-slate-200">
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <div>
                          <p className="text-sm font-bold text-blue-600">{item.time}</p>
                          <h3 className="mt-1 text-xl font-black text-slate-900">{item.title}</h3>
                        </div>
                        <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-bold text-blue-700">
                          {item.category}
                        </span>
                      </div>

                      <p className="mt-3 text-slate-700">{item.reason}</p>

                      <div className="mt-4 grid gap-3 sm:grid-cols-2">
                        <div className="rounded-2xl bg-white p-4 ring-1 ring-slate-200">
                          <p className="text-xs font-semibold text-slate-500">예상 비용</p>
                          <p className="mt-2 text-sm font-bold text-slate-900">
                            {Number(item.estimated_cost || 0).toLocaleString()}원
                          </p>
                        </div>
                        <div className="rounded-2xl bg-white p-4 ring-1 ring-slate-200">
                          <p className="text-xs font-semibold text-slate-500">팁</p>
                          <p className="mt-2 text-sm font-bold text-slate-900">{item.tips || '-'}</p>
                        </div>
                      </div>

                      <div className="mt-4">
                        <button
                          type="button"
                          onClick={() => openMap(item.title)}
                          className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-bold text-white transition hover:bg-blue-700"
                        >
                          지도 보기
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {trip.result?.budget_comment && (
              <section className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
                <p className="text-sm font-bold uppercase tracking-[0.2em] text-blue-600">예산 안내</p>
                <p className="mt-3 text-slate-700">{trip.result.budget_comment}</p>
                <p className="mt-3 text-lg font-black text-slate-900">
                  총 예상 비용: {Number(trip.result.total_estimated_cost || 0).toLocaleString()}원
                </p>
              </section>
            )}

            {Array.isArray(trip.result?.tips) && trip.result.tips.length > 0 && (
              <section className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
                <p className="text-sm font-bold uppercase tracking-[0.2em] text-blue-600">여행 팁</p>
                <ul className="mt-4 space-y-2 text-slate-700">
                  {trip.result.tips.map((tip, index) => (
                    <li key={index}>• {tip}</li>
                  ))}
                </ul>
              </section>
            )}

            {Array.isArray(trip.result?.alternative_plan) && trip.result.alternative_plan.length > 0 && (
              <section className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
                <p className="text-sm font-bold uppercase tracking-[0.2em] text-blue-600">대체 코스</p>

                <div className="mt-6 space-y-4">
                  {trip.result.alternative_plan.map((item, index) => (
                    <div key={index} className="rounded-2xl bg-slate-50 p-5 ring-1 ring-slate-200">
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <div>
                          <p className="text-sm font-bold text-blue-600">{item.time}</p>
                          <h3 className="mt-1 text-xl font-black text-slate-900">{item.title}</h3>
                        </div>
                        <span className="rounded-full bg-slate-200 px-3 py-1 text-xs font-bold text-slate-700">
                          {item.category}
                        </span>
                      </div>

                      <p className="mt-3 text-slate-700">{item.reason}</p>
                      <p className="mt-3 text-sm font-semibold text-slate-900">
                        예상 비용: {Number(item.estimated_cost || 0).toLocaleString()}원
                      </p>
                      <p className="mt-1 text-sm text-slate-600">팁: {item.tips || '-'}</p>

                      <div className="mt-4">
                        <button
                          type="button"
                          onClick={() => openMap(item.title)}
                          className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-bold text-white transition hover:bg-slate-700"
                        >
                          지도 보기
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {trip.weather && (
              <section className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
                <p className="text-sm font-bold uppercase tracking-[0.2em] text-blue-600">날씨 참고</p>
                <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  <div className="rounded-2xl bg-slate-50 p-4 ring-1 ring-slate-200">
                    <p className="text-xs font-semibold text-slate-500">대상 지역</p>
                    <p className="mt-2 font-bold text-slate-900">{trip.weather.target_area || '-'}</p>
                  </div>
                  <div className="rounded-2xl bg-slate-50 p-4 ring-1 ring-slate-200">
                    <p className="text-xs font-semibold text-slate-500">강수 위험</p>
                    <p className="mt-2 font-bold text-slate-900">
                      {trip.weather.weather_summary?.rain_risk || '-'}
                    </p>
                  </div>
                  <div className="rounded-2xl bg-slate-50 p-4 ring-1 ring-slate-200">
                    <p className="text-xs font-semibold text-slate-500">추천 모드</p>
                    <p className="mt-2 font-bold text-slate-900">
                      {trip.weather.weather_summary?.recommendation_mode || '-'}
                    </p>
                  </div>
                </div>
              </section>
            )}
          </div>
        )}
      </main>
    </div>
  )
}