import React, {useEffect, useState} from 'react';
import {
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Button,
    TextField,
    FormControl,
    InputLabel, Select, MenuItem
} from '@mui/material';
import theme from "../theme";

function EditDeviceDialog({ open, handleClose, device, handleUpdate }) {
    const [editedDevice, setEditedDevice] = useState({
        name: '',
        lan_ip_address: '',
        device_type: '',
        os_type: 'ubuntu_20_server',
        openflow_version: '',
        ovs_enabled: false,
        ovs_version: '',
        ports: 0,
    });


    useEffect(() => {
        if (device) {
            setEditedDevice({
                name: device.name || '',
                lan_ip_address: device.lan_ip_address || '',
                device_type: device.device_type || '',
                os_type: device.os_type || '',
                openflow_version: device.openflow_version || '',
                ovs_enabled: device.ovs_enabled || false,
                ovs_version: device.ovs_version || '',
                ports: device.ports || 0,
            });
        }
    }, [device]);

    const handleFieldChange = (e) => {
        setEditedDevice({ ...editedDevice, [e.target.name]: e.target.value });
    };

    const handleSubmit = () => {
        handleUpdate(device.lan_ip_address, editedDevice);
    };

    if (!device) {
        return null;
    }

    return (
        <Dialog open={open} onClose={handleClose}>
            <DialogTitle>Edit Basic Device Details</DialogTitle>
            <DialogContent>
                <TextField
                    autoFocus
                    margin="dense"
                    name="name"
                    label="Device Name"
                    type="text"
                    fullWidth
                    value={editedDevice.name}
                    onChange={handleFieldChange}
                />
                <TextField
                    margin="dense"
                    name="lan_ip_address"
                    label="LAN IP Address"
                    type="text"
                    fullWidth
                    value={editedDevice.lan_ip_address}
                    onChange={handleFieldChange}
                />

                <FormControl fullWidth margin="dense">
                    <InputLabel id="os-select-label">Operating System</InputLabel>
                    <Select
                        labelId="os-select-label"
                        value={editedDevice.os_type || ''}
                        onChange={handleFieldChange}
                        label="Operating System"
                    >
                        <MenuItem value={'ubuntu_20_server'}>Ubuntu 20.04 Server</MenuItem>
                    </Select>
                </FormControl>
                <FormControl fullWidth margin="normal" >
                    <InputLabel>Device Type</InputLabel>
                    <Select
                        name="device_type"
                        value={editedDevice.device_type}
                        label="Device Type"
                        onChange={handleFieldChange}
                    >
                        <MenuItem value="switch">Switch</MenuItem>
                        <MenuItem value="access_point">Access Point</MenuItem>
                        <MenuItem value="server">Server</MenuItem>
                    </Select>
                </FormControl>

            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose} sx={{ color: theme.palette.button_red.main }}>Cancel</Button>
                <Button onClick={handleSubmit} sx={{ color: theme.palette.button_green.main }}>Update</Button>
            </DialogActions>
        </Dialog>
    );
}

export default EditDeviceDialog;