import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import '@testing-library/jest-dom'
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { vi } from 'vitest'
import Login from "../src/pages/Login"
import Home from '../src/pages/Home';

vi.mock('axios');
import { axiosInstance } from 'axios';

describe('Logout', () => {
    test('clicks on logout', async () => {
        axiosInstance.get.mockResolvedValue({
            status: 200,
            data: { groups: [] },
        })

        axiosInstance.post.mockResolvedValue({
            status: 200,
            data: {},
        })

        const user = userEvent.setup();

        render(
            <MemoryRouter initialEntries={['/dashboard']}>
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/dashboard" element={<Home />} />
                </Routes>
            </MemoryRouter>
        );

        await user.click(screen.getByRole('button', { name: "Logout" }));

        await waitFor(() => {
            expect(screen.getByLabelText("Email")).toBeInTheDocument();
            expect(screen.getByLabelText("Password")).toBeInTheDocument();
            expect(screen.getByRole('button', { name: "Login" })).toBeInTheDocument();
            expect(screen.getByRole('link', { name: "Sign up" })).toBeInTheDocument();
        });
    });

});
