import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import '@testing-library/jest-dom'
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { vi } from 'vitest'
import Login from "../src/pages/Login"
import Home from '../src/pages/Home';
import SignUp from '../src/pages/SignUp'

vi.mock('axios');
import { axiosInstance } from 'axios';

describe('Login', () => {
    const token = "eyJhbGciOiJIUzI1NiJ9.e30.2-w724PWbrMu69daqBElQGCDvL8hJdAKn3ChxHrjxxA"

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

    test('submits working email and password', async () => {          
        axiosInstance.post.mockResolvedValue({
            status: 200,
            data: { access_token: token, user: {email: 'user@example.com'} },
        })

        axiosInstance.get.mockResolvedValue({
            status: 200,
            data: { groups: [], tasks: [], invitations: [] },
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
        await user.type(screen.getByLabelText("Password"), 'Pass1234!');
        await user.click(screen.getByRole('button', { name: "Login" }));

        await waitFor(() => {

            expect(axiosInstance.post).toHaveBeenCalledWith('/api/auth/login', {
                email: 'user@example.com',
                password: 'Pass1234!',
            });

            expect(screen.queryByRole('Alert')).not.toBeInTheDocument();
            expect(screen.queryByLabelText("Password")).not.toBeInTheDocument();

            expect(screen.getByRole('heading', {name: /Welcome to CULater Dashboard/i,})).toBeInTheDocument();
            
        });
    });

    test('submits wrong email and password', async () => {
        axiosInstance.post.mockRejectedValue({
            status: 401,
            data:  {"error": "Bad credentials"},
        })

        const user = userEvent.setup();

        render(
            <MemoryRouter>
                <Login />
            </MemoryRouter>
        );

        await user.type(screen.getByLabelText("Email"), 'user@example.com');
        await user.type(screen.getByLabelText("Password"), 'Pass1234!');
        await user.click(screen.getByRole('button', { name: "Login" }));

        await waitFor(() => {

            expect(axiosInstance.post).toHaveBeenCalledWith('/api/auth/login', {
                email: 'user@example.com',
                password: 'Pass1234!',
            });

            expect(screen.getByRole("alert")).toBeInTheDocument();
            expect(screen.getByLabelText("Password")).toBeInTheDocument();
        });
    });

    test('requests signup', async () => {
        const user = userEvent.setup();

        render(
            <MemoryRouter initialEntries={['/login']}>
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/signup" element={<SignUp />} />
                </Routes>
            </MemoryRouter>
        );

        await user.click(screen.getByRole('link', { name: "Sign up" }));

        await waitFor(() => {
            expect(screen.getByLabelText("Email")).toBeInTheDocument();
            expect(screen.getByLabelText("Password")).toBeInTheDocument();
            expect(screen.getByLabelText("License Key")).toBeInTheDocument();
            expect(screen.getByRole('button', { name: "Cancel" })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: "Create Account" })).toBeInTheDocument();
        });
    });

});
