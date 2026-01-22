import { useState, useEffect } from 'react'
import { useTelegram } from './hooks/use-telegram'
import WelcomeScreen from './components/WelcomeScreen'
import RoleSelector from './components/RoleSelector'
import AthleteDashboard from './components/AthleteDashboard'
import CoachDashboard from './components/CoachDashboard'

type UserRole = 'athlete' | 'coach' | null

function App() {
  const { user, webApp } = useTelegram()
  const [currentRole, setCurrentRole] = useState<UserRole>(null)
  const [showWelcome, setShowWelcome] = useState(true)

  useEffect(() => {
    // Configure Telegram Web App
    if (webApp) {
      webApp.ready()
      webApp.expand()
    }
  }, [webApp])

  const handleWelcomeComplete = () => {
    setShowWelcome(false)
  }

  const handleRoleSelect = (role: UserRole) => {
    setCurrentRole(role)
  }

  if (showWelcome) {
    return <WelcomeScreen onComplete={handleWelcomeComplete} />
  }

  if (!currentRole) {
    return <RoleSelector onRoleSelect={handleRoleSelect} />
  }

  return (
    <div className="min-h-screen bg-background">
      {currentRole === 'athlete' ? (
        <AthleteDashboard userId={user?.id.toString() || 'demo'} />
      ) : (
        <CoachDashboard userId={user?.id.toString() || 'demo'} />
      )}
    </div>
  )
}

export default App
