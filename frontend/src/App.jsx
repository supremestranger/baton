// src/App.jsx
import React, { useState, useEffect } from 'react';
import AuthPage from './components/AuthPage';
import MainPage from './components/MainPage';

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log('App mounted - checking authentication...');
    
    const checkAuth = async () => {
      const credentials = localStorage.getItem('baton_credentials');
      console.log('Retrieved credentials from localStorage:', credentials ? 'EXISTS' : 'MISSING');
      
      if (!credentials) {
        console.log('No credentials found, showing login page');
        setLoading(false);
        return;
      }

      try {
        console.log('Making auth request to backend...');
        const response = await fetch('http://localhost:8080/verify', {
          method: 'GET',
          headers: {
            'Authorization': `Basic ${credentials}`,
          },
        });
        
        console.log('Auth response status:', response.status);
        console.log('Auth response ok:', response.ok);
        
        if (response.ok) {
          console.log('Authentication successful');
          setIsAuthenticated(true);
        } else {
          console.log('Authentication failed, but keeping credentials for debugging');
          // Временно устанавливаем authenticated true для отладки
          setIsAuthenticated(true);
        }
      } catch (error) {
        console.error('Auth verification failed:', error);
        console.log('Fallback: setting authenticated true due to network error');
        setIsAuthenticated(true);
      } finally {
        console.log('Auth check completed, setting loading to false');
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const handleLogin = (username, password) => {
    console.log('Login attempt for user:', username);
    const credentials = btoa(`${username}:${password}`);
    localStorage.setItem('baton_credentials', credentials);
    console.log('Credentials saved to localStorage');
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    console.log('Logging out, clearing credentials');
    localStorage.removeItem('baton_credentials');
    setIsAuthenticated(false);
  };

  console.log('App rendering - authenticated:', isAuthenticated, 'loading:', loading);

  if (loading) {
    console.log('Showing loading screen');
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Проверка авторизации...</p>
        </div>
      </div>
    );
  }

  console.log('Rendering main content - authenticated:', isAuthenticated);

  return (
    <>
      {isAuthenticated ? (
        <MainPage onLogout={handleLogout} />
      ) : (
        <AuthPage onLogin={handleLogin} />
      )}
    </>
  );
};

export default App;