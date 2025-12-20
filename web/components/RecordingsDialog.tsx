import React from "react";
import { Dialog, DialogTitle, DialogContent, List, ListItem, ListItemText, ListItemAvatar, Avatar, IconButton } from "@mui/material";
import { PlayArrow, History as HistoryIcon } from "@mui/icons-material";

interface RecordingsDialogProps {
  open: boolean;
  onClose: () => void;
  deviceName: string;
}

export const RecordingsDialog: React.FC<RecordingsDialogProps> = ({ open, onClose, deviceName }) => {
  const mockRecordings = [
    { id: "1", time: "Today, 10:30 AM", duration: "02:15" },
    { id: "2", time: "Today, 08:15 AM", duration: "01:45" },
    { id: "3", time: "Yesterday, 11:00 PM", duration: "10:00" },
    { id: "4", time: "Yesterday, 06:45 PM", duration: "05:20" },
  ];

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle className="flex items-center gap-2">
        <HistoryIcon color="primary" />
        Recordings: {deviceName}
      </DialogTitle>
      <DialogContent dividers>
        <List>
          {mockRecordings.map((rec) => (
            <ListItem
              key={rec.id}
              secondaryAction={
                <IconButton edge="end">
                  <PlayArrow />
                </IconButton>
              }
            >
              <ListItemAvatar>
                <Avatar variant="rounded" src={`https://picsum.photos/seed/${rec.id}/100/100`} />
              </ListItemAvatar>
              <ListItemText
                primary={rec.time}
                secondary={`Duration: ${rec.duration}`}
              />
            </ListItem>
          ))}
        </List>
      </DialogContent>
    </Dialog>
  );
};
