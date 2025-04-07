import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import '@testing-library/jest-dom'
import { vi } from 'vitest'
import Login from "../src/pages/Login"

vi.mock('axios');
import { axiosInstance } from 'axios';

describe('Login', () => {
    test('renders the login form fields', () => {
        render(<Login />);

        expect(screen.getByLabelText("Username")).toBeInTheDocument();
        expect(screen.getByLabelText("Password")).toBeInTheDocument();
        expect(screen.getByRole('button', { name: "Login" })).toBeInTheDocument();
    });

    test('submits email and password', async () => {
        axiosInstance.post.mockResolvedValue({ data: { token: "token123" } })

        const user = userEvent.setup();

        render(<Login />);

        await user.type(screen.getByLabelText("Username"), 'user@example.com');
        await user.type(screen.getByLabelText("Password"), 'pass123');
        await user.click(screen.getByRole('button', { name: "Login" }));

        expect(axiosInstance.post).toHaveBeenCalledWith('/api/auth/login', {
            email: 'user@example.com',
            password: 'pass123',
        });

        expect(await screen.findByText("Login successful!")).toBeInTheDocument();
    });
});
