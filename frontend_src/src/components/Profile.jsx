import React, { useState, useEffect } from 'react';
import { TextField, Button, Select, MenuItem, FormControl, InputLabel, Card, CardContent, Typography, Grid } from '@mui/material';
import { api } from '../services/api';
import { useTelegram } from '../hooks/useTelegram';

const Profile = ({ onSave }) => {
  const { userId } = useTelegram();
  const [profile, setProfile] = useState({
    age: 30,
    weight: 70,
    height: 175,
    gender: 'male',
    goal: 'muscle_gain',
    activity_level: 'moderate',
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setProfile({ ...profile, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await api.put(`/users/${userId}/profile`, profile, userId);
      alert('Profile saved!');
      if (onSave) onSave();
    } catch (e) {
      console.error(e);
      alert('Error saving profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h5" gutterBottom>Profile</Typography>
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <TextField label="Age" name="age" type="number" fullWidth value={profile.age} onChange={handleChange} />
          </Grid>
          <Grid item xs={6}>
            <TextField label="Weight (kg)" name="weight" type="number" fullWidth value={profile.weight} onChange={handleChange} />
          </Grid>
           <Grid item xs={6}>
            <TextField label="Height (cm)" name="height" type="number" fullWidth value={profile.height} onChange={handleChange} />
          </Grid>
          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Gender</InputLabel>
              <Select name="gender" value={profile.gender} label="Gender" onChange={handleChange}>
                <MenuItem value="male">Male</MenuItem>
                <MenuItem value="female">Female</MenuItem>
                <MenuItem value="other">Other</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Goal</InputLabel>
              <Select name="goal" value={profile.goal} label="Goal" onChange={handleChange}>
                <MenuItem value="weight_loss">Weight Loss</MenuItem>
                <MenuItem value="muscle_gain">Muscle Gain</MenuItem>
                <MenuItem value="maintenance">Maintenance</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
             <FormControl fullWidth>
              <InputLabel>Activity Level</InputLabel>
              <Select name="activity_level" value={profile.activity_level} label="Activity Level" onChange={handleChange}>
                <MenuItem value="sedentary">Sedentary</MenuItem>
                <MenuItem value="moderate">Moderate</MenuItem>
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="very_active">Very Active</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <Button variant="contained" fullWidth onClick={handleSubmit} disabled={loading}>
              {loading ? 'Saving...' : 'Save Profile'}
            </Button>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default Profile;
