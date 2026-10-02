import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Divider,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import PeopleAltIcon from '@mui/icons-material/PeopleAlt';
import GroupIcon from '@mui/icons-material/Group';
import SupportAgentIcon from '@mui/icons-material/SupportAgent';
import FactCheckIcon from '@mui/icons-material/FactCheck';
import PolicyIcon from '@mui/icons-material/Policy';
import ShoppingCartCheckoutIcon from '@mui/icons-material/ShoppingCartCheckout';
import AssignmentIcon from '@mui/icons-material/Assignment';
import FolderSharedIcon from '@mui/icons-material/FolderShared';
import InsightsIcon from '@mui/icons-material/Insights';
import HistoryToggleOffIcon from '@mui/icons-material/HistoryToggleOff';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';

export const DRAWER_WIDTH = 260;

const menuSections = [
  {
    title: 'CORE MONITORING',
    items: [
      { text: 'Dashboard', path: '/admin/dashboard', icon: <DashboardIcon /> },
      { text: 'Reports & Analytics', path: '/admin/reports', icon: <InsightsIcon /> },
    ],
  },
  {
    title: 'USER & STAKEHOLDERS',
    items: [
      { text: 'All Users', path: '/admin/users', icon: <PeopleAltIcon /> },
      { text: 'Customers', path: '/admin/customers', icon: <GroupIcon /> },
      { text: 'Agents', path: '/admin/agents', icon: <SupportAgentIcon /> },
      { text: 'Claims Officers', path: '/admin/claims-officers', icon: <FactCheckIcon /> },
    ],
  },
  {
    title: 'POLICY OPERATIONS',
    items: [
      { text: 'Insurance Policies', path: '/admin/policies', icon: <PolicyIcon /> },
      { text: 'Policy Purchases', path: '/admin/policy-purchases', icon: <ShoppingCartCheckoutIcon /> },
    ],
  },
  {
    title: 'CLAIMS & COMPLIANCE',
    items: [
      { text: 'Claims Monitoring', path: '/admin/claims', icon: <AssignmentIcon /> },
      { text: 'Claim Documents', path: '/admin/documents', icon: <FolderSharedIcon /> },
      { text: 'System Audit Logs', path: '/admin/audit-logs', icon: <HistoryToggleOffIcon /> },
    ],
  },
  {
    title: 'PREFERENCES',
    items: [
      { text: 'Admin Profile', path: '/admin/profile', icon: <AccountCircleIcon /> },
    ],
  },
];

const AdminSidebar = ({ mobileOpen, onDrawerToggle }) => {
  const location = useLocation();
  const navigate = useNavigate();

  const handleItemClick = (path) => {
    navigate(path);
    if (mobileOpen) {
      onDrawerToggle();
    }
  };

  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', bgcolor: '#ffffff' }}>
      <Box sx={{ p: 2.5, display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <Box
          sx={{
            width: 38,
            height: 38,
            borderRadius: 2,
            bgcolor: 'primary.main',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ffffff',
            fontWeight: 800,
            fontSize: '1.1rem',
          }}
        >
          SC
        </Box>
        <Box>
          <Typography variant="subtitle1" fontWeight="800" sx={{ color: '#0f172a', lineHeight: 1.2 }}>
            SecureCare
          </Typography>
          <Typography variant="caption" color="text.secondary" fontWeight="600">
            ADMIN PORTAL v1.0
          </Typography>
        </Box>
      </Box>

      <Divider sx={{ borderColor: '#f1f5f9' }} />

      <Box sx={{ flexGrow: 1, overflowY: 'auto', py: 1.5, px: 1.5 }}>
        {menuSections.map((section, idx) => (
          <Box key={section.title} sx={{ mb: 2 }}>
            <Typography
              variant="caption"
              sx={{
                px: 2,
                py: 0.5,
                display: 'block',
                fontWeight: 700,
                color: '#94a3b8',
                letterSpacing: '0.06em',
                fontSize: '0.7rem',
              }}
            >
              {section.title}
            </Typography>
            <List disablePadding>
              {section.items.map((item) => {
                const isActive = location.pathname === item.path || (item.path !== '/admin/dashboard' && location.pathname.startsWith(item.path + '/'));
                return (
                  <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
                    <ListItemButton
                      onClick={() => handleItemClick(item.path)}
                      sx={{
                        borderRadius: 2,
                        py: 1,
                        px: 1.5,
                        bgcolor: isActive ? '#eff6ff' : 'transparent',
                        color: isActive ? 'primary.main' : 'text.secondary',
                        '&:hover': {
                          bgcolor: isActive ? '#dbeafe' : '#f8fafc',
                          color: isActive ? 'primary.dark' : 'text.primary',
                        },
                      }}
                    >
                      <ListItemIcon
                        sx={{
                          minWidth: 36,
                          color: isActive ? 'primary.main' : '#64748b',
                        }}
                      >
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText
                        primary={item.text}
                        primaryTypographyProps={{
                          fontSize: '0.875rem',
                          fontWeight: isActive ? 700 : 500,
                        }}
                      />
                    </ListItemButton>
                  </ListItem>
                );
              })}
            </List>
          </Box>
        ))}
      </Box>

      <Box sx={{ p: 2, bgcolor: '#f8fafc', borderTop: '1px solid #e2e8f0' }}>
        <Typography variant="caption" color="text.secondary" display="block" align="center">
          Team Insurance Management
        </Typography>
        <Typography variant="caption" color="text.secondary" display="block" align="center" fontWeight="600">
          Admin Module Active
        </Typography>
      </Box>
    </Box>
  );

  return (
    <>
      {/* Mobile temporary drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={onDrawerToggle}
        ModalProps={{ keepMounted: true }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: DRAWER_WIDTH },
        }}
      >
        {drawerContent}
      </Drawer>

      {/* Desktop permanent drawer */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', md: 'block' },
          width: DRAWER_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: DRAWER_WIDTH,
            borderRight: '1px solid #e2e8f0',
          },
        }}
        open
      >
        {drawerContent}
      </Drawer>
    </>
  );
};

export default AdminSidebar;
