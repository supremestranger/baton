// src/components/Tasks/TaskList.jsx
import React, { useState, useEffect, useCallback } from 'react';

const TaskList = ({ onNavigate }) => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  const getUsernameFromCredentials = useCallback(() => {
    const credentials = localStorage.getItem('baton_credentials');
    if (!credentials) return null;
    
    try {
      const decoded = atob(credentials);
      return decoded.split(':')[0];
    } catch (error) {
      console.error('Error decoding credentials:', error);
      return null;
    }
  }, []);

  const fetchTasks = useCallback(async () => {
    try {
      const credentials = localStorage.getItem('baton_credentials');
      const username = getUsernameFromCredentials();
      
      if (!username) {
        console.error('Cannot get username from credentials');
        setLoading(false);
        return;
      }

      const response = await fetch(`http://localhost:8080/tasks/${encodeURIComponent(username)}`, {
        headers: {
          'Authorization': `Basic ${credentials}`,
        },
      });
      
      if (response.ok) {
        const tasksData = await response.json();
        
        const tasksArray = Object.entries(tasksData).map(([taskId, status]) => ({
          task_id: taskId,
          status: status,
          created_at: new Date().toISOString(),
          code: "Код задачи..."
        }));
        
        setTasks(tasksArray);
      } else {
        console.error('Failed to fetch tasks:', response.status);
      }
    } catch (error) {
      console.error('Error fetching tasks:', error);
    } finally {
      setLoading(false);
    }
  }, [getUsernameFromCredentials]);

  // Первоначальная загрузка
  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // Поллинг каждые 5 секунд
  useEffect(() => {
    const intervalId = setInterval(() => {
      console.log('🔄 Поллинг списка задач...');
      fetchTasks();
    }, 5000);

    // Очистка интервала при размонтировании
    return () => clearInterval(intervalId);
  }, [fetchTasks]);

  const getStatusInfo = (status) => {
    const statusConfig = {
      done: {
        color: 'text-green-400',
        bg: 'bg-green-500/20', 
        border: 'border-green-500/30',
        text: '✅ ГОТОВО',
        icon: '✅'
      },
      running: {
        color: 'text-yellow-400',
        bg: 'bg-yellow-500/20',
        border: 'border-yellow-500/30', 
        text: '🔄 В РАБОТЕ',
        icon: '🔄'
      },
      failed: {
        color: 'text-red-400',
        bg: 'bg-red-500/20',
        border: 'border-red-500/30',
        text: '❌ НЕ УДАЛОСЬ',
        icon: '❌'
      },
      unknown: {
        color: 'text-gray-400',
        bg: 'bg-gray-500/20',
        border: 'border-gray-500/30',
        text: '❓ НЕИЗВЕСТНО',
        icon: '❓'
      }
    };

    return statusConfig[status] || statusConfig.unknown;
  };

  // Показываем индикатор обновления если есть задачи в работе
  const hasRunningTasks = tasks.some(task => task.status === 'running');

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Загрузка задач...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center space-x-4">
          <h1 className="text-3xl font-bold text-white">Мои задачи</h1>
          {hasRunningTasks && (
            <div className="flex items-center space-x-2 text-yellow-400">
              <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
              <span className="text-sm">Автообновление</span>
            </div>
          )}
        </div>
        <button
          onClick={() => onNavigate('create')}
          className="bg-gradient-to-r from-green-500 to-cyan-600 text-white px-6 py-3 rounded-2xl font-semibold hover:from-green-600 hover:to-cyan-700 transition-all duration-300"
        >
          ➕ Новая задача
        </button>
      </div>

      <div className="grid gap-4">
        {tasks.length === 0 ? (
          <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-8 text-center border border-gray-700/50">
            <div className="text-6xl mb-4">📋</div>
            <h3 className="text-xl text-white mb-2">Задач пока нет</h3>
            <p className="text-gray-400 mb-4">Создайте первую задачу для обработки данных</p>
            <button
              onClick={() => onNavigate('create')}
              className="bg-gradient-to-r from-green-500 to-cyan-600 text-white px-6 py-2 rounded-xl font-semibold hover:from-green-600 hover:to-cyan-700 transition-all duration-300"
            >
              Создать задачу
            </button>
          </div>
        ) : (
          <>
            {tasks.map((task) => {
              const statusInfo = getStatusInfo(task.status);
              
              return (
                <div
                  key={task.task_id}
                  className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-gray-700/50 hover:border-cyan-500/30 transition-all duration-300 cursor-pointer"
                  onClick={() => onNavigate('task', task.task_id)}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusInfo.bg} ${statusInfo.border} ${statusInfo.color}`}>
                          {statusInfo.text}
                        </span>
                        <span className="text-sm text-gray-400">
                          {task.created_at ? new Date(task.created_at).toLocaleString() : 'Неизвестно'}
                        </span>
                        {task.status === 'running' && (
                          <div className="flex items-center space-x-1 text-yellow-400">
                            <div className="w-1.5 h-1.5 bg-yellow-400 rounded-full animate-pulse"></div>
                            <span className="text-xs">обновляется...</span>
                          </div>
                        )}
                      </div>
                      <div className="text-white font-mono text-sm">
                        Задача ID: {task.task_id}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-cyan-400 text-lg">→</div>
                      <div className="text-xs text-gray-400 mt-1">
                        ID: {task.task_id}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </>
        )}
      </div>
    </div>
  );
};

export default TaskList;