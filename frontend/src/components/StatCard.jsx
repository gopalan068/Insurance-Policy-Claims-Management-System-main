import React from 'react';
import { Card, CardContent, Typography, Box, Avatar } from '@mui/material';

const StatCard = ({ title, value, icon, color = 'primary', subtitle, trend }) => {
  const colorMap = {
    primary: { bg: '#eff6ff', text: '#1d4ed8', border: '#bfdbfe' },
    secondary: { bg: '#f0fdfa', text: '#0f766e', border: '#99f6e4' },
    success: { bg: '#ecfdf5', text: '#047857', border: '#a7f3d0' },
    warning: { bg: '#fffbeb', text: '#b45309', border: '#fde68a' },
    error: { bg: '#fef2f2', text: '#b91c1c', border: '#fecaca' },
    info: { bg: '#f0f9ff', text: '#0369a1', border: '#bae6fd' },
  };

  const themeColors = colorMap[color] || colorMap.primary;

  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        transition: 'transform 0.2s ease, box-shadow 0.2s ease',
        '&:hover': {
          transform: 'translateY(-3px)',
          boxShadow: '0 10px 20px -5px rgba(0,0,0,0.07)',
        },
      }}
    >
      <CardContent sx={{ p: 2.5, '&:last-child': { pb: 2.5 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1.5 }}>
          <Typography variant="body2" color="text.secondary" fontWeight="600" sx={{ textTransform: 'uppercase', letterSpacing: '0.04em', fontSize: '0.75rem' }}>
            {title}
          </Typography>
          <Avatar
            variant="rounded"
            sx={{
              bgcolor: themeColors.bg,
              color: themeColors.text,
              border: `1px solid ${themeColors.border}`,
              width: 42,
              height: 42,
            }}
          >
            {icon}
          </Avatar>
        </Box>

        <Typography variant="h4" fontWeight="800" sx={{ color: '#0f172a', mb: 0.5 }}>
          {value}
        </Typography>

        {(subtitle || trend) && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
            {trend && (
              <Typography variant="caption" sx={{ color: themeColors.text, fontWeight: 700 }}>
                {trend}
              </Typography>
            )}
            {subtitle && (
              <Typography variant="caption" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default StatCard;
