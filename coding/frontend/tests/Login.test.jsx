import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import '@testing-library/jest-dom'
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { vi } from 'vitest'
import Login from "../src/pages/Login"
import Home from '../src/pages/Home';

vi.mock('axios');
import { axiosInstance } from 'axios';

describe('Login', () => {
    test('renders the login form fields', () => {

        render(
            <MemoryRouter>
                <Login />
            </MemoryRouter>
        );

        expect(screen.getByLabelText("Email")).toBeInTheDocument();
        expect(screen.getByLabelText("Password")).toBeInTheDocument();
        expect(screen.getByRole('button', { name: "Login" })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: "Sign up" })).toBeInTheDocument();
    });

    test('submits email and password', async () => {
        axiosInstance.post.mockResolvedValue({
            status: 200,
            data: { access_token: 'token123' },
        })

        const user = userEvent.setup();

        render(
            <MemoryRouter initialEntries={['/login']}>
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/dashboard" element={<Home />} />
                </Routes>
            </MemoryRouter>
        );

        await user.type(screen.getByLabelText("Email"), 'user@example.com');
        await user.type(screen.getByLabelText("Password"), 'pass123');
        await user.click(screen.getByRole('button', { name: "Login" }));

        await waitFor(() => {

            expect(axiosInstance.post).toHaveBeenCalledWith('/api/auth/login', {
                email: 'user@example.com',
                password: 'pass123',
            });

            expect(screen.queryByRole('Alert')).not.toBeInTheDocument();
            expect(screen.queryByLabelText ("Password")).not.toBeInTheDocument();

            expect(screen.getByRole('heading', {name: /Welcome to CULater Dashboard/i,})).toBeInTheDocument();
            
        });
    });
});
