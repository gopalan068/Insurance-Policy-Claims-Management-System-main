import React from 'react';
import {
  Drawer, List, ListItem, ListItemButton, ListItemIcon,
  ListItemText, Typography, Box, Divider,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AssignmentIcon from '@mui/icons-material/Assignment';
import RateReviewIcon from '@mui/icons-material/RateReview';
import HistoryToggleOffIcon from '@mui/icons-material/HistoryToggleOff';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import PersonIcon from '@mui/icons-material/Person';
import GavelIcon from '@mui/icons-material/Gavel';
import { useLocation, useNavigate } from 'react-router-dom';

const DRAWER_WIDTH = 260;

const MENU_ITEMS = [
  { label: 'Dashboard', path: '/officer/dashboard', icon: <DashboardIcon /> },
  { label: 'All Claims', path: '/officer/claims', icon: <AssignmentIcon /> },
  { label: 'Pending Reviews', path: '/officer/claims?status=SUBMITTED', icon: <RateReviewIcon /> },
  { label: 'Review History', path: '/officer/reviews', icon: <HistoryToggleOffIcon /> },
  { label: 'Notifications', path: '/officer/notifications', icon: <NotificationsActiveIcon /> },
  { label: 'My Profile', path: '/officer/profile', icon: <PersonIcon /> },
];

const OfficerSidebar = ({ mobileOpen, onDrawerToggle }) => {
  const location = useLocation();
  const navigate = useNavigate();

  const handleNavigate = (path) => {
    navigate(path);
    if (mobileOpen && onDrawerToggle) onDrawerToggle();
  };

  const isSelected = (path) => {
    if (path.includes('?')) {
      const [basePath, query] = path.split('?');
      return location.pathname === basePath && location.search.includes(query);
    }
    return location.pathname === path;
  };

  const drawerContent = (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Box sx={{ p: 2.5, display: { xs: 'block', md: 'none' } }}>
        <Typography variant="h6" fontWeight="800" color="secondary.main">SecureCare Portal</Typography>
      </Box>
      <Divider sx={{ display: { xs: 'block', md: 'none' } }} />
      <Box sx={{ p: 2, flexGrow: 1, overflowY: 'auto' }}>
        <Typography variant="caption" sx={{ px: 1.5, py: 1, display: 'block', fontWeight: 700, color: '#94a3b8', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
          Claims Officer Menu
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
                    bgcolor: active ? 'rgba(15, 118, 110, 0.08)' : 'transparent',
                    color: active ? 'secondary.main' : '#475569',
                    fontWeight: active ? 700 : 500,
                    '&:hover': { bgcolor: active ? 'rgba(15, 118, 110, 0.12)' : 'rgba(0, 0, 0, 0.04)' },
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 38, color: active ? 'secondary.main' : '#64748b' }}>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.label} primaryTypographyProps={{ fontSize: '0.9rem', fontWeight: active ? 700 : 500 }} />
                </ListItemButton>
              </ListItem>
            );
          })}
        </List>
      </Box>
      <Box sx={{ p: 2, m: 2, bgcolor: '#f0fdfa', borderRadius: 3, border: '1px solid #ccfbf1' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
          <GavelIcon sx={{ fontSize: 18, color: '#0f766e' }} />
          <Typography variant="subtitle2" fontWeight="700" color="secondary.dark">Claims Center</Typography>
        </Box>
        <Typography variant="caption" color="text.secondary">Review and process policyholder claims efficiently.</Typography>
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

export default OfficerSidebar;
