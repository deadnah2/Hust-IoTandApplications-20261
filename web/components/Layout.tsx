import React, { useState } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Chip,
  Menu,
  MenuItem,
  Drawer,
  List,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Box,
  Divider,
  Button,
  Collapse
} from "@mui/material";
import {
  Menu as MenuIcon,
  Home as HomeIcon,
  MeetingRoom as RoomIcon,
  Add as AddIcon,
  AccountCircle,
  ExpandLess,
  ExpandMore,
  AddHome as AddHomeIcon,
  Delete as DeleteIcon
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { House, Room } from "../types";
import { USE_MOCK, ROUTES } from "../constants";

interface LayoutProps {
  houses: House[];
  roomsByHome: Record<string, Room[]>; // { homeId: Room[] }
  selectedHomeId: string | null;
  selectedRoomId: string | null;
  onSelectHome: (id: string) => void;
  onSelectRoom: (homeId: string, roomId: string) => void;
  onAddHome: () => void;
  onAddRoom: (homeId: string) => void;
  onDeleteHome: (id: string) => void;
  onDeleteRoom: (id: string) => void;
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({
  houses,
  roomsByHome,
  selectedHomeId,
  selectedRoomId,
  onSelectHome,
  onSelectRoom,
  onAddHome,
  onAddRoom,
  onDeleteHome,
  onDeleteRoom,
  children
}) => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [expandedHomeId, setExpandedHomeId] = useState<string | null>(selectedHomeId);

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

  const handleHomeClick = (homeId: string) => {
    if (expandedHomeId === homeId) {
      setExpandedHomeId(null);
    } else {
      setExpandedHomeId(homeId);
      onSelectHome(homeId);
    }
  };

  const handleRoomClick = (homeId: string, roomId: string) => {
    onSelectRoom(homeId, roomId);
  };

  const drawerWidth = 280;

  const drawerContent = (
    <div className="flex flex-col h-full bg-slate-50">
      <Toolbar className="bg-slate-100">
        <Typography variant="h6" noWrap component="div" className="text-slate-700 font-bold">
          My Homes
        </Typography>
      </Toolbar>
      <Divider />
      
      {/* Create Home Button */}
      <Box className="p-3">
        <Button 
          variant="outlined" 
          fullWidth 
          startIcon={<AddHomeIcon />}
          onClick={onAddHome}
          color="primary"
          sx={{ borderStyle: 'dashed' }}
        >
          Create New Home
        </Button>
      </Box>
      
      <Divider />
      
      {/* Homes List with nested Rooms */}
      <List className="flex-grow overflow-y-auto">
        {houses.length === 0 ? (
          <Box className="p-4 text-center">
            <Typography variant="body2" className="text-gray-500">
              No homes yet. Create your first home!
            </Typography>
          </Box>
        ) : (
          houses.map((house) => {
            const isExpanded = expandedHomeId === house.id;
            const rooms = roomsByHome[house.id] || [];
            
            return (
              <React.Fragment key={house.id}>
                {/* Home Item */}
                <ListItemButton 
                  onClick={() => handleHomeClick(house.id)}
                  selected={selectedHomeId === house.id && !selectedRoomId}
                  sx={{
                    bgcolor: isExpanded ? 'rgba(37, 99, 235, 0.04)' : 'transparent',
                    "&.Mui-selected": {
                      backgroundColor: "#dbeafe",
                    }
                  }}
                >
                  <ListItemIcon>
                    <HomeIcon color={isExpanded ? "primary" : "inherit"} />
                  </ListItemIcon>
                  <ListItemText 
                    primary={house.name} 
                    secondary={house.location || "No location"}
                    primaryTypographyProps={{ 
                      fontWeight: isExpanded ? 'bold' : 'medium',
                      color: isExpanded ? 'primary' : 'inherit'
                    }}
                    secondaryTypographyProps={{
                      fontSize: '0.75rem'
                    }}
                  />
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      if (confirm(`Delete "${house.name}" and all its rooms?`)) {
                        onDeleteHome(house.id);
                      }
                    }}
                    sx={{ opacity: 0.5, '&:hover': { opacity: 1, color: 'error.main' } }}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                  {isExpanded ? <ExpandLess /> : <ExpandMore />}
                </ListItemButton>
                
                {/* Rooms Collapse */}
                <Collapse in={isExpanded} timeout="auto" unmountOnExit>
                  <List component="div" disablePadding>
                    {rooms.length === 0 ? (
                      <Box className="pl-8 py-2">
                        <Typography variant="caption" className="text-gray-400 italic">
                          No rooms yet
                        </Typography>
                      </Box>
                    ) : (
                      rooms.map((room) => (
                        <ListItemButton
                          key={room.id}
                          sx={{ pl: 4 }}
                          selected={selectedRoomId === room.id}
                          onClick={() => handleRoomClick(house.id, room.id)}
                        >
                          <ListItemIcon>
                            <RoomIcon 
                              fontSize="small" 
                              color={selectedRoomId === room.id ? "primary" : "inherit"} 
                            />
                          </ListItemIcon>
                          <ListItemText 
                            primary={room.name}
                            primaryTypographyProps={{
                              fontSize: '0.9rem'
                            }}
                          />
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              if (confirm(`Delete room "${room.name}"?`)) {
                                onDeleteRoom(room.id);
                              }
                            }}
                            sx={{ opacity: 0.5, '&:hover': { opacity: 1, color: 'error.main' } }}
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </ListItemButton>
                      ))
                    )}
                    
                    {/* Add Room Button */}
                    <ListItemButton 
                      sx={{ pl: 4 }} 
                      onClick={() => onAddRoom(house.id)}
                      className="text-blue-600"
                    >
                      <ListItemIcon>
                        <AddIcon fontSize="small" color="primary" />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Add Room" 
                        primaryTypographyProps={{ 
                          color: "primary", 
                          fontWeight: "medium",
                          fontSize: '0.9rem'
                        }} 
                      />
                    </ListItemButton>
                  </List>
                </Collapse>
                
                <Divider variant="middle" />
              </React.Fragment>
            );
          })
        )}
      </List>
      
      <Box className="p-4 text-xs text-gray-400 text-center border-t">
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
