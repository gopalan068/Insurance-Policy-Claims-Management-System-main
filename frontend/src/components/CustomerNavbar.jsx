import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Badge,
  Menu,
  MenuItem,
  Avatar,
  Divider,
  ListItemIcon,
  ListItemText,
  Button,
  Chip,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import NotificationsIcon from '@mui/icons-material/Notifications';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import LogoutIcon from '@mui/icons-material/Logout';
import PolicyIcon from '@mui/icons-material/Policy';
import ShieldIcon from '@mui/icons-material/Shield';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useNavigate, Link } from 'react-router-dom';

import { useAuth } from '../context/AuthContext';
import customerService from '../services/customerService';

const CustomerNavbar = ({ onDrawerToggle }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [anchorElUser, setAnchorElUser] = useState(null);
  const [anchorElNotif, setAnchorElNotif] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const fetchNotifs = async () => {
    try {
      const data = await customerService.getNotifications();
      setNotifications(data.items.slice(0, 5) || []);
      setUnreadCount(data.unread_count || 0);
    } catch (e) {
      // Non-critical
    }
  };

  useEffect(() => {
    fetchNotifs();
    const interval = setInterval(fetchNotifs, 20000);
    return () => clearInterval(interval);
  }, []);

  const handleOpenUserMenu = (event) => {
    setAnchorElUser(event.currentTarget);
  };

  const handleCloseUserMenu = () => {
    setAnchorElUser(null);
  };

  const handleOpenNotifMenu = (event) => {
    setAnchorElNotif(event.currentTarget);
  };

  const handleCloseNotifMenu = () => {
    setAnchorElNotif(null);
  };

  const handleLogout = () => {
    handleCloseUserMenu();
    logout();
    navigate('/login');
  };

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        backgroundColor: '#ffffff',
        color: '#0f172a',
        borderBottom: '1px solid #e2e8f0',
        zIndex: (theme) => theme.zIndex.drawer + 1,
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between', px: { xs: 2, sm: 3 } }}>
        {/* Left: Mobile Toggle & Brand */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={onDrawerToggle}
            sx={{ display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>

          <Box
            component={Link}
            to="/customer/dashboard"
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1.2,
              textDecoration: 'none',
              color: 'inherit',
            }}
          >
            <Box
              sx={{
                width: 38,
                height: 38,
                borderRadius: 2,
                bgcolor: 'primary.main',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
              }}
            >
              <ShieldIcon sx={{ fontSize: 22 }} />
            </Box>
            <Box>
              <Typography variant="subtitle1" fontWeight="800" sx={{ lineHeight: 1.1, color: '#0f172a' }}>
                SecureCare
              </Typography>
              <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 700, letterSpacing: '0.04em' }}>
                CUSTOMER PORTAL
              </Typography>
            </Box>
          </Box>
        </Box>

        {/* Right: Notifications & Profile */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: { xs: 1, sm: 2 } }}>
          {/* Notification Bell */}
          <IconButton onClick={handleOpenNotifMenu} sx={{ color: '#475569' }}>
            <Badge badgeContent={unreadCount} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>

          {/* Notifications Dropdown */}
          <Menu
            anchorEl={anchorElNotif}
            open={Boolean(anchorElNotif)}
            onClose={handleCloseNotifMenu}
            PaperProps={{
              sx: { width: 340, maxHeight: 420, mt: 1.5, borderRadius: 2, boxShadow: '0 10px 25px rgba(0,0,0,0.1)' },
            }}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          >
            <Box sx={{ px: 2, py: 1.5, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="subtitle2" fontWeight="700">
                Notifications
              </Typography>
              {unreadCount > 0 && <Chip label={`${unreadCount} New`} size="small" color="error" sx={{ height: 20, fontSize: '0.7rem' }} />}
            </Box>
            <Divider />

            {notifications.length === 0 ? (
              <Box sx={{ p: 3, textAlign: 'center', color: 'text.secondary' }}>
                <Typography variant="body2">No notifications</Typography>
              </Box>
            ) : (
              notifications.map((n) => (
                <MenuItem
                  key={n.id}
                  onClick={() => {
                    handleCloseNotifMenu();
                    if (n.link) navigate(n.link);
                  }}
                  sx={{
                    py: 1.2,
                    px: 2,
                    bgcolor: n.is_read ? 'transparent' : '#f0fdf4',
                    borderBottom: '1px solid #f1f5f9',
                    whiteSpace: 'normal',
                  }}
                >
                  <Box>
                    <Typography variant="body2" fontWeight={n.is_read ? 600 : 700} color={n.is_read ? 'text.primary' : 'primary.main'}>
                      {n.title}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.3 }}>
                      {n.message}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#94a3b8', fontSize: '0.7rem', display: 'block', mt: 0.4 }}>
                      {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </Typography>
                  </Box>
                </MenuItem>
              ))
            )}

            <Divider />
            <Box sx={{ p: 1, textAlign: 'center' }}>
              <Button
                component={Link}
                to="/customer/notifications"
                onClick={handleCloseNotifMenu}
                size="small"
                fullWidth
                sx={{ textTransform: 'none', fontWeight: 600 }}
              >
                View All Notifications
              </Button>
            </Box>
          </Menu>

          {/* Profile Dropdown */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ display: { xs: 'none', sm: 'block' }, textAlign: 'right' }}>
              <Typography variant="body2" fontWeight="700" sx={{ color: '#0f172a', lineHeight: 1.2 }}>
                {user?.full_name || 'Customer'}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Policyholder
              </Typography>
            </Box>

            <IconButton onClick={handleOpenUserMenu} sx={{ p: 0.5 }}>
              <Avatar sx={{ bgcolor: 'primary.main', width: 38, height: 38, fontSize: '0.95rem', fontWeight: 700 }}>
                {user?.full_name?.charAt(0) || 'C'}
              </Avatar>
            </IconButton>
          </Box>

          <Menu
            anchorEl={anchorElUser}
            open={Boolean(anchorElUser)}
            onClose={handleCloseUserMenu}
            PaperProps={{
              sx: { width: 220, mt: 1.5, borderRadius: 2, boxShadow: '0 10px 25px rgba(0,0,0,0.1)' },
            }}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          >
            <Box sx={{ px: 2, py: 1.5 }}>
              <Typography variant="subtitle2" fontWeight="700">
                {user?.full_name}
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', wordBreak: 'break-all' }}>
                {user?.email}
              </Typography>
            </Box>
            <Divider />

            <MenuItem
              onClick={() => {
                handleCloseUserMenu();
                navigate('/customer/profile');
              }}
            >
              <ListItemIcon>
                <AccountCircleIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText primary="My Profile" />
            </MenuItem>

            <MenuItem
              onClick={() => {
                handleCloseUserMenu();
                navigate('/customer/policies/my');
              }}
            >
              <ListItemIcon>
                <PolicyIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText primary="My Subscriptions" />
            </MenuItem>

            <Divider />

            <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
              <ListItemIcon sx={{ color: 'error.main' }}>
                <LogoutIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText primary="Logout" />
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default CustomerNavbar;
