/**
 * File: DeviceStatsGraph.jsx
 * Copyright (C) 2025 Keegan White
 *
 * This file is part of the SDN Launch Control project.
 *
 * This project is licensed under the GNU General Public License v3.0 (GPL-3.0),
 * available at: https://www.gnu.org/licenses/gpl-3.0.en.html#license-text
 *
 * Contributions to this project are governed by a Contributor License Agreement (CLA).
 * By submitting a contribution, contributors grant Keegan White exclusive rights to
 * the contribution, including the right to relicense it under a different license
 * at the copyright owner's discretion.
 *
 * Unless required by applicable law or agreed to in writing, software distributed
 * under this license is provided "AS IS", WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
 * either express or implied. See the GNU General Public License for more details.
 *
 * For inquiries, contact Keegan White at keeganwhite@taurinetech.com.
 */
import React, { useEffect, useState } from 'react';
import {LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend} from 'recharts';
import {Card, CardContent, Typography} from "@mui/material";
import Box from "@mui/material/Box";

const DeviceStatsGraph = ( {targetIpAddress} ) => {
    const [data, setData] = useState([]);
    const wsUrl = "ws://localhost:8000/ws/device_stats/"

    useEffect(() => {
        const ws = new WebSocket(wsUrl);
        ws.onmessage = (event) => {
            const stats = JSON.parse(event.data);
            if (stats.data.ip_address === targetIpAddress) {  // Filter by IP address
                const newData = {
                    time: new Date().toISOString().substr(11, 8), // Extract HH:MM:SS from ISO string
                    ...stats.data
                };

                setData((currentData) => {
                    const newDataArray = [...currentData, newData];
                    // Keep only the last 60 seconds of data
                    const sixtySecondsAgo = new Date(new Date() - 60000).toISOString().substr(11, 8);
                    return newDataArray.filter(item => item.time >= sixtySecondsAgo);
                });
            }
        };

        return () => {
            ws.close();
        };
    }, [wsUrl]);

    return (
        <Card raised sx={{ margin: 4, bgcolor: '#02032F', }}>
            <CardContent>
                <Typography variant="h2" sx={{ mb: 2, color: "#FFF" }}>Device Stats for {targetIpAddress}</Typography>
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 300, width: '100%' }}>
                    {data.length > 0 ? (
                        <LineChart width={700} height={400} data={data}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="time" />
                            <YAxis domain={[0, 100]} />
                            <Tooltip />
                            <Legend verticalAlign="bottom" height={36}/>
                            <Line type="monotone" dataKey="cpu" stroke="#8884d8" name="CPU Usage (%)" activeDot={{ r: 8 }} />
                            <Line type="monotone" dataKey="memory" stroke="#82ca9d" name="Memory Usage (%)" />
                            <Line type="monotone" dataKey="disk" stroke="#ffc658" name="Disk Usage (%)" />
                        </LineChart>
                    ) : <div style={{ color: '#fff' }}>No data available</div>}
                </Box>
            </CardContent>
        </Card>
    );
};

export default DeviceStatsGraph;
