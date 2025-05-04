import React, { useState } from 'react';
import { TextField, Button, Container, Typography, Box, Alert } from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';
import { createGroup, updateGroup } from '../services/api'

const GroupFormPage = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const existingGroup = location.state?.group;

  const [id] = useState(existingGroup?.id || null);
  const [name, setName] = useState(existingGroup?.name || '');
  const [description, setDescription] = useState(existingGroup?.description || '');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('')

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const groupData = { id, name, description };

      if (existingGroup?.id) {
        await updateGroup(groupData.id, groupData.name, groupData.description)
      } else {
        await createGroup(groupData.name, groupData.description)
      }

      navigate('/dashboard');
    } catch (err) {
      setError(`Action failed: ${err.response.data.error || 'Unknown error'}`)
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    navigate('/dashboard');
  };

  return (
    <Container maxWidth="sm">
      <Box mt={5}>
        <Typography variant="h4" gutterBottom>
          {existingGroup ? 'Edit Group' : 'Create Group'}
        </Typography>

        {error && <Alert severity="error">{error}</Alert>}

        <Box
          component="form"
          noValidate
          autoComplete="off"
          display="flex"
          flexDirection="column"
          gap={2}
        >
          <TextField
            required
            label="Group Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            margin="normal"
          />
          <TextField
            label="Description"
            multiline
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <Box display="flex" justifyContent="space-between" mt={2}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleSubmit}
              disabled={isSubmitting}
            >
              OK
            </Button>
            <Button
              variant="outlined"
              onClick={handleCancel}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
          </Box>
        </Box>
      </Box>
    </Container>
  );
};

export default GroupFormPage;
