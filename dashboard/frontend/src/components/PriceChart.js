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
    Scatter,
    Brush
} from 'recharts';
import { format } from 'date-fns';
import {
    Box,
    Paper,
    Typography,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Chip,
    Grid,
    IconButton,
    Tooltip as MuiTooltip
} from '@mui/material';
import { Event as EventIcon, TrendingUp, TrendingDown } from '@mui/icons-material';
import api from '../services/api';

const PriceChart = () => {
    const [priceData, setPriceData] = useState([]);
    const [events, setEvents] = useState([]);
    const [selectedEvent, setSelectedEvent] = useState(null);
    const [timeRange, setTimeRange] = useState('5y'); // 1y, 5y, 10y, all
    const [eventTypeFilter, setEventTypeFilter] = useState('all');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, [timeRange, eventTypeFilter]);

    const loadData = async () => {
        setLoading(true);
        try {
            // Calculate date range based on selection
            const endDate = new Date();
            let startDate = new Date();
            
            switch (timeRange) {
                case '1y':
                    startDate.setFullYear(startDate.getFullYear() - 1);
                    break;
                case '5y':
                    startDate.setFullYear(startDate.getFullYear() - 5);
                    break;
                case '10y':
                    startDate.setFullYear(startDate.getFullYear() - 10);
                    break;
                case 'all':
                default:
                    startDate = new Date('1987-01-01');
            }

            // Fetch price data
            const priceResponse = await api.getPriceData(
                format(startDate, 'yyyy-MM-dd'),
                format(endDate, 'yyyy-MM-dd')
            );

            if (priceResponse.success) {
                // Combine dates and prices into chart format
                const chartData = priceResponse.data.dates.map((date, index) => ({
                    date,
                    price: priceResponse.data.prices[index],
                    return: priceResponse.data.log_returns[index] || 0
                }));
                setPriceData(chartData);
            }

            // Fetch events
            const eventsResponse = await api.getEvents(
                eventTypeFilter,
                format(startDate, 'yyyy-MM-dd'),
                format(endDate, 'yyyy-MM-dd')
            );

            if (eventsResponse.success) {
                setEvents(eventsResponse.events);
            }
        } catch (error) {
            console.error('Error loading data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleEventClick = (event) => {
        setSelectedEvent(event);
        // You could add zoom or highlight functionality here
    };

    const formatCurrency = (value) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2
        }).format(value);
    };

    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            const date = new Date(label);
            const formattedDate = format(date, 'MMM dd, yyyy');
            
            return (
                <Paper elevation={3} sx={{ p: 2, backgroundColor: 'rgba(255, 255, 255, 0.95)' }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                        {formattedDate}
                    </Typography>
                    <Typography variant="body2" color="primary">
                        Price: {formatCurrency(payload[0].value)}
                    </Typography>
                    {payload[1] && (
                        <Typography variant="body2" color="secondary">
                            Daily Return: {(payload[1].value * 100).toFixed(2)}%
                        </Typography>
                    )}
                </Paper>
            );
        }
        return null;
    };

    const EventMarkers = () => {
        return events.map((event, index) => {
            const dataPoint = priceData.find(d => d.date === event.Date);
            if (!dataPoint) return null;

            const getEventColor = (type) => {
                const colors = {
                    'Geopolitical Conflict': '#ff4444',
                    'Economic Crisis': '#ff9900',
                    'Policy Decision': '#00aa00',
                    'Natural Disaster': '#996633',
                    'Environmental Disaster': '#009966',
                    'Military Action': '#cc0000',
                    'Global Crisis': '#660066'
                };
                return colors[type] || '#888888';
            };

            return (
                <Scatter
                    key={index}
                    data={[{ ...dataPoint, event }]}
                    dataKey="price"
                    fill={getEventColor(event.Type)}
                    shape={(props) => (
                        <MuiTooltip title={`${event.Event} (${event.Type})`} arrow>
                            <EventIcon
                                style={{
                                    cursor: 'pointer',
                                    fontSize: '20px',
                                    color: getEventColor(event.Type),
                                    transform: 'translate(-10px, -10px)'
                                }}
                                onClick={() => handleEventClick(event)}
                            />
                        </MuiTooltip>
                    )}
                />
            );
        }).filter(Boolean);
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
                <Typography>Loading chart data...</Typography>
            </Box>
        );
    }

    return (
        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h5" component="h2">
                    Brent Oil Price History with Events
                </Typography>
                
                <Box sx={{ display: 'flex', gap: 2 }}>
                    <FormControl size="small" sx={{ minWidth: 120 }}>
                        <InputLabel>Time Range</InputLabel>
                        <Select
                            value={timeRange}
                            label="Time Range"
                            onChange={(e) => setTimeRange(e.target.value)}
                        >
                            <MenuItem value="1y">1 Year</MenuItem>
                            <MenuItem value="5y">5 Years</MenuItem>
                            <MenuItem value="10y">10 Years</MenuItem>
                            <MenuItem value="all">All Data</MenuItem>
                        </Select>
                    </FormControl>

                    <FormControl size="small" sx={{ minWidth: 150 }}>
                        <InputLabel>Event Type</InputLabel>
                        <Select
                            value={eventTypeFilter}
                            label="Event Type"
                            onChange={(e) => setEventTypeFilter(e.target.value)}
                        >
                            <MenuItem value="all">All Events</MenuItem>
                            <MenuItem value="Geopolitical Conflict">Geopolitical</MenuItem>
                            <MenuItem value="Economic Crisis">Economic Crisis</MenuItem>
                            <MenuItem value="Policy Decision">Policy Decision</MenuItem>
                            <MenuItem value="Natural Disaster">Natural Disaster</MenuItem>
                        </Select>
                    </FormControl>
                </Box>
            </Box>

            <Box sx={{ height: 400 }}>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                        data={priceData}
                        margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
                    >
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                        <XAxis
                            dataKey="date"
                            tickFormatter={(date) => format(new Date(date), 'MMM yyyy')}
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
                        
                        <Line
                            type="monotone"
                            dataKey="return"
                            stroke="#ff9800"
                            strokeWidth={1}
                            dot={false}
                            name="Daily Return"
                            yAxisId={1}
                            strokeDasharray="3 3"
                            hide={priceData.length > 365} // Hide returns for long time ranges
                        />
                        
                        <EventMarkers />
                        
                        {selectedEvent && (
                            <ReferenceLine
                                x={selectedEvent.Date}
                                stroke="#ff4444"
                                strokeWidth={2}
                                strokeDasharray="3 3"
                                label={{
                                    value: selectedEvent.Event,
                                    position: 'top',
                                    fill: '#ff4444',
                                    fontSize: 12
                                }}
                            />
                        )}
                        
                        <Brush
                            dataKey="date"
                            height={30}
                            stroke="#1976d2"
                            tickFormatter={(date) => format(new Date(date), 'yyyy')}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </Box>

            {selectedEvent && (
                <Paper elevation={2} sx={{ p: 2, mt: 2, backgroundColor: '#fff8e1' }}>
                    <Grid container spacing={2}>
                        <Grid item xs={12}>
                            <Typography variant="h6" color="primary">
                                Selected Event: {selectedEvent.Event}
                            </Typography>
                        </Grid>
                        <Grid item xs={6}>
                            <Typography variant="body2">
                                <strong>Date:</strong> {format(new Date(selectedEvent.Date), 'MMMM dd, yyyy')}
                            </Typography>
                            <Typography variant="body2">
                                <strong>Type:</strong> {selectedEvent.Type}
                            </Typography>
                        </Grid>
                        <Grid item xs={6}>
                            <Typography variant="body2">
                                <strong>Impact:</strong> {selectedEvent.Impact_Expected}
                            </Typography>
                            <Typography variant="body2">
                                <strong>Description:</strong> {selectedEvent.Description}
                            </Typography>
                        </Grid>
                    </Grid>
                </Paper>
            )}

            <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                <Chip icon={<EventIcon />} label={`${events.length} Events`} color="primary" size="small" />
                <Chip 
                    icon={<TrendingUp />} 
                    label={`Max: $${Math.max(...priceData.map(d => d.price)).toFixed(2)}`} 
                    color="success" 
                    size="small" 
                />
                <Chip 
                    icon={<TrendingDown />} 
                    label={`Min: $${Math.min(...priceData.map(d => d.price)).toFixed(2)}`} 
                    color="error" 
                    size="small" 
                />
            </Box>
        </Paper>
    );
};

export default PriceChart;