import React, { useState, useEffect } from 'react';
import {
  AppBar, Toolbar, Typography, IconButton, Box, Badge, Menu, MenuItem,
  Avatar, Divider, ListItemIcon, ListItemText, Button, Chip,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import NotificationsIcon from '@mui/icons-material/Notifications';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import LogoutIcon from '@mui/icons-material/Logout';
import SupportAgentIcon from '@mui/icons-material/SupportAgent';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import agentService from '../services/agentService';

const AgentNavbar = ({ onDrawerToggle }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [anchorElUser, setAnchorElUser] = useState(null);
  const [anchorElNotif, setAnchorElNotif] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const fetchNotifs = async () => {
    try {
      const data = await agentService.getNotifications();
      setNotifications(data.items?.slice(0, 5) || []);
      setUnreadCount(data.unread_count || 0);
    } catch (e) {}
  };

  useEffect(() => {
    fetchNotifs();
    const interval = setInterval(fetchNotifs, 20000);
    return () => clearInterval(interval);
  }, []);

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <AppBar position="sticky" elevation={0} sx={{ backgroundColor: '#ffffff', color: '#0f172a', borderBottom: '1px solid #e2e8f0', zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar sx={{ justifyContent: 'space-between', px: { xs: 2, sm: 3 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <IconButton color="inherit" edge="start" onClick={onDrawerToggle} sx={{ display: { md: 'none' } }}><MenuIcon /></IconButton>
          <Box component={Link} to="/agent/dashboard" sx={{ display: 'flex', alignItems: 'center', gap: 1.2, textDecoration: 'none', color: 'inherit' }}>
            <Box sx={{ width: 38, height: 38, borderRadius: 2, bgcolor: 'primary.main', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><SupportAgentIcon sx={{ color: '#fff', fontSize: 20 }} /></Box>
            <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
              <Typography variant="body2" fontWeight="700" sx={{ color: '#0f172a', lineHeight: 1.2 }}>SecureCare</Typography>
              <Typography variant="caption" color="text.secondary">Agent Portal</Typography>
            </Box>
          </Box>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Chip icon={<SupportAgentIcon sx={{ fontSize: '16px !important' }} />} label="AGENT" size="small" color="primary" sx={{ fontWeight: 700, display: { xs: 'none', sm: 'inline-flex' } }} />
          <IconButton onClick={(e) => setAnchorElNotif(e.currentTarget)} sx={{ p: 0.5 }}><Badge badgeContent={unreadCount} color="error"><NotificationsIcon /></Badge></IconButton>
          <Menu anchorEl={anchorElNotif} open={Boolean(anchorElNotif)} onClose={() => setAnchorElNotif(null)} PaperProps={{ sx: { width: 320, borderRadius: 2, mt: 1.5 } }}>
            <Box sx={{ px: 2, py: 1.5, borderBottom: '1px solid #e2e8f0' }}><Typography variant="subtitle2" fontWeight="700">Notifications</Typography></Box>
            {notifications.length === 0 ? (<MenuItem disabled><Typography variant="body2" color="text.secondary">No notifications</Typography></MenuItem>) : (notifications.map((n) => (<MenuItem key={n.id} onClick={() => { setAnchorElNotif(null); navigate(n.link || '/agent/notifications'); }} sx={{ bgcolor: n.is_read ? 'transparent' : '#f0f9ff', py: 1 }}><Box><Typography variant="body2" fontWeight="600">{n.title}</Typography><Typography variant="caption" color="text.secondary" noWrap sx={{ maxWidth: 250, display: 'block' }}>{n.message}</Typography></Box></MenuItem>)))}
            <Divider />
            <Box sx={{ p: 1, textAlign: 'center' }}><Button component={Link} to="/agent/notifications" onClick={() => setAnchorElNotif(null)} size="small" fullWidth sx={{ textTransform: 'none', fontWeight: 600 }}>View All Notifications</Button></Box>
          </Menu>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ display: { xs: 'none', sm: 'block' }, textAlign: 'right' }}>
              <Typography variant="body2" fontWeight="700" sx={{ color: '#0f172a', lineHeight: 1.2 }}>{user?.full_name || 'Agent'}</Typography>
              <Typography variant="caption" color="text.secondary">Insurance Agent</Typography>
            </Box>
            <IconButton onClick={(e) => setAnchorElUser(e.currentTarget)} sx={{ p: 0.5 }}><Avatar sx={{ bgcolor: 'primary.main', width: 38, height: 38, fontSize: '0.95rem', fontWeight: 700 }}>{user?.full_name?.charAt(0) || 'A'}</Avatar></IconButton>
          </Box>
          <Menu anchorEl={anchorElUser} open={Boolean(anchorElUser)} onClose={() => setAnchorElUser(null)} PaperProps={{ sx: { width: 220, mt: 1.5, borderRadius: 2 } }}>
            <Box sx={{ px: 2, py: 1.5 }}><Typography variant="subtitle2" fontWeight="700">{user?.full_name}</Typography><Typography variant="caption" color="text.secondary" sx={{ display: 'block', wordBreak: 'break-all' }}>{user?.email}</Typography></Box>
            <Divider />
            <MenuItem onClick={() => { setAnchorElUser(null); navigate('/agent/profile'); }}><ListItemIcon><AccountCircleIcon fontSize="small" /></ListItemIcon><ListItemText primary="My Profile" /></MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}><ListItemIcon sx={{ color: 'error.main' }}><LogoutIcon fontSize="small" /></ListItemIcon><ListItemText primary="Logout" /></MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default AgentNavbar;
