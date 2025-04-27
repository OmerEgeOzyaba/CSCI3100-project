// This file is used when unit testing the frontend
// It is a dummy implementation of axios and mocks its behavior
// In the tests itself you can specify what should happen when certain axios methods are called
// F.e. axiosInstance.post.mockResolvedValue({ data: { token: "token123" } })

import { vi } from 'vitest';

const axiosInstance = {
  post: vi.fn(),
  get: vi.fn(),
  put: vi.fn(),
  interceptors: {
    request: {
      use: vi.fn(),
      eject: vi.fn(),
    },
    response: {
      use: vi.fn(),
      eject: vi.fn(),
    },
  },
};

export default {
  __esModule: true,
  create: vi.fn(() => axiosInstance),
};

export { axiosInstance };
