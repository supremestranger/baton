// src/components/Tasks/TaskDetail.jsx
import React, { useState, useEffect } from 'react';

const TaskDetail = ({ onNavigate }) => {
  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);

  // В реальном приложении taskId будет передаваться как параметр
  const taskId = 'example-task-id';

  useEffect(() => {
    fetchTask();
  }, []);

  const fetchTask = async () => {
    try {
      const credentials = localStorage.getItem('baton_credentials');
      const response = await fetch(`http://localhost:8080/api/task/${taskId}`, {
        headers: {
          'Authorization': `Basic ${credentials}`,
        },
      });
      
      if (response.ok) {
        const taskData = await response.json();
        setTask(taskData);
      }
    } catch (error) {
      console.error('Error fetching task:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Загрузка задачи...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center mb-8">
        <button
          onClick={() => onNavigate('tasks')}
          className="text-gray-400 hover:text-white mr-4"
        >
          ← Назад к списку
        </button>
        <h1 className="text-3xl font-bold text-white">Детали задачи</h1>
      </div>

      <div className="grid gap-6">
        {/* Информация о задаче */}
        <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-gray-700/50">
          <h2 className="text-xl font-semibold text-white mb-4">Информация</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-400">Статус:</span>
              <span className="ml-2 text-green-400">✅ completed</span>
            </div>
            <div>
              <span className="text-gray-400">Создана:</span>
              <span className="ml-2 text-white">2024-01-15 14:30</span>
            </div>
            <div>
              <span className="text-gray-400">Завершена:</span>
              <span className="ml-2 text-white">2024-01-15 14:32</span>
            </div>
            <div>
              <span className="text-gray-400">Строк обработано:</span>
              <span className="ml-2 text-white">6</span>
            </div>
          </div>
        </div>

        {/* Код задачи */}
        <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl border border-gray-700/50">
          <div className="p-4 border-b border-gray-700/50">
            <h2 className="text-lg font-semibold text-cyan-400">📝 Код задачи</h2>
          </div>
          <pre className="p-4 text-gray-100 font-mono text-sm overflow-auto">
            {task?.code || 'def process_data(df):\n    return df'}
          </pre>
        </div>

        {/* Результат */}
        <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl border border-gray-700/50">
          <div className="p-4 border-b border-gray-700/50">
            <h2 className="text-lg font-semibold text-green-400">📊 Результат</h2>
          </div>
          <pre className="p-4 text-green-100 font-mono text-sm overflow-auto">
            A,B,C,D,sum,mean,std
1,2,3,4,10,2.5,1.29
5,6,7,8,26,6.5,1.29
9,10,11,12,42,10.5,1.29
13,14,15,16,58,14.5,1.29
2,4,6,8,20,5.0,2.58
1,3,5,7,16,4.0,2.58
          </pre>
        </div>
      </div>
    </div>
  );
};

export default TaskDetail;