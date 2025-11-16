// src/App.jsx
import React, { useState, useEffect } from 'react';
import AuthPage from './components/Auth/AuthPage';
import TaskList from './components/Tasks/TaskList';
import TaskCreate from './components/Tasks/TaskCreate';
import TaskDetail from './components/Tasks/TaskDetail';
import Navbar from './components/Layout/Navbar';
import LoadingSpinner from './components/Common/LoadingSpinner';

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState('tasks');

  useEffect(() => {
    const checkAuth = async () => {
      const credentials = localStorage.getItem('baton_credentials');
      
      if (!credentials) {
        setLoading(false);
        return;
      }

      try {
        const response = await fetch('http://localhost:8084/verify', {
          method: 'GET',
          headers: {
            'Authorization': `Basic ${credentials}`,
          },
        });
        
        if (response.ok) {
          setIsAuthenticated(true);
        } else {
          // localStorage.removeItem('baton_credentials');
        }
      } catch (error) {
        console.error('Auth verification failed:', error);
        // localStorage.removeItem('baton_credentials');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const handleLogin = (username, password) => {
    const credentials = btoa(`${username}:${password}`);
    localStorage.setItem('baton_credentials', credentials);
    setIsAuthenticated(true);
    setCurrentPage('tasks');
  };

  const handleLogout = () => {
    localStorage.removeItem('baton_credentials');
    setIsAuthenticated(false);
    setCurrentPage('auth');
  };

  const navigateTo = (page) => {
    setCurrentPage(page);
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!isAuthenticated) {
    return <AuthPage onLogin={handleLogin} />;
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'create':
        return <TaskCreate onNavigate={navigateTo} />;
      case 'task':
        return <TaskDetail onNavigate={navigateTo} />;
      case 'tasks':
      default:
        return <TaskList onNavigate={navigateTo} />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black">
      <Navbar 
        currentPage={currentPage} 
        onNavigate={navigateTo} 
        onLogout={handleLogout} 
      />
      <div className="container mx-auto px-4 py-8">
        {renderPage()}
      </div>
    </div>
  );
};

export default App;