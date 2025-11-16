// src/components/Tasks/TaskCreate.jsx
import React, { useState } from 'react';

const TaskCreate = ({ onNavigate }) => {
  const [code, setCode] = useState(`# Ваш код для обработки данных
# Входные данные в переменной df (DataFrame)

def process_data(df):
    result = df.copy()
    # Добавляем новые столбцы
    result['sum'] = df.sum(axis=1)
    result['mean'] = df.mean(axis=1)
    result['std'] = df.std(axis=1)
    return result

output_df = process_data(df)`);

  const [inputData, setInputData] = useState(`A,B,C,D
1,2,3,4
5,6,7,8
9,10,11,12
13,14,15,16
2,4,6,8
1,3,5,7`);

  const [isLoading, setIsLoading] = useState(false);

  const getUsernameFromCredentials = () => {
    const credentials = localStorage.getItem('baton_credentials');
    if (!credentials) return null;
    
    try {
      const decoded = atob(credentials);
      return decoded.split(':')[0];
    } catch (error) {
      console.error('Error decoding credentials:', error);
      return null;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const credentials = localStorage.getItem('baton_credentials');
      const username = getUsernameFromCredentials();
      const rowCount = Math.max(0, inputData.split('\n').length - 1);
      
      if (!username) {
        throw new Error('Cannot get username from credentials');
      }

      const response = await fetch('http://localhost:8080/task', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Basic ${credentials}`,
        },
        body: JSON.stringify({
          code: code,
          data: inputData,
          rows: rowCount,
          creator: username  // Добавляем creator в запрос
        }),
      });

      if (response.ok) {
        // Задача создана, переходим к списку
        onNavigate('tasks');
      } else {
        const errorText = await response.text();
        throw new Error(errorText || 'Failed to create task');
      }
    } catch (error) {
      console.error('Error creating task:', error);
      alert(`Ошибка при создании задачи: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="flex items-center mb-8">
        <button
          onClick={() => onNavigate('tasks')}
          className="text-gray-400 hover:text-white mr-4"
        >
          ← Назад
        </button>
        <h1 className="text-3xl font-bold text-white">Новая задача</h1>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-6">
        {/* Редактор кода */}
        <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl border border-gray-700/50">
          <div className="p-4 border-b border-gray-700/50">
            <h2 className="text-lg font-semibold text-cyan-400">📝 Код обработки</h2>
          </div>
          <div className="p-1">
            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              className="w-full h-80 bg-gray-900/80 text-gray-100 font-mono text-sm p-4 rounded-lg border border-gray-600/50 focus:outline-none focus:border-cyan-500/50 resize-none"
              placeholder="Введите Python код..."
            />
          </div>
        </div>

        {/* Входные данные */}
        <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl border border-gray-700/50">
          <div className="p-4 border-b border-gray-700/50">
            <h2 className="text-lg font-semibold text-green-400">📊 Входные данные</h2>
          </div>
          <div className="p-1">
            <textarea
              value={inputData}
              onChange={(e) => setInputData(e.target.value)}
              className="w-full h-80 bg-gray-900/80 text-gray-100 font-mono text-sm p-4 rounded-lg border border-gray-600/50 focus:outline-none focus:border-green-500/50 resize-none"
              placeholder="Введите CSV данные..."
            />
            <div className="px-4 py-2 text-xs text-gray-400">
              Строк: {Math.max(0, inputData.split('\n').length - 1)}
            </div>
          </div>
        </div>
      </div>

      {/* Кнопка отправки */}
      <div className="flex justify-center">
        <button
          onClick={handleSubmit}
          disabled={isLoading || !code.trim() || !inputData.trim()}
          className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white py-4 px-8 rounded-2xl font-semibold hover:from-cyan-600 hover:to-blue-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02] flex items-center justify-center text-lg min-w-64"
        >
          {isLoading ? (
            <>
              <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin mr-3"></div>
              Создание задачи...
            </>
          ) : (
            '🚀 Запустить задачу'
          )}
        </button>
      </div>
    </div>
  );
};

export default TaskCreate;