import React, { useState, useEffect } from 'react'
import {
  Container,
  Typography,
  Box,
  AppBar,
  Toolbar,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  TextField,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Divider,
  Paper,
  InputAdornment,
  CircularProgress
} from '@mui/material'
import {
  Add as AddIcon,
  Search as SearchIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  Notifications as NotificationsIcon,
  Person as PersonIcon,
  Group as GroupIcon,
  Assignment as AssignmentIcon
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { getGroups } from '../services/api'

export default function Home() {
  const navigate = useNavigate()

  const handleEditGroup = (group) => {
    navigate('/group-edit', { state: { group } });
  };

  const handleViewMembers = (group) => {
    navigate('/members-view', { state: { group } });
  };

  const [groups, setGroups] = useState([]);
  const [groupLoading, setGroupLoading] = useState(true);

  useEffect(() => {
    const fetchGroup = async () => {
      try {
        const response = await getGroups();
        const groups = response.data.groups || [];
        setGroups(groups);
      } catch (error) {
        console.error('Error fetching groups:', error);
      } finally {
        setGroupLoading(false);
      }
    };

    fetchGroup();
  }, [navigate]);

  // Mock data for demonstration
  const [tasks] = useState([
    { id: 1, title: 'Complete project report', dueDate: '2023-06-15' },
    { id: 2, title: 'Prepare presentation', dueDate: '2023-06-10' },
  ])

  const [invites] = useState([
    { id: 1, groupName: 'Team Gamma', from: 'john.doe@example.com' },
    { id: 2, groupName: 'Project Delta', from: 'jane.smith@example.com' },
  ])

  return (
    <>
      {/* App Bar Navigation */}
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            CULater
          </Typography>
          <Button color="inherit" startIcon={<PersonIcon />}>
            Profile
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4 }}>
        {/* Welcome Header */}
        <Box sx={{ mb: 4, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Welcome to CULater Dashboard
          </Typography>
        </Box>

        {/* Main Dashboard Grid */}
        <Grid container spacing={4}>
          {/* Feature 1: Create/View Tasks */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h5" component="div" gutterBottom>
                  Tasks
                </Typography>

                {/* Task Search */}
                <TextField
                  fullWidth
                  placeholder="Search for task"
                  variant="outlined"
                  size="small"
                  margin="normal"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <SearchIcon />
                      </InputAdornment>
                    ),
                  }}
                />

                {/* Task List */}
                <Paper variant="outlined" sx={{ mt: 2, maxHeight: 300, overflow: 'auto' }}>
                  <List>
                    {tasks.map((task) => (
                      <React.Fragment key={task.id}>
                        <ListItem>
                          <ListItemText
                            primary={task.title}
                            secondary={`Due: ${task.dueDate}`}
                          />
                        </ListItem>
                        <Divider />
                      </React.Fragment>
                    ))}
                    {tasks.length === 0 && (
                      <ListItem>
                        <ListItemText primary="No tasks found" />
                      </ListItem>
                    )}
                  </List>
                </Paper>
              </CardContent>
              <CardActions>
                <Button startIcon={<AddIcon />} size="small">
                  Add New Task
                </Button>
              </CardActions>
            </Card>
          </Grid>

          {/* Feature 2: Create/Manage Groups */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h5" component="div" gutterBottom>
                  Groups
                </Typography>

                {/* Group List */}
                <Paper variant="outlined" sx={{ maxHeight: 300, overflow: 'auto' }}>
                  {groupLoading ? (
                    <Box display="flex" justifyContent="center" mt={4}>
                      <CircularProgress />
                    </Box>
                  ) : (
                    <List>
                      {groups.map((group) => (
                        <React.Fragment key={group.id}>
                          <ListItem>
                            <ListItemText
                              primary={group.name}
                            />
                            <ListItemSecondaryAction>
                              <Button size="small" variant="outlined" onClick={() => handleEditGroup(group)}>
                                Manage
                              </Button>
                              <Button size="small" variant="outlined" onClick={() => handleViewMembers(group)}>
                                Members
                              </Button>
                              <Button size="small" variant="outlined">
                                Leave
                              </Button>
                            </ListItemSecondaryAction>
                          </ListItem>
                          <Divider />
                        </React.Fragment>
                      ))}
                      {groups.length === 0 && (
                        <ListItem>
                          <ListItemText primary="No groups found" />
                        </ListItem>
                      )}
                    </List>
                  )}
                </Paper>
              </CardContent>
              <CardActions>
                <Button startIcon={<AddIcon />} size="small" onClick={() => handleEditGroup()}>
                  Create New Group
                </Button>
              </CardActions>
            </Card>
          </Grid>

          {/* Feature 3: View Invites */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h5" component="div" gutterBottom>
                  Pending Invitations
                </Typography>

                <Paper variant="outlined" sx={{ maxHeight: 300, overflow: 'auto' }}>
                  <List>
                    {invites.map((invite) => (
                      <React.Fragment key={invite.id}>
                        <ListItem>
                          <ListItemText
                            primary={`Join ${invite.groupName}`}
                            secondary={`From: ${invite.from}`}
                          />
                          <ListItemSecondaryAction>
                            <IconButton color="success" edge="end" aria-label="accept" sx={{ mr: 1 }}>
                              <CheckIcon />
                            </IconButton>
                            <IconButton color="error" edge="end" aria-label="decline">
                              <CloseIcon />
                            </IconButton>
                          </ListItemSecondaryAction>
                        </ListItem>
                        <Divider />
                      </React.Fragment>
                    ))}
                    {invites.length === 0 && (
                      <ListItem>
                        <ListItemText primary="No pending invitations" />
                      </ListItem>
                    )}
                  </List>
                </Paper>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </>
  )
} 