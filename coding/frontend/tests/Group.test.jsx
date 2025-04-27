import { render, screen, waitFor, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import '@testing-library/jest-dom'
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { expect, vi } from 'vitest'
import GroupView from "../src/pages/GroupView"
import MembersView from "../src/pages/MembersView"
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

const test_group_edit = [
    {
        "created_at": "2025-03-01T10:00:00Z",
        "description": "Software development team but now different",
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
        "name": "Project Alpha 2",
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

const test_members_group = {
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
}

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

            expect(axiosInstance.get).toHaveBeenCalledWith('/api/groups/');
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

        const groupList = await screen.findByTestId('group-list');
        const groupItems = within(groupList).getAllByRole('listitem');

        const alphaItem = groupItems.find(item =>
            within(item).queryByText('Project Alpha')
        );
        expect(within(alphaItem).getByRole('button', { name: "Leave" })).toBeInTheDocument();

        const marketingItem = groupItems.find(item =>
            within(item).queryByText('Marketing Team')
        );
        expect(within(marketingItem).getByRole('button', { name: "Leave" })).toBeInTheDocument();

        await user.click(within(marketingItem).getByRole('button', { name: "Leave" }));

        expect(axiosInstance.post).toHaveBeenCalledWith('/api/groups/2/leave');

        await waitFor(() => {
            expect(within(groupList).queryByText('Marketing Team')).not.toBeInTheDocument();
        });

        expect(within(groupList).getByText('Project Alpha')).toBeInTheDocument();

    });

    test('views members', async () => {
        axiosInstance.get.mockImplementation((url) => {
            if (url === '/api/groups/') {
                return Promise.resolve({
                    status: 200,
                    data: { groups: test_groups }
                });
            } else {
                return Promise.resolve({
                    status: 200,
                    data: { group: test_members_group }
                });
            }
        });

        const user = userEvent.setup();

        render(
            <MemoryRouter initialEntries={['/dashboard']}>
                <Routes>
                    <Route path="/dashboard" element={<Home />} />
                    <Route path="/members-view" element={<MembersView />} />
                </Routes>
            </MemoryRouter>
        );

        const groupList = await screen.findByTestId('group-list');
        const groupItems = within(groupList).getAllByRole('listitem');

        const alphaItem = groupItems.find(item =>
            within(item).queryByText('Project Alpha')
        );
        expect(within(alphaItem).getByRole('button', { name: "Members" })).toBeInTheDocument();

        await user.click(within(alphaItem).getByRole('button', { name: "Members" }));

        expect(axiosInstance.get).toHaveBeenCalledWith('/api/groups/1');

        await waitFor(() => {
            expect(screen.queryByTestId('group-list')).not.toBeInTheDocument();
        });

        expect(await screen.findByText('Project Alpha Members:')).toBeInTheDocument();

        const membersList = await screen.findByTestId('members-list');
        const memberItems = within(membersList).getAllByRole('listitem');

        expect(memberItems).toHaveLength(3);
        const adminItem = memberItems.find(item =>
            within(item).queryByText('Role: admin')
        );
        expect(adminItem).not.toBeNull();

        expect(screen.getByRole('button', { name: "OK" })).toBeInTheDocument();

    });

    test('creates a new group', async () => {
        axiosInstance.get.mockResolvedValueOnce({
            status: 200,
            data: { groups: test_groups_only_alpha }
        })
        axiosInstance.get.mockResolvedValueOnce({
            status: 200,
            data: { groups: test_groups }
        })
        axiosInstance.post.mockResolvedValue({
            status: 201,
            data: { group: test_groups_only_alpha }
        })

        const user = userEvent.setup();

        render(
            <MemoryRouter initialEntries={['/dashboard']}>
                <Routes>
                    <Route path="/dashboard" element={<Home />} />
                    <Route path="/group-edit" element={<GroupView />} />
                </Routes>
            </MemoryRouter>
        );

        const groupListBegin = await screen.findByTestId('group-list');
        const groupItemsBegin = within(groupListBegin).getAllByRole('listitem');

        const alphaItemBegin = groupItemsBegin.find(item =>
            within(item).queryByText('Project Alpha')
        );
        expect(alphaItemBegin).not.toBeNull();

        const marketingItemBegin = groupItemsBegin.find(item =>
            within(item).queryByText('Marketing Team')
        );
        expect(marketingItemBegin).toBeUndefined();

        await user.click(screen.getByRole('button', { name: "Create New Group" }));

        expect(screen.getByText('Create Group')).toBeInTheDocument();
        expect(screen.getByLabelText("Group Name *")).toBeInTheDocument();
        expect(screen.getByLabelText("Description")).toBeInTheDocument();
        expect(screen.getByRole('button', { name: "OK" })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: "Cancel" })).toBeInTheDocument();

        await user.type(screen.getByLabelText("Group Name *"), 'Marketing Team');
        await user.type(screen.getByLabelText("Description"), 'Product marketing');
        await user.click(screen.getByRole('button', { name: "OK" }));

        expect(axiosInstance.post).toHaveBeenCalledWith('/api/groups/', {
            name: 'Marketing Team',
            description: 'Product marketing',
        });

        const groupList = await screen.findByTestId('group-list');
        const groupItems = within(groupList).getAllByRole('listitem');

        const alphaItem = groupItems.find(item =>
            within(item).queryByText('Project Alpha')
        );
        expect(alphaItem).not.toBeNull();

        const marketingItem = groupItems.find(item =>
            within(item).queryByText('Marketing Team')
        );
        expect(marketingItem).not.toBeNull();

    });

    test('edits a group', async () => {
        axiosInstance.get.mockResolvedValueOnce({
            status: 200,
            data: { groups: test_groups }
        })
        axiosInstance.get.mockResolvedValueOnce({
            status: 200,
            data: { groups: test_group_edit }
        })
        axiosInstance.put.mockResolvedValue({
            status: 200,
            data: { group: test_groups_only_alpha }
        })

        const user = userEvent.setup();

        render(
            <MemoryRouter initialEntries={['/dashboard']}>
                <Routes>
                    <Route path="/dashboard" element={<Home />} />
                    <Route path="/group-edit" element={<GroupView />} />
                </Routes>
            </MemoryRouter>
        );

        const groupListBegin = await screen.findByTestId('group-list');
        const groupItemsBegin = within(groupListBegin).getAllByRole('listitem');

        const alphaItemBegin = groupItemsBegin.find(item =>
            within(item).queryByText('Project Alpha')
        );
        expect(alphaItemBegin).not.toBeNull();

        await user.click(within(alphaItemBegin).getByRole('button', { name: "Manage" }));

        expect(screen.getByText('Edit Group')).toBeInTheDocument();
        expect(screen.getByLabelText("Group Name *")).toHaveValue("Project Alpha");
        expect(screen.getByLabelText("Description")).toHaveValue("Software development team");
        expect(screen.getByRole('button', { name: "OK" })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: "Cancel" })).toBeInTheDocument();

        await user.type(screen.getByLabelText("Group Name *"), ' 2');
        await user.type(screen.getByLabelText("Description"), ' but now different');
        await user.click(screen.getByRole('button', { name: "OK" }));

        expect(axiosInstance.put).toHaveBeenCalledWith('/api/groups/1', {
            name: 'Project Alpha 2',
            description: 'Software development team but now different',
        });

        const groupList = await screen.findByTestId('group-list');
        const groupItems = within(groupList).getAllByRole('listitem');

        const alphaItem = groupItems.find(item =>
            within(item).queryByText('Project Alpha')
        );
        expect(alphaItem).toBeUndefined();

        const alphaItem2 = groupItems.find(item =>
            within(item).queryByText('Project Alpha 2')
        );
        expect(alphaItem2).not.toBeNull();

    });

});
