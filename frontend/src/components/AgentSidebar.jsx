import React from 'react';
import {
  Drawer, List, ListItem, ListItemButton, ListItemIcon,
  ListItemText, Typography, Box, Divider,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import PeopleIcon from '@mui/icons-material/People';
import SecurityIcon from '@mui/icons-material/Security';
import AssignmentIcon from '@mui/icons-material/Assignment';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import PersonIcon from '@mui/icons-material/Person';
import SupportAgentIcon from '@mui/icons-material/SupportAgent';
import { useLocation, useNavigate } from 'react-router-dom';

const DRAWER_WIDTH = 260;

const MENU_ITEMS = [
  { label: 'Dashboard', path: '/agent/dashboard', icon: <DashboardIcon /> },
  { label: 'My Customers', path: '/agent/customers', icon: <PeopleIcon /> },
  { label: 'Policies', path: '/agent/purchases', icon: <SecurityIcon /> },
  { label: 'Claims', path: '/agent/claims', icon: <AssignmentIcon /> },
  { label: 'Notifications', path: '/agent/notifications', icon: <NotificationsActiveIcon /> },
  { label: 'My Profile', path: '/agent/profile', icon: <PersonIcon /> },
];

const AgentSidebar = ({ mobileOpen, onDrawerToggle }) => {
  const location = useLocation();
  const navigate = useNavigate();

  const handleNavigate = (path) => {
    navigate(path);
    if (mobileOpen && onDrawerToggle) onDrawerToggle();
  };

  const isSelected = (path) => location.pathname === path;

  const drawerContent = (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Box sx={{ p: 2.5, display: { xs: 'block', md: 'none' } }}>
        <Typography variant="h6" fontWeight="800" color="primary.main">SecureCare Portal</Typography>
      </Box>
      <Divider sx={{ display: { xs: 'block', md: 'none' } }} />
      <Box sx={{ p: 2, flexGrow: 1, overflowY: 'auto' }}>
        <Typography variant="caption" sx={{ px: 1.5, py: 1, display: 'block', fontWeight: 700, color: '#94a3b8', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
          Agent Menu
        </Typography>
        <List sx={{ pt: 0.5 }}>
          {MENU_ITEMS.map((item) => {
            const active = isSelected(item.path);
            return (
              <ListItem key={item.path} disablePadding sx={{ mb: 0.8 }}>
                <ListItemButton
                  onClick={() => handleNavigate(item.path)}
                  sx={{
                    borderRadius: 2, py: 1, px: 1.8,
                    bgcolor: active ? 'rgba(37, 99, 235, 0.08)' : 'transparent',
                    color: active ? 'primary.main' : '#475569',
                    fontWeight: active ? 700 : 500,
                    '&:hover': { bgcolor: active ? 'rgba(37, 99, 235, 0.12)' : 'rgba(0, 0, 0, 0.04)' },
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 38, color: active ? 'primary.main' : '#64748b' }}>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.label} primaryTypographyProps={{ fontSize: '0.9rem', fontWeight: active ? 700 : 500 }} />
                </ListItemButton>
              </ListItem>
            );
          })}
        </List>
      </Box>
      <Box sx={{ p: 2, m: 2, bgcolor: '#eff6ff', borderRadius: 3, border: '1px solid #bfdbfe' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
          <SupportAgentIcon sx={{ fontSize: 18, color: '#1d4ed8' }} />
          <Typography variant="subtitle2" fontWeight="700" color="primary.dark">Agent Center</Typography>
        </Box>
        <Typography variant="caption" color="text.secondary">Manage your customers and policy activities.</Typography>
      </Box>
    </Box>
  );

  return (
    <Box component="nav" sx={{ width: { md: DRAWER_WIDTH }, flexShrink: { md: 0 } }}>
      <Drawer variant="temporary" open={mobileOpen} onClose={onDrawerToggle} ModalProps={{ keepMounted: true }} sx={{ display: { xs: 'block', md: 'none' }, '& .MuiDrawer-paper': { boxSizing: 'border-box', width: DRAWER_WIDTH } }}>
        {drawerContent}
      </Drawer>
      <Drawer variant="permanent" sx={{ display: { xs: 'none', md: 'block' }, '& .MuiDrawer-paper': { boxSizing: 'border-box', width: DRAWER_WIDTH, borderRight: '1px solid #e2e8f0', top: 64, height: 'calc(100% - 64px)' } }} open>
        {drawerContent}
      </Drawer>
    </Box>
  );
};

export default AgentSidebar;
