import React, { useState, useEffect } from 'react';
import { useTelegram } from './hooks/useTelegram';
import { api } from './services/api';
import Layout from './components/Layout';
import Profile from './components/Profile';
import PlanGenerator from './components/PlanGenerator';
import PlanView from './components/PlanView';
import WebPassword from './components/WebPassword';
import { Typography, CircularProgress, Box, Divider } from '@mui/material';

function App() {
  const { userId, username } = useTelegram();
  const [currentPlan, setCurrentPlan] = useState(null);
  const [currentPlanType, setCurrentPlanType] = useState(null); // 'workout' | 'nutrition'
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState('home'); // 'home', 'history'

  useEffect(() => {
    // Init User
    const initUser = async () => {
      try {
        await api.post('/users/', { id: userId, username }, userId);
        loadNotifications();
      } catch (e) {
        console.error("Initialization error", e);
      }
    };
    initUser();
  }, [userId]);

  const loadNotifications = async () => {
    try {
      const res = await api.get('/notifications?unread_only=true', userId);
      setNotifications(res);
    } catch (e) {
      console.error(e);
    }
  };

  const handleMarkRead = async (id) => {
    try {
      await api.patch(`/notifications/${id}/read`, userId);
      loadNotifications();
    } catch (e) {
      console.error(e);
    }
  };

  const handleGenerateWorkout = async () => {
    setLoading(true);
    try {
      const plan = await api.post(`/users/${userId}/plans/workout`, {}, userId);
      setCurrentPlan(plan);
      setCurrentPlanType('workout');
    } catch (e) {
      alert("Error generating workout plan");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateNutrition = async () => {
    setLoading(true);
    try {
      const plan = await api.post(`/users/${userId}/plans/nutrition`, {}, userId);
      setCurrentPlan(plan);
      setCurrentPlanType('nutrition');
    } catch (e) {
      alert("Error generating nutrition plan");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout
        unreadCount={notifications.length}
        notifications={notifications}
        onMarkRead={handleMarkRead}
        onChangeView={setView}
    >
      {view === 'home' && (
          <>
            <Profile />
            <WebPassword />
            <Divider sx={{ my: 3 }} />
            <PlanGenerator
                onGenerateWorkout={handleGenerateWorkout}
                onGenerateNutrition={handleGenerateNutrition}
                loading={loading}
            />

            {loading && (
                <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
                    <CircularProgress />
                </Box>
            )}

            {currentPlan && !loading && (
                <PlanView plan={currentPlan} type={currentPlanType} />
            )}
          </>
      )}

      {view === 'history' && (
          <Box sx={{ textAlign: 'center', mt: 4 }}>
              <Typography color="text.secondary">History feature coming soon...</Typography>
          </Box>
      )}

    </Layout>
  );
}

export default App;
