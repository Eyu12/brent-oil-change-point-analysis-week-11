import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  ShowChart,
  Event,
  Timeline,
  Warning,
  Info,
  Refresh
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';
import api from '../services/api';

const DashboardOverview = () => {
  const [stats, setStats] = useState(null);
  const [recentEvents, setRecentEvents] = useState([]);
  const [priceTrend, setPriceTrend] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Load statistics
      const statsResponse = await api.getStatistics();
      if (statsResponse.success) {
        setStats(statsResponse.statistics);
      }

      // Load recent events
      const eventsResponse = await api.getEvents();
      if (eventsResponse.success) {
        // Get 5 most recent events
        const sortedEvents = eventsResponse.events
          .sort((a, b) => new Date(b.Date) - new Date(a.Date))
          .slice(0, 5);
        setRecentEvents(sortedEvents);
      }

      // Load recent price trend (last 30 days)
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - 30);
      
      const priceResponse = await api.getPriceData(
        format(startDate, 'yyyy-MM-dd'),
        format(endDate, 'yyyy-MM-dd')
      );
      
      if (priceResponse.success) {
        setPriceTrend(priceResponse.data.dates.map((date, index) => ({
          date: format(new Date(date), 'MMM dd'),
          price: priceResponse.data.prices[index]
        })));
      }

      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    loadDashboardData();
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <Box sx={{ textAlign: 'center' }}>
          <LinearProgress sx={{ width: 200, mx: 'auto', mb: 2 }} />
          <Typography>Loading dashboard data...</Typography>
        </Box>
      </Box>
    );
  }

  if (!stats) {
    return (
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography color="error">Unable to load dashboard data</Typography>
      </Paper>
    );
  }

  const overall = stats.overall;
  const returns = stats.returns;

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Dashboard Overview
        </Typography>
        <Tooltip title="Refresh Data">
          <IconButton onClick={handleRefresh}>
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <ShowChart color="primary" sx={{ mr: 1 }} />
                <Typography color="textSecondary">
                  Current Price
                </Typography>
              </Box>
              <Typography variant="h4">
                ${priceTrend.length > 0 ? priceTrend[priceTrend.length - 1].price.toFixed(2) : '--'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Last 30 days trend
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUp color="success" sx={{ mr: 1 }} />
                <Typography color="textSecondary">
                  Average Price
                </Typography>
              </Box>
              <Typography variant="h4">
                ${overall.mean.toFixed(2)}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Historical average
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Warning color="warning" sx={{ mr: 1 }} />
                <Typography color="textSecondary">
                  Annual Volatility
                </Typography>
              </Box>
              <Typography variant="h4">
                {returns.annualized_vol.toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Risk measure
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Event color="secondary" sx={{ mr: 1 }} />
                <Typography color="textSecondary">
                  Events Tracked
                </Typography>
              </Box>
              <Typography variant="h4">
                {recentEvents.length}+
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Major market events
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Trend and Events */}
      <Grid container spacing={3}>
        {/* Recent Price Trend */}
        <Grid item xs={12} md={8}>
          <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <Timeline sx={{ mr: 1 }} />
              Recent Price Trend (30 Days)
            </Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={priceTrend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="date" />
                  <YAxis 
                    tickFormatter={(value) => `$${value.toFixed(2)}`}
                    domain={['dataMin - 5', 'dataMax + 5']}
                  />
                  <RechartsTooltip 
                    formatter={(value) => [`$${value.toFixed(2)}`, 'Price']}
                    labelFormatter={(label) => `Date: ${label}`}
                  />
                  <Line
                    type="monotone"
                    dataKey="price"
                    stroke="#1976d2"
                    strokeWidth={2}
                    dot={{ r: 2 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        {/* Recent Events */}
        <Grid item xs={12} md={4}>
          <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <Event sx={{ mr: 1 }} />
              Recent Major Events
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Event</TableCell>
                    <TableCell align="right">Date</TableCell>
                    <TableCell align="right">Impact</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recentEvents.map((event, index) => (
                    <TableRow key={index} hover>
                      <TableCell>
                        <Typography variant="body2" noWrap sx={{ maxWidth: 150 }}>
                          {event.Event}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="caption">
                          {format(new Date(event.Date), 'MMM dd')}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Chip
                          label={event.Impact_Expected}
                          size="small"
                          color={
                            event.Impact_Expected === 'Very High' ? 'error' :
                            event.Impact_Expected === 'High' ? 'warning' :
                            'default'
                          }
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        {/* Quick Stats */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Statistics
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} md={2}>
                <Card variant="outlined">
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography color="textSecondary" variant="body2">
                      Min Price
                    </Typography>
                    <Typography variant="h6" color="error">
                      ${overall.min.toFixed(2)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} md={2}>
                <Card variant="outlined">
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography color="textSecondary" variant="body2">
                      Max Price
                    </Typography>
                    <Typography variant="h6" color="success">
                      ${overall.max.toFixed(2)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} md={2}>
                <Card variant="outlined">
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography color="textSecondary" variant="body2">
                      Std Dev
                    </Typography>
                    <Typography variant="h6">
                      ${overall.std.toFixed(2)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} md={2}>
                <Card variant="outlined">
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography color="textSecondary" variant="body2">
                      Data Points
                    </Typography>
                    <Typography variant="h6">
                      {overall.count.toLocaleString()}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} md={2}>
                <Card variant="outlined">
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography color="textSecondary" variant="body2">
                      Daily Return
                    </Typography>
                    <Typography variant="h6">
                      {(returns.mean_return * 100).toFixed(3)}%
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} md={2}>
                <Card variant="outlined">
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography color="textSecondary" variant="body2">
                      Last Updated
                    </Typography>
                    <Typography variant="body2">
                      {format(lastUpdated, 'HH:mm')}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>

      {/* Dashboard Sections Overview */}
      <Paper elevation={3} sx={{ p: 3, mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          Dashboard Features
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <ShowChartIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="subtitle1">Interactive Price Chart</Typography>
                </Box>
                <Typography variant="body2" color="textSecondary">
                  Visualize Brent oil prices with event annotations, filtering, and zoom capabilities.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Timeline color="secondary" sx={{ mr: 1 }} />
                  <Typography variant="subtitle1">Change Point Analysis</Typography>
                </Box>
                <Typography variant="body2" color="textSecondary">
                  Bayesian analysis to detect structural breaks and quantify their impact.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <EventIcon color="success" sx={{ mr: 1 }} />
                  <Typography variant="subtitle1">Event Impact Analyzer</Typography>
                </Box>
                <Typography variant="body2" color="textSecondary">
                  Analyze specific events and their statistical impact on oil prices.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>

      <Divider sx={{ my: 3 }} />
      
      <Typography variant="body2" color="textSecondary" align="center">
        Brent Oil Dashboard • Birhan Energies Analytics • Data from 1987-2022
      </Typography>
    </Box>
  );
};

export default DashboardOverview;