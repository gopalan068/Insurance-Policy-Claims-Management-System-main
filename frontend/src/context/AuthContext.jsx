import React, { createContext, useContext, useState, useEffect } from 'react';
import authService from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('insurance_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('insurance_token'));
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const verifyAuth = async () => {
      const storedToken = localStorage.getItem('insurance_token');
      if (storedToken) {
        try {
          const userData = await authService.getCurrentUser();
          setUser(userData);
          localStorage.setItem('insurance_user', JSON.stringify(userData));
        } catch (error) {
          console.error('Session validation failed:', error);
          logout();
        }
      }
      setIsLoading(false);
    };

    verifyAuth();
  }, []);

  const login = async (email, password) => {
    const data = await authService.login(email, password);
    const userObj = data.user;
    const tokenStr = data.access_token;

    localStorage.setItem('insurance_token', tokenStr);
    localStorage.setItem('insurance_user', JSON.stringify(userObj));

    setToken(tokenStr);
    setUser(userObj);
    return userObj;
  };

  const register = async (userData) => {
    const data = await authService.register(userData);
    const userObj = data.user;
    const tokenStr = data.access_token;

    localStorage.setItem('insurance_token', tokenStr);
    localStorage.setItem('insurance_user', JSON.stringify(userObj));

    setToken(tokenStr);
    setUser(userObj);
    return userObj;
  };

  const logout = () => {
    authService.logout();
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isAdmin: !!user && user.role === 'ADMIN',
        isCustomer: !!user && user.role === 'CUSTOMER',
        isOfficer: !!user && user.role === 'CLAIMS_OFFICER',
        isAgent: !!user && user.role === 'AGENT',
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
