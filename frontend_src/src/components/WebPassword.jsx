import React, { useState } from 'react';
import { Card, CardContent, Typography, TextField, Button, Alert } from '@mui/material';
import { api } from '../services/api';
import { useTelegram } from '../hooks/useTelegram';

const WebPassword = () => {
  const { userId } = useTelegram();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const handleSetPassword = async () => {
    if (!password) {
      setError("Password is required");
      return;
    }
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      await api.post('/auth/set-password', {
        email: email || null,
        password: password
      }, userId);
      setMessage("Password set successfully! You can now login via web.");
      setPassword('');
      setEmail('');
    } catch (e) {
      console.error(e);
      setError(e.message || "Error setting password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>Web Access</Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Set a password to access your account via the web interface outside of Telegram.
        </Typography>

        {message && <Alert severity="success" sx={{ mb: 2 }}>{message}</Alert>}
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        <TextField
          label="Email (Optional)"
          fullWidth
          margin="normal"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <TextField
          label="New Password"
          type="password"
          fullWidth
          margin="normal"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <Button
          variant="outlined"
          fullWidth
          onClick={handleSetPassword}
          disabled={loading}
          sx={{ mt: 1 }}
        >
          {loading ? 'Setting...' : 'Set Password'}
        </Button>
      </CardContent>
    </Card>
  );
};

export default WebPassword;
