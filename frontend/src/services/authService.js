import { api } from './api';

export const authService = {
  /**
   * Authenticate a user. Returns the user object on success.
   * Throws an Error with detail message on failure.
   */
  login: (username, password) =>
    api.post('/auth/login', { username, password }),

  /**
   * Register a new user account (pending admin approval).
   */
  register: (username, password) =>
    api.post('/auth/register', { username, password }),
};
