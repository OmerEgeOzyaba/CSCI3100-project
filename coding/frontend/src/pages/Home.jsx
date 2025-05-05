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
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Tooltip
} from '@mui/material'
import {
  Add as AddIcon,
  Search as SearchIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  Notifications as NotificationsIcon,
  Person as PersonIcon,
  Group as GroupIcon,
  Assignment as AssignmentIcon,
  Delete as DeleteIcon,
  Edit as EditIcon
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { getGroups, leaveGroup, logout, getTasks, getInvitations, createTask, updateTask, deleteTask, createGroup, acceptInvitation, declineInvitation } from '../services/api'

export default function Home() {
  const navigate = useNavigate()
  const [userId, setUserId] = useState(null);

  const userEmail = JSON.parse(localStorage.getItem("user"));

  // Check token validity on mount
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (!token || token === 'undefined' || token === undefined) {
      console.log('Invalid token detected in Home, redirecting to login');
      localStorage.removeItem('authToken');
      navigate('/login');
    } else {
      // Get user ID from token
      try {
        const tokenData = JSON.parse(atob(token.split('.')[1]));
        if (tokenData && tokenData.user_id) {
          setUserId(tokenData.user_id);
        }
      } catch (error) {
        console.error('Error parsing token data:', error);
      }
    }
  }, [navigate]);

  const handleEditGroup = (group) => {
    navigate('/group-edit', { state: { group } });
  };

  const handleViewMembers = (group) => {
    navigate('/members-view', { state: { group } });
  };

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

  const fetchTasks = async () => {
    try {
      const response = await getTasks();
      const tasks = response.data.tasks || [];
      setTasks(tasks);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    } finally {
      setTasksLoading(false);
    }
  };

  const fetchInvitations = async () => {
    try {
      const response = await getInvitations();
      const invitations = response.data.invitations || [];
      setInvites(invitations);
    } catch (error) {
      console.error('Error fetching invitations:', error);
    } finally {
      setInvitesLoading(false);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch groups first
        await fetchGroup();
        
        // Add delay before fetching tasks
        await new Promise(resolve => setTimeout(resolve, 500));
        await fetchTasks();
        
        // Add delay before fetching invitations
        await new Promise(resolve => setTimeout(resolve, 500));
        await fetchInvitations();
      } catch (error) {
        console.error('Error in data fetching sequence:', error);
      }
    };
    
    fetchData();
  }, [navigate]);

  const handleLeaveGroup = async (group) => {
    try {
          await leaveGroup(group.id)
          setGroupLoading(true)
          fetchGroup()
        } catch (err) {
          console.error(err)
        }
  };

  const handleRespondToInvitation = async (invitation, accept) => {
    try {
      if (accept) {
        await acceptInvitation(invitation.group_id);
        // After accepting, refresh invitations, groups, and tasks
        setInvitesLoading(true);
        setGroupLoading(true);
        setTasksLoading(true);
        await fetchInvitations();
        await fetchGroup();
        await fetchTasks();
      } else {
        await declineInvitation(invitation.group_id);
        // After declining, just refresh invitations
        setInvitesLoading(true);
        fetchInvitations();
      }
    } catch (error) {
      console.error('Error responding to invitation:', error);
    }
  };

  const handleLogout = async () => {
    try {
          await logout()
          navigate("/login")
        } catch (err) {
          console.error(err)
        }
  };

  // Task creation state
  const [openTaskDialog, setOpenTaskDialog] = useState(false);
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    due_date: '',
    group_id: '',
    assigned_to: []
  });
  const [taskErrors, setTaskErrors] = useState({});
  const [taskCreating, setTaskCreating] = useState(false);

  const handleTaskDialogOpen = () => {
    // Check if user has any groups first
    if (groups.length === 0) {
      // No groups, show alert and redirect to create group
      alert("You need to create a group before creating tasks. Let's create a group first.");
      handleCreateDefaultGroup();
      return;
    }
    
    setOpenTaskDialog(true);
    // Reset form
    setNewTask({
      title: '',
      description: '',
      due_date: '',
      group_id: groups.length > 0 ? groups[0].id : '',
      assigned_to: []
    });
    setTaskErrors({});
  };

  const handleCreateDefaultGroup = async () => {
    try {
      const groupName = prompt("Please enter a name for your new group:");
      if (!groupName) return; // User cancelled
      
      const response = await createGroup(groupName, "");
      if (response.data && response.data.group) {
        // Refresh groups
        setGroupLoading(true);
        fetchGroup();
      }
    } catch (error) {
      console.error('Error creating group:', error);
      alert("Failed to create group. Please try again.");
    }
  };

  const handleTaskDialogClose = () => {
    setOpenTaskDialog(false);
  };

  const handleTaskInputChange = (e) => {
    const { name, value } = e.target;
    setNewTask(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when field is edited
    if (taskErrors[name]) {
      setTaskErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateTaskForm = () => {
    const errors = {};
    
    if (!newTask.title.trim()) {
      errors.title = 'Title is required';
    }
    
    if (!newTask.group_id) {
      errors.group_id = 'Please select a group';
    }
    
    if (!newTask.due_date) {
      errors.due_date = 'Due date is required';
    }
    
    setTaskErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleCreateTask = async () => {
    if (!validateTaskForm()) return;
    
    setTaskCreating(true);
    try {
      // Format the date for ISO format
      const formattedTask = {
        ...newTask,
        due_date: new Date(newTask.due_date).toISOString(),
        assigned_to: userId ? [userId] : []
      };
      
      await createTask(formattedTask);
      setTaskCreating(false);
      handleTaskDialogClose();
      
      // Refresh tasks
      setTasksLoading(true);
      fetchTasks();
    } catch (error) {
      console.error('Error creating task:', error);
      setTaskCreating(false);
    }
  };

  const [groups, setGroups] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [invites, setInvites] = useState([]);
  const [groupLoading, setGroupLoading] = useState(true);
  const [tasksLoading, setTasksLoading] = useState(true);
  const [invitesLoading, setInvitesLoading] = useState(true);

  // Task search functionality
  const [taskSearchTerm, setTaskSearchTerm] = useState('');
  const [selectedGroupFilter, setSelectedGroupFilter] = useState('all');
  
  // Filter tasks by user's groups and search term
  const userGroupIds = groups.map(group => group.id);
  const userTasks = tasks.filter(task => 
    userGroupIds.includes(task.group_id) || 
    (task.assigned_to && task.assigned_to.includes(userId))
  );
  
  const filteredTasks = userTasks.filter(task => 
    task.title.toLowerCase().includes(taskSearchTerm.toLowerCase()) &&
    (selectedGroupFilter === 'all' || task.group_id === selectedGroupFilter)
  );

  const handleGroupFilterChange = (event) => {
    setSelectedGroupFilter(event.target.value);
  };
  
  // Debug logging
  useEffect(() => {
    console.log('Current user ID:', userId);
    console.log('User group IDs:', userGroupIds);
    console.log('Available tasks:', tasks);
    console.log('Filtered tasks for user:', userTasks);
  }, [userId, userGroupIds, tasks, userTasks]);

  const formatDate = (dateString) => {
    if (!dateString) return 'No due date';
    
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString();
    } catch (error) {
      console.error('Invalid date format:', dateString);
      return 'Invalid date';
    }
  };

  // Get today's date in YYYY-MM-DD format for the date input min value
  const getTodayString = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  // Confirmation dialog for deleting tasks
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [taskToDelete, setTaskToDelete] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const handleDeleteTask = (task) => {
    setTaskToDelete(task);
    setDeleteDialogOpen(true);
  };

  const confirmDeleteTask = async () => {
    if (!taskToDelete) return;
    
    setDeleteLoading(true);
    try {
      await deleteTask(taskToDelete.id);
      setDeleteLoading(false);
      setDeleteDialogOpen(false);
      
      // Remove the task from state
      setTasks(prevTasks => prevTasks.filter(task => task.id !== taskToDelete.id));
    } catch (error) {
      console.error('Error deleting task:', error);
      setDeleteLoading(false);
    }
  };

  const cancelDeleteTask = () => {
    setDeleteDialogOpen(false);
    setTaskToDelete(null);
  };

  // Add task editing state
  const [openEditTaskDialog, setOpenEditTaskDialog] = useState(false);
  const [taskToEdit, setTaskToEdit] = useState(null);
  const [editTaskErrors, setEditTaskErrors] = useState({});
  const [taskUpdating, setTaskUpdating] = useState(false);

  const handleEditTask = (task) => {
    setTaskToEdit({
      ...task,
      due_date: task.due_date ? new Date(task.due_date).toISOString().split('T')[0] : ''
    });
    setEditTaskErrors({});
    setOpenEditTaskDialog(true);
  };

  const handleEditTaskDialogClose = () => {
    setOpenEditTaskDialog(false);
    setTaskToEdit(null);
  };

  const handleEditTaskInputChange = (e) => {
    const { name, value } = e.target;
    setTaskToEdit(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when field is edited
    if (editTaskErrors[name]) {
      setEditTaskErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateEditTaskForm = () => {
    const errors = {};
    
    if (!taskToEdit.title.trim()) {
      errors.title = 'Title is required';
    }
    
    if (!taskToEdit.group_id) {
      errors.group_id = 'Please select a group';
    }
    
    if (!taskToEdit.due_date) {
      errors.due_date = 'Due date is required';
    }
    
    setEditTaskErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleUpdateTask = async () => {
    if (!validateEditTaskForm()) return;
    
    setTaskUpdating(true);
    try {
      // Format the date for ISO format
      const formattedTask = {
        ...taskToEdit,
        due_date: new Date(taskToEdit.due_date).toISOString()
      };
      
      await updateTask(taskToEdit.id, formattedTask);
      setTaskUpdating(false);
      handleEditTaskDialogClose();
      
      // Refresh tasks
      setTasksLoading(true);
      fetchTasks();
    } catch (error) {
      console.error('Error updating task:', error);
      setTaskUpdating(false);
    }
  };

  return (
    <>
      {/* App Bar Navigation */}
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {userEmail ? `CULater - ${userEmail}` : "CULater"}
          </Typography>
          <Button color="inherit" startIcon={<PersonIcon />} onClick={() => handleLogout()}>
            Logout
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
                  value={taskSearchTerm}
                  onChange={(e) => setTaskSearchTerm(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <SearchIcon />
                      </InputAdornment>
                    ),
                  }}
                />

                {/* Group Filter - Only show when there are groups */}
                {groups.length > 0 && (
                  <FormControl 
                    fullWidth 
                    variant="outlined" 
                    size="small" 
                    margin="normal"
                  >
                    <InputLabel id="group-filter-label">Filter by Group</InputLabel>
                    <Select
                      labelId="group-filter-label"
                      id="group-filter"
                      value={selectedGroupFilter}
                      onChange={handleGroupFilterChange}
                      label="Filter by Group"
                    >
                      <MenuItem value="all">All Groups</MenuItem>
                      {groups.map((group) => (
                        <MenuItem key={group.id} value={group.id}>
                          {group.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                )}

                {/* Task List */}
                <Paper variant="outlined" sx={{ mt: 2, maxHeight: 300, overflow: 'auto' }}>
                  {tasksLoading ? (
                    <Box display="flex" justifyContent="center" mt={4}>
                      <CircularProgress />
                    </Box>
                  ) : (
                    <List>
                      {filteredTasks.map((task) => {
                        const groupName = groups.find(g => g.id === task.group_id)?.name || `Group #${task.group_id}`;
                        return (
                        <React.Fragment key={task.id}>
                          <ListItem>
                            <ListItemText
                              primary={task.title}
                              secondary={`Group: ${groupName} • Due: ${formatDate(task.due_date)}`}
                            />
                            <ListItemSecondaryAction>
                              <Tooltip title="Edit Task">
                                <IconButton 
                                  edge="end" 
                                  aria-label="edit" 
                                  onClick={() => handleEditTask(task)}
                                  color="primary"
                                  size="small"
                                  sx={{ mr: 1 }}
                                >
                                  <EditIcon />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Delete Task">
                                <IconButton 
                                  edge="end" 
                                  aria-label="delete" 
                                  onClick={() => handleDeleteTask(task)}
                                  color="error"
                                  size="small"
                                >
                                  <DeleteIcon />
                                </IconButton>
                              </Tooltip>
                            </ListItemSecondaryAction>
                          </ListItem>
                          <Divider />
                        </React.Fragment>
                      )})}
                      {filteredTasks.length === 0 && (
                        <ListItem>
                          <ListItemText primary="No tasks found" />
                        </ListItem>
                      )}
                    </List>
                  )}
                </Paper>
              </CardContent>
              <CardActions>
                <Button 
                  startIcon={<AddIcon />} 
                  size="small"
                  onClick={handleTaskDialogOpen}
                >
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
                    <List data-testid="group-list">
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
                              <Button size="small" variant="outlined" onClick={() => handleLeaveGroup(group)}>
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
                  {invitesLoading ? (
                    <Box display="flex" justifyContent="center" mt={4}>
                      <CircularProgress />
                    </Box>
                  ) : (
                    <List>
                      {invites.filter(invite => invite.status === 'sent').map((invite) => (
                        <React.Fragment key={invite.id}>
                          <ListItem>
                            <ListItemText
                              primary={`Join Group: ${invite.group_name}`}
                              secondary={`From: ${invite.inviter_email || 'Unknown'} • Date: ${new Date(invite.invite_date).toLocaleDateString()}`}
                            />
                            <ListItemSecondaryAction>
                              <IconButton 
                                color="success" 
                                edge="end" 
                                aria-label="accept" 
                                sx={{ mr: 1 }}
                                onClick={() => handleRespondToInvitation(invite, true)}
                              >
                                <CheckIcon />
                              </IconButton>
                              <IconButton 
                                color="error" 
                                edge="end" 
                                aria-label="decline"
                                onClick={() => handleRespondToInvitation(invite, false)}
                              >
                                <CloseIcon />
                              </IconButton>
                            </ListItemSecondaryAction>
                          </ListItem>
                          <Divider />
                        </React.Fragment>
                      ))}
                      {invites.filter(invite => invite.status === 'sent').length === 0 && (
                        <ListItem>
                          <ListItemText primary="No pending invitations" />
                        </ListItem>
                      )}
                    </List>
                  )}
                </Paper>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>

      {/* Create Task Dialog */}
      <Dialog 
        open={openTaskDialog} 
        onClose={handleTaskDialogClose} 
        fullWidth 
        maxWidth="sm"
        aria-labelledby="task-dialog-title"
        closeAfterTransition={false}
      >
        <DialogTitle id="task-dialog-title">Create New Task</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="title"
            name="title"
            label="Task Title"
            type="text"
            fullWidth
            variant="outlined"
            value={newTask.title}
            onChange={handleTaskInputChange}
            error={!!taskErrors.title}
            helperText={taskErrors.title}
            sx={{ mb: 2 }}
          />
          
          <TextField
            margin="dense"
            id="description"
            name="description"
            label="Description"
            type="text"
            fullWidth
            variant="outlined"
            multiline
            rows={3}
            value={newTask.description}
            onChange={handleTaskInputChange}
            sx={{ mb: 2 }}
          />
          
          <TextField
            margin="dense"
            id="due_date"
            name="due_date"
            label="Due Date"
            type="date"
            fullWidth
            variant="outlined"
            InputLabelProps={{ shrink: true }}
            value={newTask.due_date}
            onChange={handleTaskInputChange}
            error={!!taskErrors.due_date}
            helperText={taskErrors.due_date}
            inputProps={{ min: getTodayString() }}
            sx={{ mb: 2 }}
          />
          
          <FormControl fullWidth variant="outlined" error={!!taskErrors.group_id} sx={{ mb: 2 }}>
            <InputLabel id="group-select-label">Group</InputLabel>
            <Select
              labelId="group-select-label"
              id="group_id"
              name="group_id"
              value={newTask.group_id}
              onChange={handleTaskInputChange}
              label="Group"
            >
              {groups.map((group) => (
                <MenuItem key={group.id} value={group.id}>
                  {group.name}
                </MenuItem>
              ))}
            </Select>
            {taskErrors.group_id && <FormHelperText>{taskErrors.group_id}</FormHelperText>}
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleTaskDialogClose} disabled={taskCreating}>Cancel</Button>
          <Button 
            onClick={handleCreateTask} 
            variant="contained" 
            color="primary"
            disabled={taskCreating}
            startIcon={taskCreating ? <CircularProgress size={20} /> : null}
          >
            {taskCreating ? 'Creating...' : 'Create Task'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Task Dialog */}
      <Dialog 
        open={openEditTaskDialog} 
        onClose={handleEditTaskDialogClose} 
        fullWidth 
        maxWidth="sm"
        aria-labelledby="edit-task-dialog-title"
        closeAfterTransition={false}
      >
        <DialogTitle id="edit-task-dialog-title">Edit Task</DialogTitle>
        <DialogContent>
          {taskToEdit && (
            <>
              <TextField
                autoFocus
                margin="dense"
                id="title"
                name="title"
                label="Task Title"
                type="text"
                fullWidth
                variant="outlined"
                value={taskToEdit.title}
                onChange={handleEditTaskInputChange}
                error={!!editTaskErrors.title}
                helperText={editTaskErrors.title}
                sx={{ mb: 2 }}
              />
              
              <TextField
                margin="dense"
                id="description"
                name="description"
                label="Description"
                type="text"
                fullWidth
                variant="outlined"
                multiline
                rows={3}
                value={taskToEdit.description || ''}
                onChange={handleEditTaskInputChange}
                sx={{ mb: 2 }}
              />
              
              <TextField
                margin="dense"
                id="due_date"
                name="due_date"
                label="Due Date"
                type="date"
                fullWidth
                variant="outlined"
                InputLabelProps={{ shrink: true }}
                value={taskToEdit.due_date}
                onChange={handleEditTaskInputChange}
                error={!!editTaskErrors.due_date}
                helperText={editTaskErrors.due_date}
                inputProps={{ min: getTodayString() }}
                sx={{ mb: 2 }}
              />
              
              <FormControl fullWidth variant="outlined" error={!!editTaskErrors.group_id} sx={{ mb: 2 }}>
                <InputLabel id="edit-group-select-label">Group</InputLabel>
                <Select
                  labelId="edit-group-select-label"
                  id="group_id"
                  name="group_id"
                  value={taskToEdit.group_id}
                  onChange={handleEditTaskInputChange}
                  label="Group"
                  disabled={true}
                >
                  {groups.map((group) => (
                    <MenuItem key={group.id} value={group.id}>
                      {group.name}
                    </MenuItem>
                  ))}
                </Select>
                {editTaskErrors.group_id && <FormHelperText>{editTaskErrors.group_id}</FormHelperText>}
              </FormControl>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleEditTaskDialogClose} disabled={taskUpdating}>Cancel</Button>
          <Button 
            onClick={handleUpdateTask} 
            variant="contained" 
            color="primary"
            disabled={taskUpdating}
            startIcon={taskUpdating ? <CircularProgress size={20} /> : null}
          >
            {taskUpdating ? 'Updating...' : 'Update Task'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Task Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={cancelDeleteTask}
        aria-labelledby="delete-dialog-title"
        closeAfterTransition={false}
      >
        <DialogTitle id="delete-dialog-title">Delete Task</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the task "{taskToDelete?.title}"?
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={cancelDeleteTask} disabled={deleteLoading}>
            Cancel
          </Button>
          <Button 
            onClick={confirmDeleteTask} 
            color="error" 
            disabled={deleteLoading}
            startIcon={deleteLoading ? <CircularProgress size={20} /> : null}
          >
            {deleteLoading ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  )
} 