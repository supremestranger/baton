// src/components/Layout/Navbar.jsx
import React from 'react';

const Navbar = ({ currentPage, onNavigate, onLogout }) => {
  return (
    <nav className="bg-gray-800/50 backdrop-blur-lg border-b border-gray-700/50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Лого и название */}
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              🎯 Baton
            </h1>
          </div>

          {/* Навигация */}
          <div className="flex items-center space-x-4">
            <button
              onClick={() => onNavigate('tasks')}
              className={`px-4 py-2 rounded-xl transition-all duration-300 ${
                currentPage === 'tasks'
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
              }`}
            >
              📋 Мои задачи
            </button>
            <button
              onClick={() => onNavigate('create')}
              className={`px-4 py-2 rounded-xl transition-all duration-300 ${
                currentPage === 'create'
                  ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
              }`}
            >
              ➕ Новая задача
            </button>
            <button
              onClick={onLogout}
              className="px-4 py-2 text-red-400 hover:text-red-300 hover:bg-red-500/20 rounded-xl transition-all duration-300"
            >
              🚪 Выйти
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;