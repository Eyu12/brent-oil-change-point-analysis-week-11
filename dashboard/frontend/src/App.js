import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Box,
  CssBaseline,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Container,
  Paper,
  Grid,
  Card,
  CardContent,
  Divider,
  Chip,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  ShowChart as ShowChartIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
  Event as EventIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Warning as WarningIcon
} from '@mui/icons-material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Import components
import PriceChart from './components/PriceChart';
import ChangePointAnalysis from './components/ChangePointAnalysis';
import EventImpactAnalyzer from './components/EventImpactAnalyzer';
import DashboardOverview from './components/DashboardOverview';
import api from './services/api';

const drawerWidth = 240;

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
});

function App() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [healthStatus, setHealthStatus] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  useEffect(() => {
    checkApiHealth();
    loadStatistics();
  }, []);

  const checkApiHealth = async () => {
    try {
      const response = await api.healthCheck();
      setHealthStatus(response);
    } catch (error) {
      console.error('API Health check failed:', error);
      setHealthStatus({ status: 'unhealthy', error: error.message });
    }
  };

  const loadStatistics = async () => {
    try {
      const response = await api.getStatistics();
      if (response.success) {
        setStatistics(response.statistics);
      }
    } catch (error) {
      console.error('Error loading statistics:', error);
    }
  };

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Price Chart', icon: <ShowChartIcon />, path: '/price-chart' },
    { text: 'Change Point Analysis', icon: <TimelineIcon />, path: '/change-points' },
    { text: 'Event Impact Analyzer', icon: <EventIcon />, path: '/event-impact' },
    { text: 'Statistics', icon: <AssessmentIcon />, path: '/statistics' },
  ];

  const drawer = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap>
          Brent Oil Analytics
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem
            button
            key={item.text}
            component="a"
            href={`#${item.path}`}
            onClick={() => window.location.hash = item.path}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
      <Divider />
      {healthStatus && (
        <Box sx={{ p: 2 }}>
          <Typography variant="caption" display="block" gutterBottom>
            API Status
          </Typography>
          <Chip
            label={healthStatus.status === 'healthy' ? 'API Healthy' : 'API Error'}
            color={healthStatus.status === 'healthy' ? 'success' : 'error'}
            size="small"
            sx={{ width: '100%' }}
          />
          {statistics && (
            <Typography variant="caption" display="block" sx={{ mt: 1 }}>
              {statistics.overall.count.toLocaleString()} data points
            </Typography>
          )}
        </Box>
      )}
    </div>
  );

  return (
    <ThemeProvider theme={theme}>
      <Router>
        <Box sx={{ display: 'flex' }}>
          <CssBaseline />
          
          <AppBar
            position="fixed"
            sx={{
              width: { sm: `calc(100% - ${drawerWidth}px)` },
              ml: { sm: `${drawerWidth}px` },
            }}
          >
            <Toolbar>
              <IconButton
                color="inherit"
                aria-label="open drawer"
                edge="start"
                onClick={handleDrawerToggle}
                sx={{ mr: 2, display: { sm: 'none' } }}
              >
                <MenuIcon />
              </IconButton>
              <Typography variant="h6" noWrap component="div">
                Brent Oil Price Analysis Dashboard
              </Typography>
              <Box sx={{ flexGrow: 1 }} />
              {statistics && (
                <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 1 }}>
                  <Chip
                    icon={<TrendingUpIcon />}
                    label={`Max: $${statistics.overall.max.toFixed(2)}`}
                    size="small"
                    variant="outlined"
                    sx={{ color: 'white', borderColor: 'white' }}
                  />
                  <Chip
                    icon={<TrendingDownIcon />}
                    label={`Min: $${statistics.overall.min.toFixed(2)}`}
                    size="small"
                    variant="outlined"
                    sx={{ color: 'white', borderColor: 'white' }}
                  />
                  <Chip
                    icon={<WarningIcon />}
                    label={`Vol: ${statistics.returns.annualized_vol.toFixed(1)}%`}
                    size="small"
                    variant="outlined"
                    sx={{ color: 'white', borderColor: 'white' }}
                  />
                </Box>
              )}
            </Toolbar>
          </AppBar>
          
          <Box
            component="nav"
            sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
          >
            <Drawer
              variant="temporary"
              open={mobileOpen}
              onClose={handleDrawerToggle}
              ModalProps={{
                keepMounted: true,
              }}
              sx={{
                display: { xs: 'block', sm: 'none' },
                '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
              }}
            >
              {drawer}
            </Drawer>
            <Drawer
              variant="permanent"
              sx={{
                display: { xs: 'none', sm: 'block' },
                '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
              }}
              open
            >
              {drawer}
            </Drawer>
          </Box>
          
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              p: 3,
              width: { sm: `calc(100% - ${drawerWidth}px)` },
              mt: '64px'
            }}
          >
            <Container maxWidth="xl">
              <Routes>
                <Route path="/" element={<DashboardOverview />} />
                <Route path="/price-chart" element={<PriceChart />} />
                <Route path="/change-points" element={<ChangePointAnalysis />} />
                <Route path="/event-impact" element={<EventImpactAnalyzer />} />
                <Route path="/statistics" element={<StatisticsPage statistics={statistics} />} />
                <Route path="*" element={<Navigate to="/" />} />
              </Routes>
              
              {/* Footer */}
              <Paper elevation={0} sx={{ mt: 4, p: 2, backgroundColor: 'transparent' }}>
                <Divider sx={{ mb: 2 }} />
                <Grid container justifyContent="space-between" alignItems="center">
                  <Grid item>
                    <Typography variant="caption" color="textSecondary">
                      Brent Oil Dashboard v1.0 • Birhan Energies Analytics
                    </Typography>
                  </Grid>
                  <Grid item>
                    <Typography variant="caption" color="textSecondary">
                      Data: 1987-2022 • Last updated: {new Date().toLocaleDateString()}
                    </Typography>
                  </Grid>
                </Grid>
              </Paper>
            </Container>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

function StatisticsPage({ statistics }) {
  if (!statistics) {
    return (
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography>Loading statistics...</Typography>
      </Paper>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Statistics & Metrics
      </Typography>
      
      <Grid container spacing={3}>
        {/* Overall Statistics */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Overall Statistics
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Mean Price
                    </Typography>
                    <Typography variant="h4">
                      ${statistics.overall.mean.toFixed(2)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Volatility (Annual)
                    </Typography>
                    <Typography variant="h4">
                      {statistics.returns.annualized_vol.toFixed(1)}%
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Price Range
                    </Typography>
                    <Typography variant="h6">
                      ${statistics.overall.min.toFixed(2)} - ${statistics.overall.max.toFixed(2)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Data Points
                    </Typography>
                    <Typography variant="h4">
                      {statistics.overall.count.toLocaleString()}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
        
        {/* More statistics cards can be added here */}
      </Grid>
    </Box>
  );
}

export default App;