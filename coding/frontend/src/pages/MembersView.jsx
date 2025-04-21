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
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { getMembers } from '../services/api'

const MembersPage = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const group = location.state?.group;
  const groupId = group?.id;

  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);

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

  return (
    <Container maxWidth="sm">
      <Box mt={5}>
        <Typography variant="h4" gutterBottom>
          Members:
        </Typography>

        {loading ? (
          <Box display="flex" justifyContent="center" mt={4}>
            <CircularProgress />
          </Box>
        ) : (
          <List>
            {members.map((user, index) => (
              <React.Fragment key={index}>
                <ListItem>
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
    </Container>
  );
};

export default MembersPage;
