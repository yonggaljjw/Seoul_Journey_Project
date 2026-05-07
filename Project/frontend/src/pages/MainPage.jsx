import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function MainPage() {
  const navigate = useNavigate()

  const [query, setQuery] = useState('')
  const [budget, setBudget] = useState(70000)
  const [travelType, setTravelType] = useState('혼자 여행')
  const [duration, setDuration] = useState('1일')
  const [customDuration, setCustomDuration] = useState('')
  const [showPlanner, setShowPlanner] = useState(false)
  const [selectedTags, setSelectedTags] = useState([])
  const [selectedThemes, setSelectedThemes] = useState([])
  const [currentUser, setCurrentUser] = useState(null)

  const [loading, setLoading] = useState(false)
  const [recommendError, setRecommendError] = useState('')
  const [loadingStepIndex, setLoadingStepIndex] = useState(0)
  const [progressValue, setProgressValue] = useState(8)

  useEffect(() => {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      try {
        setCurrentUser(JSON.parse(savedUser))
      } catch (error) {
        localStorage.removeItem('user')
      }
    }
  }, [])

  useEffect(() => {
    if (!loading) {
      setLoadingStepIndex(0)
      setProgressValue(8)
      return
    }

    const stepInterval = setInterval(() => {
      setLoadingStepIndex((prev) => (prev + 1) % loadingMessages.length)
    }, 2200)

    const progressInterval = setInterval(() => {
      setProgressValue((prev) => {
        if (prev >= 92) return prev
        const next = prev + Math.random() * 12
        return Math.min(next, 92)
      })
    }, 900)

    return () => {
      clearInterval(stepInterval)
      clearInterval(progressInterval)
    }
  }, [loading])

  const themes = [
    {
      key: 'drama',
      title: 'K-드라마 감성',
      emoji: '🎬',
      desc: '드라마 속 주인공처럼 걷고 싶은 하루',
      image:
        'https://images.unsplash.com/photo-1517154421773-0529f29ea451?auto=format&fit=crop&w=900&q=80',
    },
    {
      key: 'kpop',
      title: 'K-팝 & 트렌드',
      emoji: '🎧',
      desc: '핫플, 팝업, 트렌디한 서울 무드',
      image:
        'https://images.unsplash.com/photo-1528164344705-47542687000d?auto=format&fit=crop&w=900&q=80',
    },
    {
      key: 'food',
      title: '로컬 미식 탐방',
      emoji: '🍜',
      desc: '현지 느낌 가득한 서울 맛집 코스',
      image:
        'https://images.unsplash.com/photo-1553163147-622ab57be1c7?auto=format&fit=crop&w=900&q=80',
    },
    {
      key: 'beauty',
      title: '뷰티 & 쇼핑',
      emoji: '🛍️',
      desc: '올리브영, 성수, 뷰티 스팟까지 한 번에',
      image:
        'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=900&q=80',
    },
    {
      key: 'walk',
      title: '조용한 산책',
      emoji: '🌿',
      desc: '복잡함을 피해 여유롭게 걷는 서울',
      image:
        'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=900&q=80',
    },
  ]

  const quickTags = ['혼자 여행', '커플 여행', '야경', '저예산', '성수', '홍대', '명동', '비 오는 날']
  const travelTypes = ['혼자 여행', '커플 여행', '친구/가족 여행']
  const durations = ['1일', '3일', '직접 입력']

  const features = [
    {
      title: 'AI 취향 분석',
      desc: '자연어 입력을 바탕으로 여행 의도와 분위기를 해석합니다.',
    },
    {
      title: '서울 공공데이터 조회',
      desc: '관광지, 문화공간, 쇼핑, 숙박, 가격 데이터를 기반으로 후보를 찾습니다.',
    },
    {
      title: '맞춤 코스 추천',
      desc: '날씨, 예산, 여행 유형을 반영해 최종 서울 코스를 구성합니다.',
    },
  ]

  const loadingMessages = [
    {
      title: '취향과 여행 목적을 분석하고 있어요',
      desc: '입력한 키워드에서 원하는 분위기와 서울의 무드를 해석하고 있습니다.',
    },
    {
      title: '서울 공공데이터에서 후보 장소를 찾고 있어요',
      desc: '관광지, 문화공간, 쇼핑 장소, 음식 가격 데이터를 기반으로 실제 후보를 조회하고 있습니다.',
    },
    {
      title: '날씨와 지역 특성을 반영하고 있어요',
      desc: '오늘의 서울 날씨와 지역 특성을 고려해 실내·야외 동선을 조정하고 있습니다.',
    },
    {
      title: '예산에 맞는 흐름을 설계하고 있어요',
      desc: '개인서비스 가격 데이터와 입력 예산을 함께 고려해 무리 없는 코스를 구성하고 있습니다.',
    },
    {
      title: '대체 코스까지 준비하고 있어요',
      desc: '비가 오거나 혼잡할 때를 대비한 실내형·저예산형 대안도 함께 구성하고 있습니다.',
    },
  ]

  const loadingTips = [
    '팁: 이 추천은 서울 관광·문화·쇼핑·가격 데이터를 함께 참고해 생성됩니다.',
    '팁: 비 오는 날은 실내 전시, 쇼핑, 복합문화공간 조합이 만족도가 높아요.',
    '팁: 예산이 낮을수록 가격 데이터 기반 식사 후보를 우선 반영합니다.',
  ]

  const previewMoments = [
    {
      time: '11:00',
      title: '공공데이터 후보 탐색 중',
      desc: '입력한 지역과 취향에 맞는 관광·문화·쇼핑 후보를 찾고 있어요.',
    },
    {
      time: '14:00',
      title: '날씨 기반 동선 조정 중',
      desc: '비, 더위, 추위 가능성을 반영해 실내·야외 비중을 조정하고 있어요.',
    },
    {
      time: '18:00',
      title: '예산과 대체 코스 구성 중',
      desc: '식사 가격 데이터와 예산을 반영해 무리 없는 하루 흐름을 만들고 있어요.',
    },
  ]

  const finalDuration = useMemo(() => {
    if (duration === '직접 입력') {
      return customDuration.trim()
    }
    return duration
  }, [duration, customDuration])

  const mergedQuery = useMemo(() => {
    const tagText = selectedTags.length > 0 ? selectedTags.join(', ') : ''
    const themeText =
      selectedThemes.length > 0
        ? selectedThemes
            .map((key) => themes.find((theme) => theme.key === key)?.title)
            .filter(Boolean)
            .join(', ')
        : ''

    const durationText = finalDuration ? `일정: ${finalDuration}` : ''

    return [query, tagText, themeText, durationText].filter(Boolean).join(' / ')
  }, [query, selectedTags, selectedThemes, themes, finalDuration])

  const activeThemeTitles = useMemo(() => {
    return selectedThemes
      .map((key) => themes.find((theme) => theme.key === key)?.title)
      .filter(Boolean)
  }, [selectedThemes, themes])

  const toggleTag = (tag) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((item) => item !== tag) : [...prev, tag],
    )
  }

  const toggleTheme = (themeKey) => {
    setSelectedThemes((prev) =>
      prev.includes(themeKey) ? prev.filter((item) => item !== themeKey) : [...prev, themeKey],
    )
  }

  const requireLoginAndOpenPlanner = () => {
    if (!currentUser) {
      alert('로그인이 필요합니다.')
      navigate('/login')
      return
    }

    if (!query.trim() && selectedTags.length === 0 && selectedThemes.length === 0) {
      alert('먼저 빠른 취향 입력 또는 태그/테마를 선택해주세요.')
      return
    }

    setShowPlanner(true)

    setTimeout(() => {
      const section = document.getElementById('planner')
      if (section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }, 50)
  }

  const handleTextareaKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      requireLoginAndOpenPlanner()
    }
  }

  const handleDurationChange = (value) => {
    setDuration(value)
    if (value !== '직접 입력') {
      setCustomDuration('')
    }
  }

  const handleGoMyTrips = () => {
    if (!currentUser) {
      alert('로그인이 필요합니다.')
      navigate('/login')
      return
    }
    navigate('/my-trips')
  }

  const handleFinalRecommend = async () => {
    if (!currentUser) {
      alert('로그인이 필요합니다.')
      navigate('/login')
      return
    }

    if (duration === '직접 입력' && !customDuration.trim()) {
      alert('직접 입력한 일정을 작성해주세요.')
      return
    }

    const payload = {
      user_id: currentUser?.id,
      query_text: query,
      merged_query: mergedQuery,
      selected_tags: selectedTags,
      selected_themes: selectedThemes,
      travel_type: travelType,
      duration: finalDuration || duration,
      budget,
    }

    try {
      setLoading(true)
      setRecommendError('')

      const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

      const recommendRes = await fetch(`${apiBase}/api/recommend`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      const recommendData = await recommendRes.json()
      console.log('recommend response:', recommendData)

      if (!recommendRes.ok || !recommendData.success) {
  throw new Error(
    recommendData.error ||
    recommendData.message ||
    '추천 생성에 실패했습니다.'
  )
}

      try {
        const saveRes = await fetch(`${apiBase}/api/trips`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: currentUser.id,
            title:
              recommendData?.result?.summary ||
              mergedQuery?.slice(0, 60) ||
              '서울 여행 추천 코스',
            query_text: query,
            merged_query: mergedQuery,
            travel_type: travelType,
            duration: finalDuration || duration,
            budget,
            result: recommendData.result,
            weather: recommendData.weather,
            public_data_candidates: recommendData.public_data_candidates,
          }),
        })

        const saveData = await saveRes.json()
        console.log('trip save response:', saveData)

        if (!saveRes.ok || !saveData.success) {
          console.warn('보관함 저장 실패:', saveData.message || saveData.error)
        }
      } catch (saveError) {
        console.error('보관함 저장 실패:', saveError)
      }

      setProgressValue(100)

      navigate('/recommend-result', {
        state: {
          resultData: recommendData.result,
          requestInfo: payload,
          weatherData: recommendData.weather,
          publicDataCandidates: recommendData.public_data_candidates,
        },
      })
    } catch (error) {
      console.error('추천 요청 실패:', error)
      setRecommendError(error.message || '추천 생성 중 오류가 발생했습니다.')
      alert(error.message || '추천 생성 중 오류가 발생했습니다.')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('user')
    setCurrentUser(null)
    setShowPlanner(false)
    setRecommendError('')
    alert('로그아웃되었습니다.')
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      {loading && (
        <div className="fixed inset-0 z-[100] overflow-y-auto bg-slate-950/70 px-4 py-8 backdrop-blur-md">
          <div className="mx-auto flex min-h-full max-w-5xl items-center justify-center">
            <div className="w-full overflow-hidden rounded-[36px] bg-white shadow-2xl ring-1 ring-slate-200">
              <div className="relative overflow-hidden bg-gradient-to-r from-blue-600 via-indigo-600 to-pink-500 px-6 py-8 text-white sm:px-8 sm:py-10">
                <div className="absolute -left-10 top-0 h-40 w-40 rounded-full bg-white/10 blur-3xl" />
                <div className="absolute bottom-0 right-0 h-40 w-40 rounded-full bg-white/10 blur-3xl" />

                <div className="relative">
                  <div className="inline-flex rounded-full bg-white/15 px-4 py-2 text-sm font-semibold backdrop-blur">
                    AI가 서울 코스를 설계 중입니다
                  </div>

                  <div className="mt-5 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
                    <div>
                      <h3 className="text-3xl font-black tracking-tight sm:text-4xl">
                        {loadingMessages[loadingStepIndex].title}
                      </h3>
                      <p className="mt-3 max-w-2xl text-sm leading-7 text-white/85 sm:text-base">
                        {loadingMessages[loadingStepIndex].desc}
                      </p>

                      <div className="mt-6">
                        <div className="mb-2 flex items-center justify-between text-xs font-semibold text-white/80">
                          <span>추천 생성 진행률</span>
                          <span>{Math.round(progressValue)}%</span>
                        </div>
                        <div className="h-3 w-full overflow-hidden rounded-full bg-white/20">
                          <div
                            className="h-full rounded-full bg-white transition-all duration-700 ease-out"
                            style={{ width: `${progressValue}%` }}
                          />
                        </div>
                      </div>
                    </div>

                    <div className="rounded-[28px] bg-white/10 p-5 backdrop-blur">
                      <p className="text-sm font-bold uppercase tracking-[0.2em] text-white/80">입력 요약</p>
                      <div className="mt-4 space-y-3 text-sm">
                        <div className="rounded-2xl bg-white/10 px-4 py-3">
                          <p className="text-white/70">여행 유형</p>
                          <p className="mt-1 text-lg font-bold text-white">{travelType}</p>
                        </div>
                        <div className="rounded-2xl bg-white/10 px-4 py-3">
                          <p className="text-white/70">일정</p>
                          <p className="mt-1 text-lg font-bold text-white">{finalDuration || duration}</p>
                        </div>
                        <div className="rounded-2xl bg-white/10 px-4 py-3">
                          <p className="text-white/70">예산</p>
                          <p className="mt-1 text-lg font-bold text-white">{budget.toLocaleString()}원</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid gap-6 px-6 py-6 sm:px-8 sm:py-8 lg:grid-cols-[1fr_1fr]">
                <div>
                  <p className="text-sm font-bold uppercase tracking-[0.2em] text-blue-600">AI 미리보기</p>
                  <div className="mt-4 space-y-3">
                    {previewMoments.map((item, idx) => (
                      <div
                        key={idx}
                        className={`rounded-[24px] p-4 ring-1 transition ${
                          idx === loadingStepIndex % previewMoments.length
                            ? 'bg-blue-50 ring-blue-200'
                            : 'bg-slate-50 ring-slate-200'
                        }`}
                      >
                        <div className="flex items-start gap-4">
                          <div className="rounded-2xl bg-white px-3 py-2 text-sm font-black text-blue-700 ring-1 ring-slate-200">
                            {item.time}
                          </div>
                          <div>
                            <p className="text-lg font-black text-slate-900">{item.title}</p>
                            <p className="mt-1 text-sm leading-6 text-slate-600">{item.desc}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="mt-4 rounded-[24px] border border-dashed border-slate-300 bg-slate-50 px-4 py-4">
                    <p className="text-xs font-semibold text-slate-500">현재 입력된 취향</p>
                    <p className="mt-2 text-sm font-semibold leading-6 text-slate-900">
                      {mergedQuery || '입력된 취향이 없습니다.'}
                    </p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="rounded-[28px] bg-slate-50 p-5 ring-1 ring-slate-200">
                    <p className="text-sm font-bold uppercase tracking-[0.2em] text-blue-600">선택한 테마</p>
                    <div className="mt-4 flex flex-wrap gap-2">
                      {activeThemeTitles.length > 0 ? (
                        activeThemeTitles.map((themeTitle, idx) => (
                          <span
                            key={idx}
                            className="rounded-full bg-white px-4 py-2 text-sm font-semibold text-slate-700 ring-1 ring-slate-200"
                          >
                            {themeTitle}
                          </span>
                        ))
                      ) : (
                        <span className="rounded-full bg-white px-4 py-2 text-sm font-semibold text-slate-500 ring-1 ring-slate-200">
                          선택된 테마 없음
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="rounded-[28px] bg-slate-50 p-5 ring-1 ring-slate-200">
                    <p className="text-sm font-bold uppercase tracking-[0.2em] text-blue-600">
                      서울 공공데이터 활용
                    </p>
                    <div className="mt-4 space-y-3">
                      {loadingTips.map((tip, idx) => (
                        <div
                          key={idx}
                          className="rounded-2xl bg-white p-4 text-sm leading-6 text-slate-700 ring-1 ring-slate-200"
                        >
                          {tip}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="rounded-[28px] bg-gradient-to-r from-slate-900 to-slate-700 p-5 text-white">
                    <p className="text-sm font-bold uppercase tracking-[0.2em] text-white/70">지금 만드는 중</p>
                    <p className="mt-3 text-lg font-black">공공데이터, 날씨, 예산을 함께 반영한 서울 맞춤 코스</p>
                    <p className="mt-2 text-sm leading-6 text-white/80">
                      사용자의 입력을 바탕으로 실제 서울 관광·문화·쇼핑·가격 데이터를 조회하고 있어요.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <header className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <div>
            <p className="text-xl font-black tracking-tight text-blue-700">Seoul Like Local</p>
            <p className="text-xs text-slate-500">AI 기반 서울 맞춤 로컬 관광 추천</p>
          </div>

          <nav className="hidden items-center gap-8 md:flex">
            <a href="#intro" className="text-sm font-medium text-slate-600 transition hover:text-blue-600">
              서비스 소개
            </a>
            <a href="#theme" className="text-sm font-medium text-slate-600 transition hover:text-blue-600">
              취향 선택
            </a>
            <a href="#recommend" className="text-sm font-medium text-slate-600 transition hover:text-blue-600">
              추천 방식
            </a>
          </nav>

          {!currentUser ? (
            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate('/login')}
                className="hidden rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 sm:block"
              >
                로그인
              </button>
              <button
                onClick={() => navigate('/signup')}
                className="rounded-full bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-200 transition hover:bg-blue-700"
              >
                회원가입
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <button
                onClick={handleGoMyTrips}
                className="hidden rounded-full border border-blue-200 bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700 transition hover:bg-blue-100 sm:block"
              >
                내 여행 보관함
              </button>
              <div className="hidden rounded-full bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700 sm:block">
                환영합니다, {currentUser.name}님
              </div>
              <button
                onClick={handleLogout}
                className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
              >
                로그아웃
              </button>
            </div>
          )}
        </div>
      </header>

      <main>
        <section id="intro" className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-600 via-indigo-600 to-pink-500 opacity-95" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.25),transparent_30%),radial-gradient(circle_at_bottom_left,rgba(255,255,255,0.18),transparent_28%)]" />

          <div className="relative mx-auto grid max-w-7xl gap-12 px-4 py-16 sm:px-6 lg:grid-cols-2 lg:px-8 lg:py-24">
            <div className="flex flex-col justify-center text-white">
              <span className="mb-4 inline-flex w-fit rounded-full bg-white/15 px-4 py-2 text-sm font-semibold backdrop-blur">
                외국인을 위한 서울 일상관광 AI 서비스
              </span>

              <h1 className="text-4xl font-black leading-tight tracking-tight sm:text-5xl lg:text-6xl">
                취향으로 찾는
                <br />
                진짜 서울 여행
              </h1>

              <p className="mt-6 max-w-xl text-base leading-7 text-white/85 sm:text-lg">
                서울 관광·문화·쇼핑·가격 데이터를 기반으로 날씨와 예산까지 반영해{' '}
                <span className="font-bold text-white">나에게 맞는 서울 코스</span>를 추천합니다.
              </p>

              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <button
                  onClick={requireLoginAndOpenPlanner}
                  className="rounded-2xl bg-white px-6 py-4 text-base font-bold text-blue-700 transition hover:scale-[1.02]"
                >
                  지금 추천받기
                </button>
                {currentUser && (
                  <button
                    onClick={handleGoMyTrips}
                    className="rounded-2xl border border-white/30 bg-white/10 px-6 py-4 text-base font-semibold text-white backdrop-blur transition hover:bg-white/20"
                  >
                    내 여행 보관함 보기
                  </button>
                )}
              </div>

              <div className="mt-10 grid grid-cols-3 gap-4 sm:max-w-lg">
                <div className="rounded-2xl bg-white/12 p-4 backdrop-blur">
                  <p className="text-2xl font-black">AI</p>
                  <p className="mt-1 text-sm text-white/75">취향 분석</p>
                </div>
                <div className="rounded-2xl bg-white/12 p-4 backdrop-blur">
                  <p className="text-2xl font-black">공공</p>
                  <p className="mt-1 text-sm text-white/75">서울 데이터</p>
                </div>
                <div className="rounded-2xl bg-white/12 p-4 backdrop-blur">
                  <p className="text-2xl font-black">날씨</p>
                  <p className="mt-1 text-sm text-white/75">실시간 반영</p>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-center">
              <div className="w-full max-w-xl rounded-[28px] border border-white/30 bg-white/90 p-5 shadow-2xl shadow-black/10 backdrop-blur sm:p-6">
                <div className="rounded-[24px] bg-slate-50 p-5 sm:p-6">
                  <div className="mb-5 flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-blue-600">오늘 서울을 어떻게 보내고 싶나요?</p>
                      <h2 className="mt-1 text-2xl font-black tracking-tight text-slate-900">빠른 취향 입력</h2>
                    </div>
                    <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-bold text-blue-700">
                      STEP 1
                    </span>
                  </div>

                  <textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={handleTextareaKeyDown}
                    className="h-32 w-full resize-none rounded-2xl border border-slate-200 bg-white px-4 py-4 text-sm outline-none ring-0 placeholder:text-slate-400 focus:border-blue-500"
                    placeholder="예: 명동에서 쇼핑하고 밥 먹고 싶어 / 성수 감성 카페와 소품샵 / 비 오는 날 실내 전시 코스"
                  />

                  <div className="mt-4 flex flex-wrap gap-2">
                    {quickTags.map((tag) => {
                      const active = selectedTags.includes(tag)
                      return (
                        <button
                          key={tag}
                          type="button"
                          onClick={() => toggleTag(tag)}
                          className={`rounded-full border px-3 py-2 text-xs font-semibold transition ${
                            active
                              ? 'border-blue-600 bg-blue-600 text-white'
                              : 'border-slate-200 bg-white text-slate-700 hover:border-blue-300 hover:text-blue-700'
                          }`}
                        >
                          #{tag}
                        </button>
                      )
                    })}
                  </div>

                  <button
                    onClick={requireLoginAndOpenPlanner}
                    className="mt-6 flex w-full items-center justify-center rounded-2xl bg-blue-600 px-5 py-4 text-base font-bold text-white transition hover:bg-blue-700"
                  >
                    AI 추천 코스 생성하기
                  </button>

                  {!currentUser ? (
                    <p className="mt-3 text-center text-xs font-medium text-red-400">
                      추천 기능은 로그인 후 이용할 수 있습니다.
                    </p>
                  ) : (
                    <p className="mt-3 text-center text-xs text-slate-400">
                      Enter를 누르면 다음 단계로 넘어갑니다. 줄바꿈은 Shift + Enter
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="theme" className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8 lg:py-24">
          <div className="mb-10 text-center">
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-blue-600">취향 테마 선택</p>
            <h2 className="mt-3 text-3xl font-black tracking-tight text-slate-900 sm:text-4xl">
              원하는 서울의 분위기를 골라보세요
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-slate-600">
              선택한 테마는 서울 공공데이터 후보 조회와 AI 추천 프롬프트에 함께 반영됩니다.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-5">
            {themes.map((theme) => {
              const active = selectedThemes.includes(theme.key)

              return (
                <button
                  key={theme.key}
                  type="button"
                  onClick={() => toggleTheme(theme.key)}
                  className={`group overflow-hidden rounded-[24px] bg-white text-left shadow-sm ring-1 transition duration-300 hover:-translate-y-1 hover:shadow-xl ${
                    active ? 'ring-blue-500' : 'ring-slate-200'
                  }`}
                >
                  <div className="relative aspect-[4/5] overflow-hidden">
                    <img
                      src={theme.image}
                      alt={theme.title}
                      className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/10 to-transparent" />

                    {active && (
                      <div className="absolute right-4 top-4 rounded-full bg-blue-600 px-3 py-1 text-xs font-bold text-white">
                        선택됨
                      </div>
                    )}

                    <div className="absolute bottom-0 left-0 right-0 p-5 text-white">
                      <div className="mb-2 text-2xl">{theme.emoji}</div>
                      <h3 className="text-xl font-extrabold">{theme.title}</h3>
                      <p className="mt-2 text-sm text-white/80">{theme.desc}</p>
                    </div>
                  </div>
                </button>
              )
            })}
          </div>
        </section>

        {showPlanner && currentUser && (
          <section id="planner" className="mx-auto max-w-7xl px-4 pb-16 sm:px-6 lg:px-8">
            <div className="rounded-[32px] bg-white p-6 shadow-sm ring-1 ring-slate-200 sm:p-8 lg:p-10">
              <div className="mb-8">
                <div className="mb-3 inline-flex rounded-full bg-blue-100 px-4 py-2 text-sm font-bold text-blue-700">
                  STEP 2
                </div>
                <p className="text-sm font-bold uppercase tracking-[0.2em] text-blue-600">추가 정보 입력</p>
                <h2 className="mt-3 text-3xl font-black tracking-tight text-slate-900 sm:text-4xl">
                  여행 스타일과 예산을 한 번에 설정하세요
                </h2>
                <p className="mt-3 text-slate-600">
                  먼저 입력한 취향을 바탕으로, 서울 공공데이터 후보 조회 정확도를 높이기 위한 조건을 입력합니다.
                </p>
              </div>

              <div className="mb-6 rounded-2xl bg-slate-50 p-5 ring-1 ring-slate-200">
                <p className="text-xs font-semibold text-slate-500">현재 입력된 취향</p>
                <p className="mt-2 break-words text-base font-semibold text-slate-900">
                  {mergedQuery || '입력된 취향이 없습니다.'}
                </p>
              </div>

              <div className="grid gap-6 lg:grid-cols-12">
                <div className="lg:col-span-4">
                  <div className="h-full rounded-[28px] bg-slate-50 p-6 ring-1 ring-slate-200">
                    <p className="text-sm font-bold text-blue-600">여행 유형</p>
                    <h3 className="mt-2 text-2xl font-black tracking-tight text-slate-900">
                      누구와 함께하시나요?
                    </h3>

                    <div className="mt-6 space-y-3">
                      {travelTypes.map((item) => {
                        const active = travelType === item
                        return (
                          <button
                            key={item}
                            type="button"
                            onClick={() => setTravelType(item)}
                            className={`flex w-full items-center justify-between rounded-2xl border px-5 py-5 text-left transition ${
                              active
                                ? 'border-blue-200 bg-blue-50'
                                : 'border-slate-200 bg-white hover:border-blue-200 hover:bg-blue-50/60'
                            }`}
                          >
                            <span className="text-lg font-semibold text-slate-800">{item}</span>
                            <span
                              className={`flex h-6 w-6 items-center justify-center rounded-full border-2 ${
                                active ? 'border-blue-500 bg-blue-500' : 'border-slate-400'
                              }`}
                            >
                              <span
                                className={`h-3 w-3 rounded-full bg-white ${
                                  active ? 'opacity-100' : 'opacity-0'
                                }`}
                              />
                            </span>
                          </button>
                        )
                      })}
                    </div>
                  </div>
                </div>

                <div className="lg:col-span-8">
                  <div className="h-full rounded-[28px] bg-slate-50 p-6 ring-1 ring-slate-200">
                    <div className="flex flex-col gap-8">
                      <div>
                        <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
                          <div>
                            <p className="text-sm font-bold text-blue-600">여행 기간</p>
                            <h3 className="mt-2 text-2xl font-black tracking-tight text-slate-900">
                              일정은 얼마나 되나요?
                            </h3>
                          </div>

                          <div className="grid w-full grid-cols-3 rounded-full bg-slate-200 p-1 text-sm font-bold text-slate-600 xl:w-auto xl:min-w-[360px]">
                            {durations.map((item) => {
                              const active = duration === item
                              return (
                                <button
                                  key={item}
                                  type="button"
                                  onClick={() => handleDurationChange(item)}
                                  className={`rounded-full px-5 py-3 transition ${
                                    active
                                      ? 'bg-white text-blue-700 shadow-sm'
                                      : 'text-slate-600 hover:text-slate-900'
                                  }`}
                                >
                                  {item}
                                </button>
                              )
                            })}
                          </div>
                        </div>

                        {duration === '직접 입력' && (
                          <div className="mt-4">
                            <label className="mb-2 block text-sm font-semibold text-slate-700">
                              원하는 일정을 직접 입력해주세요
                            </label>
                            <input
                              type="text"
                              value={customDuration}
                              onChange={(e) => setCustomDuration(e.target.value)}
                              placeholder="예: 반나절, 2박 3일, 저녁 6시~밤 10시"
                              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none placeholder:text-slate-400 focus:border-blue-500"
                            />
                            <p className="mt-2 text-xs text-slate-500">
                              자유롭게 입력하면 추천 코스와 숙박 후보 조회 여부에 반영됩니다.
                            </p>
                          </div>
                        )}
                      </div>

                      <div className="rounded-[24px] bg-white p-5 ring-1 ring-slate-200">
                        <div className="mb-4 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
                          <div>
                            <p className="text-sm font-bold text-blue-600">예산 설정</p>
                            <h3 className="mt-2 text-2xl font-black tracking-tight text-slate-900">
                              하루 예산은 어느 정도인가요?
                            </h3>
                          </div>

                          <div className="text-left md:text-right">
                            <p className="text-xs font-semibold text-slate-500">예상 일일 기준</p>
                            <p className="text-3xl font-black text-blue-700 sm:text-4xl">
                              {budget.toLocaleString()}원
                            </p>
                          </div>
                        </div>

                        <input
                          type="range"
                          min="30000"
                          max="1000000"
                          step="10000"
                          value={budget}
                          onChange={(e) => setBudget(Number(e.target.value))}
                          className="w-full accent-blue-600"
                        />

                        <div className="mt-2 flex justify-between text-xs font-semibold text-slate-400">
                          <span>가성비</span>
                          <span>프리미엄</span>
                        </div>

                        <div className="mt-6 grid gap-3 rounded-2xl bg-slate-50 p-4 sm:grid-cols-3">
                          <div className="rounded-2xl bg-white p-4 ring-1 ring-slate-200">
                            <p className="text-xs font-semibold text-slate-500">선택된 여행 유형</p>
                            <p className="mt-2 text-lg font-bold text-slate-900">{travelType}</p>
                          </div>
                          <div className="rounded-2xl bg-white p-4 ring-1 ring-slate-200">
                            <p className="text-xs font-semibold text-slate-500">선택된 일정</p>
                            <p className="mt-2 text-lg font-bold text-slate-900">{finalDuration || duration}</p>
                          </div>
                          <div className="rounded-2xl bg-white p-4 ring-1 ring-slate-200">
                            <p className="text-xs font-semibold text-slate-500">예상 예산</p>
                            <p className="mt-2 text-lg font-bold text-slate-900">
                              {budget.toLocaleString()}원
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="flex flex-col gap-3 pt-2 sm:flex-row">
                        <button
                          type="button"
                          onClick={handleFinalRecommend}
                          disabled={loading}
                          className={`flex-1 rounded-2xl px-6 py-4 text-base font-bold text-white transition ${
                            loading ? 'cursor-not-allowed bg-blue-300' : 'bg-blue-600 hover:bg-blue-700'
                          }`}
                        >
                          {loading ? 'AI가 코스를 설계 중입니다...' : '최종 추천 받기'}
                        </button>
                        <button
                          type="button"
                          onClick={() => setShowPlanner(false)}
                          className="rounded-2xl border border-slate-300 bg-white px-6 py-4 text-base font-semibold text-slate-700 transition hover:bg-slate-100"
                        >
                          이전 단계로
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        )}

        {recommendError && (
          <section className="mx-auto max-w-7xl px-4 pb-16 sm:px-6 lg:px-8">
            <div className="rounded-[28px] border border-red-200 bg-red-50 p-6">
              <p className="text-lg font-bold text-red-700">추천 생성 실패</p>
              <p className="mt-2 text-red-600">{recommendError}</p>
            </div>
          </section>
        )}

        <section id="recommend" className="bg-slate-100/80 py-16 lg:py-24">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="mb-10 text-center">
              <p className="text-sm font-bold uppercase tracking-[0.2em] text-blue-600">추천 방식</p>
              <h2 className="mt-3 text-3xl font-black tracking-tight text-slate-900 sm:text-4xl">
                이렇게 추천이 만들어집니다
              </h2>
            </div>

            <div className="grid gap-6 md:grid-cols-3">
              {features.map((feature, idx) => (
                <div key={feature.title} className="rounded-[24px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
                  <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-100 text-lg font-black text-blue-700">
                    0{idx + 1}
                  </div>
                  <h3 className="text-xl font-black tracking-tight text-slate-900">{feature.title}</h3>
                  <p className="mt-3 leading-7 text-slate-600">{feature.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8 lg:py-24">
          <div className="overflow-hidden rounded-[32px] bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-10 text-white sm:px-10 lg:px-14 lg:py-14">
            <div className="flex flex-col gap-8 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-sm font-bold uppercase tracking-[0.2em] text-white/70">지금 바로 시작</p>
                <h2 className="mt-3 text-3xl font-black tracking-tight sm:text-4xl">
                  관광지가 아닌,
                  <br className="hidden sm:block" />
                  데이터 기반 서울 코스를 추천받아보세요.
                </h2>
                <p className="mt-4 max-w-2xl text-white/85">
                  빠른 취향 입력 후 추가 조건을 보완하면, 서울 공공데이터와 날씨를 함께 반영한 코스가 생성됩니다.
                </p>
              </div>

              <div className="flex flex-col gap-3 sm:flex-row">
                <button
                  onClick={requireLoginAndOpenPlanner}
                  className="rounded-2xl bg-white px-6 py-4 font-bold text-blue-700 transition hover:scale-[1.02]"
                >
                  코스 추천 받기
                </button>
                {currentUser && (
                  <button
                    onClick={handleGoMyTrips}
                    className="rounded-2xl border border-white/30 bg-white/10 px-6 py-4 font-semibold text-white backdrop-blur transition hover:bg-white/20"
                  >
                    내 여행 보관함
                  </button>
                )}
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-10 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
          <div>
            <p className="text-lg font-black text-slate-900">Seoul Like Local</p>
            <p className="mt-1 text-sm text-slate-500">AI 기반 외국인 맞춤형 서울 일상관광 추천 플랫폼</p>
          </div>
          <div className="flex flex-wrap gap-4 text-sm text-slate-500">
            <a href="#" className="hover:text-blue-600">
              개인정보처리방침
            </a>
            <a href="#" className="hover:text-blue-600">
              이용약관
            </a>
            <a href="#" className="hover:text-blue-600">
              문의하기
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}