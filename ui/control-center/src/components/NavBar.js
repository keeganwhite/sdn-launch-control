import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { AppBar, Toolbar, IconButton, Button, Grid, Drawer, List, ListItem, ListItemButton, ListItemText, Collapse } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import { Box } from '@mui/system';


const NavBar = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [openLobby, setOpenLobby] = useState(false);
    const [openHardware, setOpenHardware] = useState(false);
    const [openSystem, setOpenSystem] = useState(false);

    const handleClickLobby = () => {
        setOpenLobby(!openLobby);
    };

    const handleClickHardware = () => {
        setOpenHardware(!openHardware);
    };

    const handleClickSystem = () => {
        setOpenSystem(!openSystem);
    };

    const toggleDrawer = (open) => (event) => {
        if (event.type === 'keydown' && (event.key === 'Tab' || event.key === 'Shift')) {
            return;
        }
        setIsOpen(open);
    };

    const handleMenuItemClick = (event) => {
        event.stopPropagation();
    };


    return (
        <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
            <Toolbar>
                <Grid container direction="row" justifyContent="space-between" alignItems="center" sx={{ padding: '0 20px' }}>
                    <Grid item>
                        <IconButton onClick={toggleDrawer(true)} edge="start" color="inherit" aria-label="menu">
                            <MenuIcon />
                        </IconButton>
                        <Drawer anchor='left' open={isOpen} onClose={toggleDrawer(false)} sx={{ '& .MuiDrawer-paper': { backgroundColor: '#02032F', color: 'white' }}}>
                            <Box sx={{ width: 250, paddingTop: '100px' }} role="presentation">
                                <List>
                                    {/* Lobby Heading */}
                                    <ListItemButton onClick={(event) => {handleMenuItemClick(event); handleClickLobby();}}>
                                        <ListItemText primary="Lobby" />
                                        {openLobby ? <ExpandLess /> : <ExpandMore />}
                                    </ListItemButton>
                                    <Collapse in={openLobby} timeout="auto" unmountOnExit>
                                        <List component="div" disablePadding>
                                            <ListItemButton sx={{ pl: 4 }} component={Link} to="/">
                                                <ListItemText primary="Home" />
                                            </ListItemButton>
                                        </List>
                                    </Collapse>

                                    {/* Hardware Heading */}
                                    <ListItemButton onClick={handleClickHardware}>
                                        <ListItemText primary="Hardware" />
                                        {openHardware ? <ExpandLess /> : <ExpandMore />}
                                    </ListItemButton>
                                    <Collapse in={openHardware} timeout="auto" unmountOnExit>
                                        <List component="div" disablePadding>
                                            <ListItemButton sx={{ pl: 4 }} component={Link} to="/controllers">
                                                <ListItemText primary="Controllers" />
                                            </ListItemButton>
                                            <ListItemButton sx={{ pl: 4 }} component={Link} to="/devices">
                                                <ListItemText primary="Devices" />
                                            </ListItemButton>
                                        </List>
                                    </Collapse>

                                    {/* System Heading */}
                                    <ListItemButton onClick={handleClickSystem}>
                                        <ListItemText primary="System" />
                                        {openSystem ? <ExpandLess /> : <ExpandMore />}
                                    </ListItemButton>
                                    <Collapse in={openSystem} timeout="auto" unmountOnExit>
                                        <List component="div" disablePadding>
                                            <ListItemButton sx={{ pl: 4 }} component={Link} to="/">
                                                <ListItemText primary="Plugins" />
                                            </ListItemButton>
                                        </List>
                                    </Collapse>
                                </List>
                            </Box>
                        </Drawer>
                    </Grid>
                    <Grid item>

                            <img src="./logo100.png" alt="Logo" style={{height: '80px', padding: '10px' }}/>

                    </Grid>
                </Grid>
            </Toolbar>
        </AppBar>
    );
};



export default NavBar;
