import React, { useState } from 'react';
import {
    TextField,
    Button,
    Typography,
    Container,
    Box,
    Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { signup } from '../services/api'

export default function SignUp() {
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [licenseKey, setLicenseKey] = useState('');
    const [networkError, setNetworkError] = useState('');
    const [emailError, setEmailError] = useState('');
    const [passwordError, setPasswordError] = useState('');
    const [licenseError, setLicenseError] = useState('');

    const isValidEmail = (email) =>
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

    const handleSubmit = async () => {
        setNetworkError('');
        setEmailError('');
        setPasswordError('');
        setLicenseError('');

        if (!isValidEmail(email)) {
            setEmailError('Please enter a valid email.');
            return;
        }

        if (password.length < 8) {
            setPasswordError('Password must be at least 8 characters long.');
            return;
        }

        if (!licenseKey.trim()) {
            setLicenseError('License key cannot be empty.');
            return;
        }

        try {
            const response = await signup(email, password, licenseKey)

            if (response.status === 201) {
                navigate('/login');
            } else {
                setNetworkError(response.data.msg || 'Signup failed. Please try again.');
            }
        } catch (err) {
            setNetworkError('Network error. Please try again.');
            console.error(err)
        }
    };

    const handleCancel = () => {
        navigate('/login');
    };

    return (
        <Container sx={{
            width: '30vw',
            maxWidth: '30vw',
            overflowWrap: 'break-word',
            wordBreak: 'break-word',
            padding: 4,
            mt: 5,
        }}>
            <Box mt={5}>
                <Typography variant="h5" gutterBottom>
                    Sign Up
                </Typography>
                {networkError && <Alert severity="error">{networkError}</Alert>}
                <Box display="flex" flexDirection="column" gap={2} mt={2}>
                    <TextField
                        label="Email"
                        type="email"
                        fullWidth
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        error={!!emailError}
                        helperText={emailError || ' '}
                    />
                    <TextField
                        label="Password"
                        type="password"
                        fullWidth
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        error={!!passwordError}
                        helperText={passwordError || 'Minimum 8 characters'}
                    />
                    <TextField
                        label="License Key"
                        fullWidth
                        value={licenseKey}
                        onChange={(e) => setLicenseKey(e.target.value)}
                        error={!!licenseError}
                        helperText={licenseError || ' '}
                    />
                    <Box display="flex" justifyContent="space-between" mt={3}>
                        <Button variant="outlined" color="secondary" onClick={handleCancel}>
                            Cancel
                        </Button>
                        <Button variant="contained" color="primary" onClick={handleSubmit}>
                            Create Account
                        </Button>
                    </Box>
                </Box>
            </Box>
        </Container>
    );
}
