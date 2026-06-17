import React, { useEffect, useState } from 'react'
import './App.css'
import Scene from "./components/3d/Scene"
import BottomBar from './components/ui/BottomBar'
import Header from './components/ui/Header'
import Onboarding from './components/ui/Onboarding'
import { useCoreStore } from '@/stores/useCoreStore'

function App() {
  const { userData, setUserData } = useCoreStore()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch("http://localhost:8000/api/user-data")
      .then((res) => res.json())
      .then((data) => {
        setUserData(data || {})
        setLoading(false)
      })
      .catch((err) => {
        console.error("Failed to fetch user data:", err)
        setLoading(false)
      })
  }, [setUserData])

  const handleOnboardingComplete = async (answers) => {
    try {
      const res = await fetch("http://localhost:8000/api/user-data", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(answers),
      })
      if (res.ok) {
        setUserData(answers)
      }
    } catch (err) {
      console.error("Failed to save onboarding data:", err)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        Loading...
      </div>
    )
  }

  const showOnboarding = !userData || !userData.name

  return (
    <div className="min-h-screen">
      <Scene />
      <Header />
      {!showOnboarding && <BottomBar />}
      {showOnboarding && <Onboarding onComplete={handleOnboardingComplete} />}
    </div>
  )
}

export default App
