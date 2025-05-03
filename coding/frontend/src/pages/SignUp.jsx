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
        
    const isValidPassword = (password) => {
        const hasLength = password.length >= 8 && password.length <= 32;
        const hasUppercase = /[A-Z]/.test(password);
        const hasLowercase = /[a-z]/.test(password);
        const hasNumber = /[0-9]/.test(password);
        const hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);
        
        return hasLength && hasUppercase && hasLowercase && hasNumber && hasSpecialChar;
    };

    const handleSubmit = async () => {
        setNetworkError('');
        setEmailError('');
        setPasswordError('');
        setLicenseError('');

        if (!isValidEmail(email)) {
            setEmailError('Please enter a valid email.');
            return;
        }

        if (!isValidPassword(password)) {
            setPasswordError('Password must be between 8-32 characters and contain an uppercase letter, a lowercase letter, a number, and a special character.');
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
            } else if (response.status === 401) {
                setLicenseError(response.data.msg || 'Invalid software license.');
            } else {
                setNetworkError(response.data.msg || 'Signup failed. Please try again.');
            }
        } catch (err) {
            console.error(err);
            if (err.response) {
                if (err.response.status === 401) {
                    setLicenseError(err.response.data.msg || 'Invalid software license.');
                } else {
                    setNetworkError(err.response.data.msg || 'Signup failed. Please try again.');
                }
            } else {
                setNetworkError('Network error. Please try again.');
            }
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
                        helperText={passwordError || 'Must be 8-32 characters with uppercase, lowercase, number, and special character'}
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
