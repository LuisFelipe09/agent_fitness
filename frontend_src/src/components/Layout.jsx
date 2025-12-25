import React, { useState } from 'react';
import { useTelegram } from '../hooks/useTelegram';
import { Bell, Menu, User, History } from 'lucide-react';
import { AppBar, Toolbar, Typography, IconButton, Badge, Container, Box, Menu as MuiMenu, MenuItem } from '@mui/material';

const Layout = ({ children, unreadCount, notifications, onMarkRead, onChangeView }) => {
  const { username } = useTelegram();
  const [anchorEl, setAnchorEl] = useState(null);

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh', bgcolor: '#f5f5f5' }}>
      <AppBar position="static" color="primary" enableColorOnDark>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Fitness Agent
          </Typography>

          <IconButton
            size="large"
            aria-label="show notifications"
            color="inherit"
            onClick={handleMenu}
          >
            <Badge badgeContent={unreadCount} color="error">
              <Bell />
            </Badge>
          </IconButton>

           <MuiMenu
            id="menu-appbar"
            anchorEl={anchorEl}
            anchorOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            keepMounted
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            open={Boolean(anchorEl)}
            onClose={handleClose}
          >
             {notifications.length === 0 ? (
                 <MenuItem onClick={handleClose}>No new notifications</MenuItem>
             ) : (
                 notifications.map((n) => (
                     <MenuItem key={n.id} onClick={() => { onMarkRead(n.id); }}>
                         <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                             <Typography variant="subtitle2">{n.title}</Typography>
                             <Typography variant="caption">{n.message}</Typography>
                         </Box>
                     </MenuItem>
                 ))
             )}
          </MuiMenu>
        </Toolbar>
      </AppBar>

      <Container maxWidth="sm" sx={{ mt: 2, pb: 10 }}>
        {children}
      </Container>

      {/* Simple Bottom Nav for context switching if needed, or just keep it simple */}
      <Box sx={{ position: 'fixed', bottom: 0, left: 0, right: 0, bgcolor: 'white', borderTop: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-around', p: 1 }}>
          <IconButton onClick={() => onChangeView('home')} color="primary"><User size={24} /></IconButton>
          <IconButton onClick={() => onChangeView('history')} color="primary"><History size={24} /></IconButton>
      </Box>
    </Box>
  );
};

export default Layout;
