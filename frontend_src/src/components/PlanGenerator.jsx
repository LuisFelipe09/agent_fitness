import React from 'react';
import { Button, Grid, Box } from '@mui/material';
import { Dumbbell, Utensils } from 'lucide-react';

const PlanGenerator = ({ onGenerateWorkout, onGenerateNutrition, loading }) => {
  return (
    <Box sx={{ my: 3 }}>
      <Grid container spacing={2}>
        <Grid item xs={6}>
          <Button
            variant="contained"
            color="secondary"
            fullWidth
            startIcon={<Dumbbell />}
            onClick={onGenerateWorkout}
            disabled={loading}
            sx={{ height: '100px' }}
          >
            Generate Workout
          </Button>
        </Grid>
        <Grid item xs={6}>
          <Button
            variant="contained"
            color="success"
            fullWidth
            startIcon={<Utensils />}
            onClick={onGenerateNutrition}
            disabled={loading}
            sx={{ height: '100px' }}
          >
            Generate Nutrition
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
};

export default PlanGenerator;
