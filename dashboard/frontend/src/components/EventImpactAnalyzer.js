import React, { useState, useEffect } from 'react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    ReferenceLine,
    Area,
    BarChart,
    Bar
} from 'recharts';
import {
    Box,
    Paper,
    Typography,
    Grid,
    Card,
    CardContent,
    TextField,
    Autocomplete,
    Button,
    Chip,
    Divider,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    IconButton,
    CircularProgress
} from '@mui/material';
import {
    Search,
    Timeline,
    ShowChart,
    TrendingUp,
    TrendingDown,
    Warning,
    Info
} from '@mui/icons-material';
import { format, subDays, addDays } from 'date-fns';
import api from '../services/api';

const EventImpactAnalyzer = () => {
    const [events, setEvents] = useState([]);
    const [selectedEvent, setSelectedEvent] = useState(null);
    const [impactData, setImpactData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [priceData, setPriceData] = useState([]);

    useEffect(() => {
        loadEvents();
    }, []);

    useEffect(() => {
        if (selectedEvent) {
            analyzeEventImpact(selectedEvent.Event);
        }
    }, [selectedEvent]);

    const loadEvents = async () => {
        try {
            const response = await api.getEvents();
            if (response.success) {
                setEvents(response.events);
            }
        } catch (error) {
            console.error('Error loading events:', error);
        }
    };

    const analyzeEventImpact = async (eventName) => {
        setLoading(true);
        try {
            // Get impact analysis
            const impactResponse = await api.getEventImpact(eventName);
            if (impactResponse.success) {
                setImpactData(impactResponse.data);
                
                // Get price data for visualization
                const eventDate = new Date(impactResponse.data.event.date);
                const startDate = subDays(eventDate, 60);
                const endDate = addDays(eventDate, 60);
                
                const priceResponse = await api.getPriceData(
                    format(startDate, 'yyyy-MM-dd'),
                    format(endDate, 'yyyy-MM-dd')
                );
                
                if (priceResponse.success) {
                    const chartData = priceResponse.data.dates.map((date, index) => ({
                        date,
                        price: priceResponse.data.prices[index],
                        isBefore: new Date(date) < eventDate
                    }));
                    setPriceData(chartData);
                }
            }
        } catch (error) {
            console.error('Error analyzing event impact:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleEventSelect = (event, value) => {
        setSelectedEvent(value);
    };

    const handleSearch = async () => {
        if (!searchQuery.trim()) return;
        
        try {
            const response = await api.searchEvents(searchQuery);
            if (response.success && response.events.length > 0) {
                setSelectedEvent(response.events[0]);
                analyzeEventImpact(response.events[0].Event);
            }
        } catch (error) {
            console.error('Error searching events:', error);
        }
    };

    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            const date = new Date(label);
            const eventDate = selectedEvent ? new Date(selectedEvent.Date) : null;
            const isEventDay = eventDate && format(date, 'yyyy-MM-dd') === format(eventDate, 'yyyy-MM-dd');
            
            return (
                <Paper elevation={3} sx={{ p: 2, backgroundColor: 'rgba(255, 255, 255, 0.95)' }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                        {format(date, 'MMM dd, yyyy')}
                        {isEventDay && (
                            <Chip 
                                label="Event Day" 
                                size="small" 
                                color="error" 
                                sx={{ ml: 1 }}
                            />
                        )}
                    </Typography>
                    <Typography variant="body2" color="primary">
                        Price: ${payload[0].value.toFixed(2)}
                    </Typography>
                    {impactData && (
                        <Typography variant="body2" color="textSecondary">
                            vs. Avg Before: ${impactData.impact_metrics.price_before.toFixed(2)}
                        </Typography>
                    )}
                </Paper>
            );
        }
        return null;
    };

    const renderImpactMetrics = () => {
        if (!impactData) return null;

        const metrics = impactData.impact_metrics;
        const isIncrease = metrics.absolute_change > 0;
        const percentChange = metrics.percent_change;
        const isSignificant = metrics.significant;

        return (
            <Grid container spacing={2} sx={{ mt: 2 }}>
                <Grid item xs={12} md={3}>
                    <Card elevation={2}>
                        <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                                Price Change
                            </Typography>
                            <Typography variant="h4" sx={{ color: isIncrease ? '#4caf50' : '#f44336' }}>
                                {isIncrease ? '+' : ''}{percentChange.toFixed(1)}%
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                                ${Math.abs(metrics.absolute_change).toFixed(2)} {isIncrease ? 'increase' : 'decrease'}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card elevation={2}>
                        <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                                Statistical Significance
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                                {isSignificant ? (
                                    <>
                                        <Chip 
                                            label="Significant" 
                                            color="success" 
                                            size="small"
                                            icon={<Info />}
                                        />
                                        <Typography variant="body2" sx={{ ml: 1 }}>
                                            p = {metrics.p_value.toFixed(4)}
                                        </Typography>
                                    </>
                                ) : (
                                    <>
                                        <Chip 
                                            label="Not Significant" 
                                            color="warning" 
                                            size="small"
                                            icon={<Warning />}
                                        />
                                        <Typography variant="body2" sx={{ ml: 1 }}>
                                            p = {metrics.p_value.toFixed(4)}
                                        </Typography>
                                    </>
                                )}
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card elevation={2}>
                        <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                                Time Windows
                            </Typography>
                            <Typography variant="body1">
                                30 days before/after
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                                Event date: {format(new Date(impactData.event.date), 'MMM dd, yyyy')}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card elevation={2}>
                        <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                                Average Prices
                            </Typography>
                            <Typography variant="body2">
                                Before: ${metrics.price_before.toFixed(2)}
                            </Typography>
                            <Typography variant="body2">
                                After: ${metrics.price_after.toFixed(2)}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        );
    };

    return (
        <Box sx={{ width: '100%' }}>
            <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
                <Timeline sx={{ verticalAlign: 'middle', mr: 1 }} />
                Event Impact Analyzer
            </Typography>

            {/* Search and Selection */}
            <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
                <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={6}>
                        <Autocomplete
                            options={events}
                            getOptionLabel={(option) => `${option.Event} (${format(new Date(option.Date), 'MMM yyyy')})`}
                            value={selectedEvent}
                            onChange={handleEventSelect}
                            renderInput={(params) => (
                                <TextField
                                    {...params}
                                    label="Search or Select Event"
                                    variant="outlined"
                                    fullWidth
                                />
                            )}
                            renderOption={(props, option) => (
                                <Box component="li" {...props}>
                                    <Box>
                                        <Typography variant="body1">
                                            {option.Event}
                                        </Typography>
                                        <Typography variant="caption" color="textSecondary">
                                            {format(new Date(option.Date), 'MMM dd, yyyy')} • {option.Type}
                                        </Typography>
                                    </Box>
                                </Box>
                            )}
                        />
                    </Grid>
                    <Grid item xs={12} md={4}>
                        <TextField
                            fullWidth
                            label="Search Events"
                            variant="outlined"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                        />
                    </Grid>
                    <Grid item xs={12} md={2}>
                        <Button
                            variant="contained"
                            startIcon={<Search />}
                            onClick={handleSearch}
                            fullWidth
                            sx={{ height: '56px' }}
                        >
                            Search
                        </Button>
                    </Grid>
                </Grid>
            </Paper>

            {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
                    <CircularProgress />
                    <Typography sx={{ ml: 2 }}>Analyzing event impact...</Typography>
                </Box>
            ) : selectedEvent && impactData ? (
                <>
                    {/* Event Header */}
                    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
                        <Grid container spacing={2}>
                            <Grid item xs={12}>
                                <Typography variant="h5" gutterBottom>
                                    {selectedEvent.Event}
                                </Typography>
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <Typography variant="body1" paragraph>
                                    <strong>Description:</strong> {selectedEvent.Description}
                                </Typography>
                                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                    <Chip label={selectedEvent.Type} color="primary" />
                                    <Chip 
                                        label={`Impact: ${selectedEvent.Impact_Expected}`} 
                                        color={
                                            selectedEvent.Impact_Expected === 'Very High' ? 'error' :
                                            selectedEvent.Impact_Expected === 'High' ? 'warning' :
                                            'default'
                                        }
                                    />
                                    <Chip 
                                        label={format(new Date(selectedEvent.Date), 'MMMM dd, yyyy')}
                                        variant="outlined"
                                    />
                                </Box>
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <TableContainer component={Paper} variant="outlined">
                                    <Table size="small">
                                        <TableBody>
                                            <TableRow>
                                                <TableCell><strong>Event Date</strong></TableCell>
                                                <TableCell>{format(new Date(selectedEvent.Date), 'PPPP')}</TableCell>
                                            </TableRow>
                                            <TableRow>
                                                <TableCell><strong>Event Type</strong></TableCell>
                                                <TableCell>{selectedEvent.Type}</TableCell>
                                            </TableRow>
                                            <TableRow>
                                                <TableCell><strong>Expected Impact</strong></TableCell>
                                                <TableCell>
                                                    <Chip 
                                                        label={selectedEvent.Impact_Expected}
                                                        size="small"
                                                        color={
                                                            selectedEvent.Impact_Expected === 'Very High' ? 'error' :
                                                            selectedEvent.Impact_Expected === 'High' ? 'warning' :
                                                            'success'
                                                        }
                                                    />
                                                </TableCell>
                                            </TableRow>
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            </Grid>
                        </Grid>
                    </Paper>

                    {/* Impact Metrics */}
                    {renderImpactMetrics()}

                    {/* Price Chart */}
                    <Paper elevation={3} sx={{ p: 3, mt: 3, mb: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            <ShowChart sx={{ verticalAlign: 'middle', mr: 1 }} />
                            Price Movement Around Event
                        </Typography>
                        <Box sx={{ height: 400 }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart
                                    data={priceData}
                                    margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
                                >
                                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                    <XAxis
                                        dataKey="date"
                                        tickFormatter={(date) => format(new Date(date), 'MMM dd')}
                                        interval="preserveStartEnd"
                                    />
                                    <YAxis
                                        label={{ 
                                            value: 'Price (USD)', 
                                            angle: -90, 
                                            position: 'insideLeft',
                                            offset: 10
                                        }}
                                        tickFormatter={(value) => `$${value.toFixed(2)}`}
                                    />
                                    <Tooltip content={<CustomTooltip />} />
                                    <Legend />
                                    
                                    <Line
                                        type="monotone"
                                        dataKey="price"
                                        stroke="#1976d2"
                                        strokeWidth={2}
                                        dot={false}
                                        name="Brent Oil Price"
                                        activeDot={{ r: 6 }}
                                    />
                                    
                                    {impactData && (
                                        <ReferenceLine
                                            x={impactData.event.date}
                                            stroke="#ff4444"
                                            strokeWidth={2}
                                            label={{
                                                value: 'Event',
                                                position: 'top',
                                                fill: '#ff4444',
                                                fontSize: 12
                                            }}
                                        />
                                    )}
                                    
                                    {impactData && (
                                        <ReferenceLine
                                            y={impactData.impact_metrics.price_before}
                                            stroke="#4caf50"
                                            strokeWidth={1}
                                            strokeDasharray="3 3"
                                            label={{
                                                value: `Avg Before: $${impactData.impact_metrics.price_before.toFixed(2)}`,
                                                position: 'left',
                                                fill: '#4caf50'
                                            }}
                                        />
                                    )}
                                    
                                    {impactData && (
                                        <ReferenceLine
                                            y={impactData.impact_metrics.price_after}
                                            stroke="#ff9800"
                                            strokeWidth={1}
                                            strokeDasharray="3 3"
                                            label={{
                                                value: `Avg After: $${impactData.impact_metrics.price_after.toFixed(2)}`,
                                                position: 'right',
                                                fill: '#ff9800'
                                            }}
                                        />
                                    )}
                                    
                                    <Area
                                        type="monotone"
                                        dataKey="price"
                                        fill="#1976d2"
                                        fillOpacity={0.1}
                                        stroke="none"
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </Box>
                    </Paper>

                    {/* Statistical Analysis */}
                    <Paper elevation={3} sx={{ p: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            Statistical Analysis Details
                        </Typography>
                        <Grid container spacing={2}>
                            <Grid item xs={12} md={6}>
                                <Card variant="outlined">
                                    <CardContent>
                                        <Typography variant="subtitle1" gutterBottom>
                                            T-Test Results
                                        </Typography>
                                        <Table size="small">
                                            <TableBody>
                                                <TableRow>
                                                    <TableCell>T-Statistic</TableCell>
                                                    <TableCell align="right">
                                                        {impactData.impact_metrics.t_statistic.toFixed(4)}
                                                    </TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell>P-Value</TableCell>
                                                    <TableCell align="right">
                                                        {impactData.impact_metrics.p_value.toFixed(4)}
                                                    </TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell>Significance</TableCell>
                                                    <TableCell align="right">
                                                        <Chip
                                                            label={impactData.impact_metrics.significant ? 'Significant (p < 0.05)' : 'Not Significant'}
                                                            color={impactData.impact_metrics.significant ? 'success' : 'warning'}
                                                            size="small"
                                                        />
                                                    </TableCell>
                                                </TableRow>
                                            </TableBody>
                                        </Table>
                                    </CardContent>
                                </Card>
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <Card variant="outlined">
                                    <CardContent>
                                        <Typography variant="subtitle1" gutterBottom>
                                            Price Distribution
                                        </Typography>
                                        <Box sx={{ height: 200 }}>
                                            <ResponsiveContainer width="100%" height="100%">
                                                <BarChart
                                                    data={[
                                                        { period: 'Before Event', price: impactData.impact_metrics.price_before },
                                                        { period: 'After Event', price: impactData.impact_metrics.price_after }
                                                    ]}
                                                >
                                                    <CartesianGrid strokeDasharray="3 3" />
                                                    <XAxis dataKey="period" />
                                                    <YAxis 
                                                        tickFormatter={(value) => `$${value.toFixed(2)}`}
                                                        domain={[0, 'dataMax * 1.1']}
                                                    />
                                                    <Tooltip formatter={(value) => [`$${value.toFixed(2)}`, 'Average Price']} />
                                                    <Bar 
                                                        dataKey="price" 
                                                        fill="#1976d2"
                                                        radius={[4, 4, 0, 0]}
                                                    />
                                                </BarChart>
                                            </ResponsiveContainer>
                                        </Box>
                                    </CardContent>
                                </Card>
                            </Grid>
                        </Grid>
                        
                        <Divider sx={{ my: 3 }} />
                        
                        <Typography variant="body2" color="textSecondary" paragraph>
                            <strong>Interpretation:</strong> {
                                impactData.impact_metrics.significant ? 
                                `The ${impactData.event.name} shows a statistically significant impact on Brent oil prices. ` +
                                `Prices ${impactData.impact_metrics.absolute_change > 0 ? 'increased' : 'decreased'} by ` +
                                `${Math.abs(impactData.impact_metrics.percent_change).toFixed(1)}% following the event.` :
                                `The ${impactData.event.name} does not show a statistically significant impact on Brent oil prices ` +
                                `within the 30-day analysis window. This could indicate delayed effects, smaller impact than expected, ` +
                                `or confounding factors.`
                            }
                        </Typography>
                        
                        <Typography variant="body2" color="textSecondary">
                            <strong>Note:</strong> Statistical significance (p &lt; 0.05) indicates that the observed price difference is unlikely 
                            to have occurred by chance alone. However, correlation does not imply causation, and other factors may 
                            have contributed to the observed price movement.
                        </Typography>
                    </Paper>
                </>
            ) : (
                <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
                    <Typography variant="h6" color="textSecondary" gutterBottom>
                        Select an event to analyze its impact
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                        Choose from the dropdown or search for specific events to see their impact on Brent oil prices.
                    </Typography>
                </Paper>
            )}
        </Box>
    );
};

export default EventImpactAnalyzer;