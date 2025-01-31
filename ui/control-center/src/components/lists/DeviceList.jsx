/**
 * File: DeviceList.jsx
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
import React from 'react';
import DeviceItem from '../items/DeviceItem';
import {Grid, List} from '@mui/material';

function DeviceList({ devices, onDelete,  onEdit, onNuke, onViewDetails}) {
    return (
        <List>
            <Grid container>
                <Grid item>
                    {devices.map(device => (
                        <DeviceItem key={device.lan_ip_address} device={device} onNuke={onNuke} onDelete={onDelete} onEdit={onEdit} onViewDetails={onViewDetails} />
                    ))}
                </Grid>

            </Grid>
        </List>
    );
}

export default DeviceList;