import { render, screen, waitFor, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import '@testing-library/jest-dom'
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { vi } from 'vitest'
import GroupView from "../src/pages/GroupView"
import Home from '../src/pages/Home';

vi.mock('axios');
import { axiosInstance } from 'axios';

const test_groups = [
    {
        "created_at": "2025-03-01T10:00:00Z",
        "description": "Software development team",
        "id": 1,
        "members": [
            {
                "email": "test@gmail.com",
                "role": "admin"
            },
            {
                "email": "test@gmail.com",
                "role": "contributor"
            },
            {
                "email": "test@gmail.com",
                "role": "contributor"
            }
        ],
        "name": "Project Alpha",
        "owner_id": 1
    },
    {
        "created_at": "2025-03-05T15:30:00Z",
        "description": "Product marketing",
        "id": 2,
        "members": [
            {
                "email": "test@gmail.com",
                "role": "admin"
            },
            {
                "email": "test@gmail.com",
                "role": "contributor"
            }
        ],
        "name": "Marketing Team",
        "owner_id": 3
    }
]

const test_groups_only_alpha = [
    {
        "created_at": "2025-03-01T10:00:00Z",
        "description": "Software development team",
        "id": 1,
        "members": [
            {
                "email": "test@gmail.com",
                "role": "admin"
            },
            {
                "email": "test@gmail.com",
                "role": "contributor"
            },
            {
                "email": "test@gmail.com",
                "role": "contributor"
            }
        ],
        "name": "Project Alpha",
        "owner_id": 1
    },
]

describe('Group', () => {
    test('renders the group form fields', async () => {
        axiosInstance.get.mockResolvedValue({
            status: 200,
            data: {
                groups: test_groups
            },
        })

        render(
            <MemoryRouter>
                <Home />
            </MemoryRouter>
        );

        await waitFor(() => {

            expect(screen.getByText('Groups')).toBeInTheDocument();

            const groupList = screen.getByTestId('group-list');
            const groupItems = within(groupList).getAllByRole('listitem');

            const alphaItem = groupItems.find(item =>
                within(item).queryByText('Project Alpha')
            );
            expect(within(alphaItem).getByRole('button', { name: "Manage" })).toBeInTheDocument();
            expect(within(alphaItem).getByRole('button', { name: "Members" })).toBeInTheDocument();
            expect(within(alphaItem).getByRole('button', { name: "Leave" })).toBeInTheDocument();

            const marketingItem = groupItems.find(item =>
                within(item).queryByText('Marketing Team')
            );
            expect(within(marketingItem).getByRole('button', { name: "Manage" })).toBeInTheDocument();
            expect(within(marketingItem).getByRole('button', { name: "Members" })).toBeInTheDocument();
            expect(within(marketingItem).getByRole('button', { name: "Leave" })).toBeInTheDocument();

            expect(screen.getByRole('button', { name: "Create New Group" })).toBeInTheDocument();
        });
    });

    test('leaves a group', async () => {
        axiosInstance.get.mockResolvedValueOnce({
            status: 200,
            data: {
                groups: test_groups
            },
        })
        axiosInstance.get.mockResolvedValueOnce({
            status: 200,
            data: {
                groups: test_groups_only_alpha
            },
        })

        axiosInstance.post.mockResolvedValue({
            status: 200,
            data: {}
        })

        const user = userEvent.setup();

        render(
            <MemoryRouter>
                <Home />
            </MemoryRouter>
        );

        await waitFor(() => {

            const groupList = screen.getByTestId('group-list');
            const groupItems = within(groupList).getAllByRole('listitem');

            const alphaItem = groupItems.find(item =>
                within(item).queryByText('Project Alpha')
            );
            expect(within(alphaItem).getByRole('button', { name: "Leave" })).toBeInTheDocument();

            const marketingItem = groupItems.find(item =>
                within(item).queryByText('Marketing Team')
            );
            expect(within(marketingItem).getByRole('button', { name: "Leave" })).toBeInTheDocument();
    
            user.click(within(marketingItem).getByRole('button', { name: "Leave" }));

            expect(within(groupList).getByText('Marketing Team')).toBeInTheDocument();
            expect(within(groupList).getByText('Project Alpha')).toBeInTheDocument();
        });
    });

});
