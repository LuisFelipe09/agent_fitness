import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Chip, Box, Divider, Button, Collapse, List, ListItem, ListItemText } from '@mui/material';
import { api } from '../services/api';
import { useTelegram } from '../hooks/useTelegram';
import Comments from './Comments';

const PlanView = ({ plan, type }) => {
  const { userId } = useTelegram();
  const [showVersions, setShowVersions] = useState(false);
  const [versions, setVersions] = useState([]);

  const loadVersions = async () => {
    if (!showVersions && versions.length === 0) {
      try {
        const res = await api.get(`/plans/${plan.id}/versions`, userId);
        setVersions(res);
      } catch (e) {
        console.error(e);
      }
    }
    setShowVersions(!showVersions);
  };

  const badgeColor = {
    draft: 'default',
    approved: 'success',
    active: 'primary',
    archived: 'error'
  }[plan.state || 'draft'] || 'default';

  return (
    <Box sx={{ mt: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5">Your {type === 'workout' ? 'Workout' : 'Nutrition'} Plan</Typography>
        <Chip label={plan.state || 'DRAFT'} color={badgeColor} />
      </Box>

      <Typography variant="caption" display="block" color="text.secondary" gutterBottom>
        Created: {new Date(plan.created_at).toLocaleDateString()}
      </Typography>

      {type === 'workout' && plan.sessions.map((s, i) => (
        <Card key={i} sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6">{s.day} - {s.focus}</Typography>
            <ul>
              {s.exercises.map((e, idx) => (
                <li key={idx}>{e.name}: {e.sets}x{e.reps}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      ))}

      {type === 'nutrition' && plan.daily_plans.map((d, i) => (
        <Card key={i} sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6">{d.day}</Typography>
            <ul>
              {d.meals.map((m, idx) => (
                <li key={idx}>{m.name} ({m.calories} kcal)</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      ))}

      <Divider sx={{ my: 2 }} />

      <Button onClick={loadVersions} size="small">
        {showVersions ? 'Hide History' : 'View Version History'}
      </Button>

      <Collapse in={showVersions}>
        <List dense>
            {versions.length === 0 && <ListItem><ListItemText primary="No history available." /></ListItem>}
            {versions.map((v) => (
                <ListItem key={v.id}>
                    <ListItemText primary={`v${v.version_number} - ${v.changes_summary || 'Update'}`} secondary={new Date(v.created_at).toLocaleDateString()} />
                </ListItem>
            ))}
        </List>
      </Collapse>

      <Divider sx={{ my: 2 }} />

      <Comments planId={plan.id} planType={type} />
    </Box>
  );
};

export default PlanView;
