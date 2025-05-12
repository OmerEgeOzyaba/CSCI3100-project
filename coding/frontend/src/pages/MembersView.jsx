import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  List,
  ListItem,
  ListItemText,
  Button,
  Box,
  Divider,
  CircularProgress,
  ListItemIcon,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Snackbar,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { Person as PersonIcon, Add as AddIcon } from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { getMembers, sendInvitation } from '../services/api'

const MembersPage = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const group = location.state?.group;
  const groupId = group?.id;
  const groupName = group?.name;

  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openInviteDialog, setOpenInviteDialog] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('reader');
  const [inviteLoading, setInviteLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });

  useEffect(() => {
    if (!groupId) {
      console.error('Group ID not provided');
      navigate('/dashboard');
      return;
    }

    const fetchGroup = async () => {
      try {
        const response = await getMembers(groupId);
        const fetchedMembers = response.data.group.members || [];
        setMembers(fetchedMembers);
      } catch (error) {
        console.error('Error fetching group members:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchGroup();
  }, [groupId, navigate]);

  const handleOk = () => {
    navigate('/dashboard');
  };

  const handleOpenInviteDialog = () => {
    setInviteEmail('');
    setInviteRole('reader');
    setOpenInviteDialog(true);
  };

  const handleCloseInviteDialog = () => {
    setOpenInviteDialog(false);
  };

  const handleSendInvite = async () => {
    if (!inviteEmail || !inviteEmail.includes('@')) {
      setSnackbar({
        open: true,
        message: 'Please enter a valid email address',
        severity: 'error'
      });
      return;
    }

    setInviteLoading(true);
    try {
      await sendInvitation(inviteEmail, groupId, inviteRole);
      setOpenInviteDialog(false);
      setSnackbar({
        open: true,
        message: `Invitation sent to ${inviteEmail}`,
        severity: 'success'
      });
    } catch (error) {
      console.error('Error sending invitation:', error);
      let errorMessage = 'Failed to send invitation';
      if (error.response && error.response.data && error.response.data.error) {
        errorMessage = error.response.data.error;
      }
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
    } finally {
      setInviteLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <Container maxWidth="sm">
      <Box mt={5}>
        <Box display="flex" flexDirection="column" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h4" gutterBottom>
            {groupName} Members:
          </Typography>
          <Button 
            variant="contained" 
            color="primary" 
            startIcon={<AddIcon />}
            onClick={handleOpenInviteDialog}
          >
            Invite
          </Button>
        </Box>

        {loading ? (
          <Box display="flex" justifyContent="center" mt={4}>
            <CircularProgress />
          </Box>
        ) : (
          <List data-testid="members-list">
            {members.map((user, index) => (
              <React.Fragment key={index}>
                <ListItem>
                  <ListItemIcon>
                    <PersonIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={user.email}
                    secondary={`Role: ${user.role}`}
                  />
                </ListItem>
                <Divider />
              </React.Fragment>
            ))}
          </List>
        )}

        <Box mt={4} display="flex" justifyContent="center">
          <Button variant="contained" color="primary" onClick={handleOk}>
            OK
          </Button>
        </Box>
      </Box>

      {/* Invite User Dialog */}
      <Dialog open={openInviteDialog} onClose={handleCloseInviteDialog}>
        <DialogTitle>Invite User to {groupName}</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="email"
            label="Email Address"
            type="email"
            fullWidth
            variant="outlined"
            value={inviteEmail}
            onChange={(e) => setInviteEmail(e.target.value)}
            sx={{ mb: 2 }}
          />
          <FormControl fullWidth variant="outlined">
            <InputLabel id="role-select-label">Role</InputLabel>
            <Select
              labelId="role-select-label"
              id="role"
              value={inviteRole}
              onChange={(e) => setInviteRole(e.target.value)}
              label="Role"
            >
              <MenuItem value="admin">Admin</MenuItem>
              <MenuItem value="contributor">Contributor</MenuItem>
              <MenuItem value="reader">Reader</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseInviteDialog} disabled={inviteLoading}>Cancel</Button>
          <Button 
            onClick={handleSendInvite} 
            variant="contained" 
            color="primary"
            disabled={inviteLoading || !inviteEmail}
          >
            {inviteLoading ? 'Sending...' : 'Send Invitation'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar 
        open={snackbar.open} 
        autoHideDuration={6000} 
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default MembersPage;
