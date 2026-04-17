import { Routes, Route } from 'react-router-dom'
import MainPage from './pages/MainPage'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import ResultPage from './pages/ResultPage'
import MyTripsPage from './pages/MyTripsPage'
import TripDetailPage from './pages/TripDetailPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<MainPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/recommend-result" element={<ResultPage />} />
      <Route path="/my-trips" element={<MyTripsPage />} />
      <Route path="/trip/:id" element={<TripDetailPage />} />
    </Routes>
  )
}