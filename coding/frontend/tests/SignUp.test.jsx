import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import '@testing-library/jest-dom'
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { vi } from 'vitest'
import Login from "../src/pages/Login"
import SignUp from '../src/pages/SignUp';

vi.mock('axios');
import { axiosInstance } from 'axios';

describe('SignUp', () => {
    test('renders the signup form fields', () => {

        render(
            <MemoryRouter>
                <SignUp />
            </MemoryRouter>
        );

        expect(screen.getByLabelText("Email")).toBeInTheDocument();
        expect(screen.getByLabelText("Password")).toBeInTheDocument();
        expect(screen.getByLabelText("License Key")).toBeInTheDocument();
        expect(screen.getByRole('button', { name: "Cancel" })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: "Create Account" })).toBeInTheDocument();
    });

    test('submits new user', async () => {
        axiosInstance.post.mockResolvedValue({
            status: 201,
            data: {},
        })

        const user = userEvent.setup();

        render(
            <MemoryRouter initialEntries={['/signup']}>
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/signup" element={<SignUp />} />
                </Routes>
            </MemoryRouter>
        );

        await user.type(screen.getByLabelText("Email"), 'user@example.com');
        await user.type(screen.getByLabelText("Password"), 'pass1234');
        await user.type(screen.getByLabelText("License Key"), '12341234');
        await user.click(screen.getByRole('button', { name: "Create Account" }));

        await waitFor(() => {

            expect(axiosInstance.post).toHaveBeenCalledWith('/api/auth/signup', {
                email: 'user@example.com',
                password: 'pass1234',
                licenseKey: '12341234'
            });

            expect(screen.queryByRole('Alert')).not.toBeInTheDocument();
            expect(screen.queryByLabelText("License Key")).not.toBeInTheDocument();

            expect(screen.getByRole('link', { name: "Sign up" })).toBeInTheDocument();
            
        });
    });
});
