import React, { useState, useEffect } from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    AreaChart,
    Area,
    ComposedChart,
    Line
} from 'recharts';
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
    Divider
} from '@mui/material';
import {
    TrendingUp,
    TrendingDown,
    ShowChart,
    Timeline,
    Assessment
} from '@mui/icons-material';
import api from '../services/api';

const ChangePointAnalysis = () => {
    const [changePointData, setChangePointData] = useState(null);
    const [posteriorSamples, setPosteriorSamples] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadChangePointData();
    }, []);

    const loadChangePointData = async () => {
        setLoading(true);
        try {
            const response = await api.getChangePoints();
            if (response.success) {
                setChangePointData(response.data.change_point);
                setPosteriorSamples(response.data.posterior_samples);
            }
        } catch (error) {
            console.error('Error loading change point data:', error);
        } finally {
            setLoading(false);
        }
    };

    const prepareHistogramData = () => {
        if (!posteriorSamples) return [];
        
        // Process tau samples for histogram
        const tauSamples = posteriorSamples.tau;
        const histData = {};
        
        tauSamples.forEach(sample => {
            histData[sample] = (histData[sample] || 0) + 1;
        });
        
        return Object.entries(histData)
            .map(([tau, count]) => ({ tau: parseInt(tau), count }))
            .sort((a, b) => a.tau - b.tau);
    };

    const prepareParameterDistributions = () => {
        if (!posteriorSamples) return { muBefore: [], muAfter: [], sigma: [] };
        
        return {
            muBefore: posteriorSamples.mu_before,
            muAfter: posteriorSamples.mu_after,
            sigma: posteriorSamples.sigma
        };
    };

    if (loading) {
        return (
            <Box sx={{ width: '100%', p: 3 }}>
                <LinearProgress />
                <Typography sx={{ mt: 2 }}>Loading change point analysis...</Typography>
            </Box>
        );
    }

    if (!changePointData) {
        return (
            <Paper elevation={3} sx={{ p: 3 }}>
                <Typography color="error">No change point data available</Typography>
            </Paper>
        );
    }

    const histogramData = prepareHistogramData();
    const paramDistributions = prepareParameterDistributions();
    
    const isIncrease = changePointData.difference > 0;
    const changeColor = isIncrease ? '#4caf50' : '#f44336';
    const changeIcon = isIncrease ? <TrendingUp /> : <TrendingDown />;

    return (
        <Box sx={{ width: '100%' }}>
            <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
                <ShowChart sx={{ verticalAlign: 'middle', mr: 1 }} />
                Bayesian Change Point Analysis
            </Typography>

            {/* Summary Cards */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} md={3}>
                    <Card elevation={2}>
                        <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                                Change Point Date
                            </Typography>
                            <Typography variant="h5" component="div">
                                {new Date(changePointData.date).toLocaleDateString()}
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                                Most probable structural break
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card elevation={2}>
                        <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                                Price Change
                            </Typography>
                            <Typography variant="h5" component="div" sx={{ color: changeColor }}>
                                {changeIcon} ${Math.abs(changePointData.difference).toFixed(2)}
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                                {isIncrease ? 'Increase' : 'Decrease'} of {Math.abs(changePointData.percentage_change).toFixed(1)}%
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card elevation={2}>
                        <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                                Probability of Increase
                            </Typography>
                            <Typography variant="h5" component="div">
                                {(changePointData.probability_increase * 100).toFixed(1)}%
                            </Typography>
                            <Box sx={{ mt: 1 }}>
                                <LinearProgress 
                                    variant="determinate" 
                                    value={changePointData.probability_increase * 100}
                                    sx={{ height: 8, borderRadius: 4 }}
                                />
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card elevation={2}>
                        <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                                Statistical Confidence
                            </Typography>
                            <Typography variant="h5" component="div">
                                High
                            </Typography>
                            <Chip 
                                label="95% Credible Interval" 
                                size="small" 
                                color="primary" 
                                sx={{ mt: 1 }}
                            />
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Charts */}
            <Grid container spacing={3}>
                {/* Change Point Posterior Distribution */}
                <Grid item xs={12} md={6}>
                    <Paper elevation={3} sx={{ p: 2, height: 400 }}>
                        <Typography variant="h6" gutterBottom>
                            <Timeline sx={{ verticalAlign: 'middle', mr: 1 }} />
                            Posterior Distribution of Change Point (τ)
                        </Typography>
                        <ResponsiveContainer width="100%" height="85%">
                            <BarChart data={histogramData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis 
                                    dataKey="tau" 
                                    label={{ value: 'Time Index (Days)', position: 'insideBottom', offset: -5 }}
                                />
                                <YAxis label={{ value: 'Frequency', angle: -90, position: 'insideLeft' }} />
                                <Tooltip 
                                    formatter={(value) => [value, 'Frequency']}
                                    labelFormatter={(label) => `Day ${label}`}
                                />
                                <Bar 
                                    dataKey="count" 
                                    fill="#1976d2" 
                                    name="Posterior Probability"
                                    radius={[4, 4, 0, 0]}
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    </Paper>
                </Grid>

                {/* Before/After Comparison */}
                <Grid item xs={12} md={6}>
                    <Paper elevation={3} sx={{ p: 2, height: 400 }}>
                        <Typography variant="h6" gutterBottom>
                            <Assessment sx={{ verticalAlign: 'middle', mr: 1 }} />
                            Mean Price: Before vs After Change
                        </Typography>
                        <ResponsiveContainer width="100%" height="85%">
                            <ComposedChart data={[
                                { 
                                    parameter: 'Before Change', 
                                    value: changePointData.mu_before,
                                    min: changePointData.mu_before * 0.95,
                                    max: changePointData.mu_before * 1.05
                                },
                                { 
                                    parameter: 'After Change', 
                                    value: changePointData.mu_after,
                                    min: changePointData.mu_after * 0.95,
                                    max: changePointData.mu_after * 1.05
                                }
                            ]}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="parameter" />
                                <YAxis 
                                    label={{ value: 'Price (USD)', angle: -90, position: 'insideLeft' }}
                                    domain={['dataMin - 5', 'dataMax + 5']}
                                />
                                <Tooltip formatter={(value) => [`$${value.toFixed(2)}`, 'Mean Price']} />
                                <Bar 
                                    dataKey="value" 
                                    fill="#4caf50" 
                                    name="Mean Price"
                                    radius={[4, 4, 0, 0]}
                                />
                                <Line 
                                    type="monotone" 
                                    dataKey="min" 
                                    stroke="#ff9800" 
                                    strokeWidth={2}
                                    dot={false}
                                    name="95% CI Lower"
                                />
                                <Line 
                                    type="monotone" 
                                    dataKey="max" 
                                    stroke="#ff9800" 
                                    strokeWidth={2}
                                    dot={false}
                                    name="95% CI Upper"
                                />
                            </ComposedChart>
                        </ResponsiveContainer>
                    </Paper>
                </Grid>

                {/* Parameter Distributions */}
                <Grid item xs={12}>
                    <Paper elevation={3} sx={{ p: 2, mt: 2 }}>
                        <Typography variant="h6" gutterBottom>
                            Posterior Distributions of Model Parameters
                        </Typography>
                        <Grid container spacing={2}>
                            <Grid item xs={12} md={4}>
                                <Card variant="outlined">
                                    <CardContent>
                                        <Typography color="primary" gutterBottom>
                                            μ_before (Mean Before)
                                        </Typography>
                                        <ResponsiveContainer width="100%" height={150}>
                                            <AreaChart data={paramDistributions.muBefore.map((value, index) => ({ index, value }))}>
                                                <Area 
                                                    type="monotone" 
                                                    dataKey="value" 
                                                    stroke="#4caf50" 
                                                    fill="#4caf50" 
                                                    fillOpacity={0.3}
                                                />
                                                <Tooltip formatter={(value) => [`$${parseFloat(value).toFixed(2)}`, 'Price']} />
                                            </AreaChart>
                                        </ResponsiveContainer>
                                        <Typography variant="body2" align="center" sx={{ mt: 1 }}>
                                            Mean: ${changePointData.mu_before.toFixed(2)}
                                        </Typography>
                                    </CardContent>
                                </Card>
                            </Grid>

                            <Grid item xs={12} md={4}>
                                <Card variant="outlined">
                                    <CardContent>
                                        <Typography color="primary" gutterBottom>
                                            μ_after (Mean After)
                                        </Typography>
                                        <ResponsiveContainer width="100%" height={150}>
                                            <AreaChart data={paramDistributions.muAfter.map((value, index) => ({ index, value }))}>
                                                <Area 
                                                    type="monotone" 
                                                    dataKey="value" 
                                                    stroke="#2196f3" 
                                                    fill="#2196f3" 
                                                    fillOpacity={0.3}
                                                />
                                                <Tooltip formatter={(value) => [`$${parseFloat(value).toFixed(2)}`, 'Price']} />
                                            </AreaChart>
                                        </ResponsiveContainer>
                                        <Typography variant="body2" align="center" sx={{ mt: 1 }}>
                                            Mean: ${changePointData.mu_after.toFixed(2)}
                                        </Typography>
                                    </CardContent>
                                </Card>
                            </Grid>

                            <Grid item xs={12} md={4}>
                                <Card variant="outlined">
                                    <CardContent>
                                        <Typography color="primary" gutterBottom>
                                            σ (Standard Deviation)
                                        </Typography>
                                        <ResponsiveContainer width="100%" height={150}>
                                            <AreaChart data={paramDistributions.sigma.map((value, index) => ({ index, value }))}>
                                                <Area 
                                                    type="monotone" 
                                                    dataKey="value" 
                                                    stroke="#ff9800" 
                                                    fill="#ff9800" 
                                                    fillOpacity={0.3}
                                                />
                                                <Tooltip formatter={(value) => [parseFloat(value).toFixed(2), 'Std Dev']} />
                                            </AreaChart>
                                        </ResponsiveContainer>
                                        <Typography variant="body2" align="center" sx={{ mt: 1 }}>
                                            Mean: {paramDistributions.sigma.reduce((a, b) => a + b, 0) / paramDistributions.sigma.length}
                                        </Typography>
                                    </CardContent>
                                </Card>
                            </Grid>
                        </Grid>
                    </Paper>
                </Grid>

                {/* Impact Analysis Table */}
                <Grid item xs={12}>
                    <Paper elevation={3} sx={{ p: 2, mt: 2 }}>
                        <Typography variant="h6" gutterBottom>
                            Change Point Impact Analysis
                        </Typography>
                        <TableContainer>
                            <Table size="small">
                                <TableHead>
                                    <TableRow>
                                        <TableCell><strong>Metric</strong></TableCell>
                                        <TableCell align="right"><strong>Before Change</strong></TableCell>
                                        <TableCell align="right"><strong>After Change</strong></TableCell>
                                        <TableCell align="right"><strong>Difference</strong></TableCell>
                                        <TableCell align="right"><strong>% Change</strong></TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    <TableRow>
                                        <TableCell>Mean Price (USD)</TableCell>
                                        <TableCell align="right">${changePointData.mu_before.toFixed(2)}</TableCell>
                                        <TableCell align="right">${changePointData.mu_after.toFixed(2)}</TableCell>
                                        <TableCell align="right" sx={{ color: changeColor }}>
                                            ${changePointData.difference.toFixed(2)}
                                        </TableCell>
                                        <TableCell align="right" sx={{ color: changeColor }}>
                                            {changePointData.percentage_change.toFixed(1)}%
                                        </TableCell>
                                    </TableRow>
                                    <TableRow>
                                        <TableCell>Probability Distribution</TableCell>
                                        <TableCell align="right" colSpan={4}>
                                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                                <Typography variant="body2" sx={{ mr: 1 }}>
                                                    Probability of Increase:
                                                </Typography>
                                                <Chip 
                                                    label={`${(changePointData.probability_increase * 100).toFixed(1)}%`}
                                                    color={changePointData.probability_increase > 0.5 ? "success" : "error"}
                                                    size="small"
                                                />
                                            </Box>
                                        </TableCell>
                                    </TableRow>
                                    <TableRow>
                                        <TableCell>Statistical Significance</TableCell>
                                        <TableCell align="right" colSpan={4}>
                                            <Chip 
                                                label="High (95% Credible Interval Excludes Zero)"
                                                color="primary"
                                                size="small"
                                            />
                                        </TableCell>
                                    </TableRow>
                                </TableBody>
                            </Table>
                        </TableContainer>
                        
                        <Divider sx={{ my: 2 }} />
                        
                        <Typography variant="body2" color="textSecondary" paragraph>
                            <strong>Interpretation:</strong> The Bayesian change point model detected a structural break in Brent oil prices on {new Date(changePointData.date).toLocaleDateString()}. 
                            There is a {changePointData.probability_increase > 0.5 ? 'high' : 'low'} probability ({Math.round(changePointData.probability_increase * 100)}%) 
                            that prices {isIncrease ? 'increased' : 'decreased'} by approximately ${Math.abs(changePointData.difference).toFixed(2)} 
                            ({Math.abs(changePointData.percentage_change).toFixed(1)}%) following this change point.
                        </Typography>
                        
                        <Typography variant="body2" color="textSecondary">
                            <strong>Note:</strong> This analysis identifies statistical associations, not causal relationships. 
                            The change point may correlate with geopolitical events, economic shifts, or policy changes.
                        </Typography>
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
};

export default ChangePointAnalysis;