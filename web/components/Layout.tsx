import React, { useState } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Chip,
  Avatar,
  Menu,
  MenuItem,
  Drawer,
  List,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Box,
  Divider,
  Button
} from "@mui/material";
import {
  Menu as MenuIcon,
  Home as HomeIcon,
  MeetingRoom as RoomIcon,
  Add as AddIcon,
  AccountCircle
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { House, Room } from "../types";
import { USE_MOCK, ROUTES } from "../constants";

interface LayoutProps {
  houses: House[];
  rooms: Room[];
  selectedRoomId: string | null;
  onSelectRoom: (id: string) => void;
  onAddRoom: () => void;
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({
  houses,
  rooms,
  selectedRoomId,
  onSelectRoom,
  onAddRoom,
  children
}) => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    localStorage.removeItem("id_token");
    navigate(ROUTES.LOGIN);
  };

  const drawerWidth = 260;

  const drawerContent = (
    <div className="flex flex-col h-full bg-slate-50">
      <Toolbar className="bg-slate-100">
        <Typography variant="h6" noWrap component="div" className="text-slate-700 font-bold">
          My Homes
        </Typography>
      </Toolbar>
      <Divider />
      <Box className="p-4">
        {houses.length > 0 ? (
          <Button variant="outlined" fullWidth startIcon={<HomeIcon />}>
            {houses[0].name}
          </Button>
        ) : (
          <Typography variant="body2" className="text-gray-500">No houses found</Typography>
        )}
      </Box>
      <Divider />
      <List className="flex-grow">
        <Typography variant="overline" className="px-4 text-gray-500 font-bold">
          Rooms
        </Typography>
        {rooms.map((room) => (
          <ListItemButton
            key={room.id}
            selected={selectedRoomId === room.id}
            onClick={() => onSelectRoom(room.id)}
            sx={{
              "&.Mui-selected": {
                backgroundColor: "#e0f2fe", // blue-100
                borderRight: "4px solid #0288d1"
              }
            }}
          >
            <ListItemIcon>
              <RoomIcon color={selectedRoomId === room.id ? "primary" : "inherit"} />
            </ListItemIcon>
            <ListItemText primary={room.name} />
          </ListItemButton>
        ))}
        <ListItemButton onClick={onAddRoom} className="text-blue-600">
          <ListItemIcon>
            <AddIcon color="primary" />
          </ListItemIcon>
          <ListItemText primary="Add Room" primaryTypographyProps={{ color: "primary", fontWeight: "medium" }} />
        </ListItemButton>
      </List>
      <Box className="p-4 text-xs text-gray-400 text-center">
         v0.1.0 Alpha
      </Box>
    </div>
  );

  return (
    <Box sx={{ display: "flex" }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, bgcolor: 'white', color: 'black', boxShadow: 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={() => setMobileOpen(!mobileOpen)}
            sx={{ mr: 2, display: { sm: "none" } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 2 }}>
            Smart Home
            <Chip
              label={USE_MOCK ? "MOCK API" : "LIVE API"}
              color={USE_MOCK ? "warning" : "success"}
              size="small"
              variant="outlined"
            />
          </Typography>

          <div>
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleMenu}
              color="inherit"
            >
              <AccountCircle />
            </IconButton>
            <Menu
              id="menu-appbar"
              anchorEl={anchorEl}
              anchorOrigin={{
                vertical: "top",
                horizontal: "right",
              }}
              keepMounted
              transformOrigin={{
                vertical: "top",
                horizontal: "right",
              }}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem onClick={handleClose}>Profile</MenuItem>
              <MenuItem onClick={handleLogout}>Logout</MenuItem>
            </Menu>
          </div>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        aria-label="mailbox folders"
      >
        {/* Mobile Drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: "block", sm: "none" },
            "& .MuiDrawer-paper": { boxSizing: "border-box", width: drawerWidth },
          }}
        >
          {drawerContent}
        </Drawer>
        {/* Desktop Drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: "none", sm: "block" },
            "& .MuiDrawer-paper": { boxSizing: "border-box", width: drawerWidth, top: '64px', height: 'calc(100% - 64px)' },
          }}
          open
        >
          {drawerContent}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{ flexGrow: 1, p: 3, width: { sm: `calc(100% - ${drawerWidth}px)` }, mt: '64px', minHeight: '100vh', bgcolor: '#f8fafc' }}
      >
        {children}
      </Box>
    </Box>
  );
};
