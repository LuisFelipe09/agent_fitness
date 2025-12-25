import React, { useState, useEffect } from 'react';
import { Box, Typography, TextField, Button, Paper } from '@mui/material';
import { api } from '../services/api';
import { useTelegram } from '../hooks/useTelegram';

const Comments = ({ planId, planType }) => {
  const { userId } = useTelegram();
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');

  const loadComments = async () => {
    try {
      const res = await api.get(`/plans/${planId}/comments`, userId);
      setComments(res);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadComments();
  }, [planId]);

  const handlePost = async () => {
    if (!newComment.trim()) return;
    try {
      await api.post(`/plans/${planId}/comments?plan_type=${planType}`, {
        content: newComment,
        is_internal: false
      }, userId);
      setNewComment('');
      loadComments();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>Comments</Typography>
      <Box sx={{ maxHeight: 300, overflow: 'auto', mb: 2 }}>
        {comments.length === 0 && <Typography variant="body2" color="text.secondary">No comments yet.</Typography>}
        {comments.map((c) => (
          <Paper key={c.id} sx={{ p: 1, mb: 1, bgcolor: c.is_internal ? '#fff3e0' : 'white' }}>
             <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="subtitle2" fontWeight="bold">{c.author_role}</Typography>
                <Typography variant="caption">{new Date(c.created_at).toLocaleString()}</Typography>
             </Box>
             <Typography variant="body2">{c.content}</Typography>
          </Paper>
        ))}
      </Box>
      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Add a comment..."
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
        />
        <Button variant="contained" onClick={handlePost}>Post</Button>
      </Box>
    </Box>
  );
};

export default Comments;
