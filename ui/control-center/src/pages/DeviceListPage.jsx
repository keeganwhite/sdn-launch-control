/**
 * File: ControllerListPage.jsx
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
import React, {useEffect, useState} from 'react';
import NavBar from "../components/NavBar";
import Box from "@mui/material/Box";
import Footer from "../components/Footer";
import ConfirmDeleteDialog from "../components/ConfirmDeleteDialogue";
import Alert from '@mui/material/Alert';
import axios from "axios";
import DeviceList from "../components/lists/DeviceList";
import Theme from "../theme";
import EditDeviceDialog from "../components/EditDeviceDialogue";
import theme from "../theme";
import { useNavigate } from 'react-router-dom';
import {Backdrop, CircularProgress, Typography} from "@mui/material";
import AddDeviceDialogue from "../components/AddDeviceDialogue";
import NukeDeviceDialogue from "../components/NukeDeviceDialogue";

const DeviceListPage = () => {
    const [openDeleteDialogue, setOpenDeleteDialogue] = useState(false);
    const [openNukeDialogue, setOpenNukeDialogue] = useState(false);
    const [deviceToDelete, setDeviceToDelete] = useState(null);
    const [devices, setDevices] = useState([]);
    const [alert, setAlert] = useState({ show: false, message: '' });
    const [successAlert, setSuccessAlert] = useState({ show: false, message: '' });
    const [openEditDialogue, setOpenEditDialogue] = useState(false);
    const [deviceToEdit, setDeviceToEdit] = useState({ name: '', ip_address: '', device_type: '' });
    const [openAddDialog, setOpenAddDialog] = useState(false);
    const [responseMessage, setResponseMessage] = useState('');
    const [responseType, setResponseType] = useState(''); // 'success' or 'error'
    const [error, setError] = useState(null);
    const [openPortDialogue, setOpenPortDialogue] = useState(false)
    const [loading, setLoading] = useState(false);
    const [isDeleteLoading, setIsDeleteLoading] = useState(false);
    const [isNukeLoading, setIsNukeLoading] = useState(false);
    const navigate = useNavigate();


        const handleDetailsClick = async (ipAddress) => {
            setLoading(true);
            try {
                const response = await axios.get(`http://localhost:8000/check-connection/${ipAddress}/`);
                if (response.data.status === 'success') {
                    navigate(`/devices/${ipAddress}`);
                } else {
                    // Handle unsuccessful connection check
                    setAlert({ show: true, message: 'Device connection failed.' });
                }
            } catch (error) {
                // Handle error
                console.error('Error:', error || 'Deployment failed');
                setResponseMessage(error.response?.data?.message || error.message || 'Deployment failed');
                setResponseType('error');
            } finally {
                setLoading(false);
            }
        };
    const handleCloseAlert = () => {
        setResponseMessage('');
    };
    const handleDeleteClick = (device) => {
        setDeviceToDelete(device);
        setOpenDeleteDialogue(true);
    };
    const handleNukeClick = (device) => {
        setDeviceToDelete(device);
        setOpenNukeDialogue(true);
    };


    const handleCloseDeleteDialog = () => {
        setOpenDeleteDialogue(false);
    };
    const handleCloseNukeDialog = () => {
        setOpenNukeDialogue(false);
    };
    const handleCloseAddDevice = () => {
        fetchDevices();
    };

    const handleConfirmDelete = async () => {
        if (deviceToDelete) {
            try {
                setIsDeleteLoading(true);
                const payload = {
                    lan_ip_address: deviceToDelete.lan_ip_address,
                };

                const response = await axios.delete('http://localhost:8000/delete-device/', { data: payload })
                    .then(response =>
                {

                    setResponseMessage('Successfully deleted device.');
                    setResponseType('success');
                    fetchDevices()
                }).catch(error => {
                        setResponseMessage(`Failed to delete device. Please check your connection to the device`);
                        setResponseType('error');
                }).finally(() =>{
                        setIsDeleteLoading(false);
                        setOpenDeleteDialogue(false);
                        setDeviceToDelete(null);
                    });

                // setDevices(devices.filter(device => device.lan_ip_address !== deviceToDelete.lan_ip_address));

            } catch (error) {
                // console.error('Error deleting device:', error);
                setResponseMessage(`Failed to delete device: ${error.message}`);
                setResponseType('error');
            }
        }

    };

    const handleConfirmNuke = async () => {
        if (deviceToDelete) {
            try {
                setIsNukeLoading(true);
                const payload = {
                    lan_ip_address: deviceToDelete.lan_ip_address,
                };

                const response = await axios.delete('http://localhost:8000/force-delete-device/', { data: payload })
                    .then(response =>
                    {
                        setResponseMessage('Successfully deleted device.');
                        setResponseType('success');
                        fetchDevices()
                    }).catch(error => {
                        setResponseMessage(`Failed to delete device: ${error}`);
                        setResponseType('error');
                    }).finally(() =>{
                        setIsNukeLoading(false);
                        setOpenNukeDialogue(false);
                        setDeviceToDelete(null);
                    });

            } catch (error) {
                // console.error('Error deleting device:', error);
                setResponseMessage(`Failed to delete device: ${error.message}`);
                setResponseType('error');
            }
        }

    };


    const handleUpdateDevice = async (oldIpAddress, updatedDevice) => {
        console.log('Updating device...');

        try {
            const response = await fetch(`http://localhost:8000/update-device/${oldIpAddress}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updatedDevice),
            });

            const result = await response.json();

            if (response.ok) {
                console.log('Device updated successfully.');
                fetchDevices()
                setResponseMessage('Successfully Updated device.');
                setResponseType('success');
                setOpenEditDialogue(false);
            } else {
                console.error('Failed to update device:', result.message);
                setResponseMessage(`Failed to update device: ${result.message}`);
                setResponseType('error');
                setOpenEditDialogue(false);

            }
        } catch (error) {
            console.error('Error updating device:', error);
            setResponseMessage(`Failed to update device: ${error}`);
            setResponseType('error');
            setOpenEditDialogue(false);

        }
    };
    const handleEditClick = (device) => {
        console.log(device)
        setDeviceToEdit(device);
        console.log(device)
        setOpenEditDialogue(true);
    };
    const handleEditPortClick = (device) => {
        setDeviceToEdit(device);
        console.log(device)
        setOpenPortDialogue(true);
    };

    const handleClosePortDialogue = () => {
        setOpenPortDialogue(false);
    }
    const selectedDeviceForPortManagement = (device) => {
        console.log('selecting ports')
        setDeviceToEdit(device);
        console.log(device)
        setOpenEditDialogue(true);
    }
    const handleCloseEditDialogue = () => {
        setOpenEditDialogue(false);
    };
    const fetchDevices = async () => {
        try {
            const response = await axios.get('http://localhost:8000/devices/');
            setDevices(response.data); // Axios automatically handles JSON parsing
            console.log(response.data)
        } catch (error) {
            console.error('Error fetching devices:', error);
            setError(error.message);
        }
    };
    useEffect(() => {


        fetchDevices();
    }, []);
    const handleClose = () => {
        // Reset the error state to null
        setError(null);
    };
    return (

            <Box
                sx={{
                    minHeight: '100vh',
                    display: 'flex',
                    flexDirection: 'column',
                    backgroundColor: '#7456FD',
                }}
            >
                <NavBar />
                <Backdrop open={loading} style={{ zIndex: theme.zIndex.drawer + 1 }}>
                    <CircularProgress style={{'color': "#7456FD"}} />
                </Backdrop>
                <Box sx={{ flexGrow: 1, paddingTop: '100px', overflow: 'auto' }}>
                    <Typography variant="h1" sx={{ mb: 2, p: 3, color: "#FFF" }}>Hardware: Devices</Typography>
                <Box
                    sx={{
                        flexGrow: 1,
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'center',
                        alignItems: 'center',
                        backgroundSize: 'cover',
                        backgroundPosition: 'center',
                    }}
                >
                    {responseMessage && (
                        <Alert severity={responseType} onClose={handleCloseAlert}>
                            {responseMessage}
                        </Alert>
                    )}

                    <Box
                        sx={{
                            flexGrow: 1,
                            display: 'flex',
                            justifyContent: 'center',
                            alignItems: 'start',
                            paddingBottom: '50px',
                            margin: Theme.spacing(2),
                        }}
                    >

                        <DeviceList devices={devices}
                                    onDelete={handleDeleteClick}
                                    onEdit={handleEditClick}
                                    onNuke={handleNukeClick}
                                    // onEditPorts={handleEditPortClick}
                                    onViewDetails={handleDetailsClick}
                        />
                        <ConfirmDeleteDialog
                            open={openDeleteDialogue}
                            handleClose={handleCloseDeleteDialog}
                            handleConfirm={handleConfirmDelete}
                            itemName='device'
                            isLoading={isDeleteLoading}
                        />
                        <NukeDeviceDialogue
                            open={openNukeDialogue}
                            handleClose={handleCloseNukeDialog}
                            handleConfirm={handleConfirmNuke}
                            isLoading={isNukeLoading}
                        />
                        <EditDeviceDialog
                            open={openEditDialogue}
                            handleClose={handleCloseEditDialogue}
                            device={deviceToEdit}
                            handleUpdate={handleUpdateDevice}
                        />

                    </Box>
                    </Box>
                <AddDeviceDialogue fetchDevices={fetchDevices} />
                </Box>
                <Footer />
            </Box>

    );
}

export default DeviceListPage