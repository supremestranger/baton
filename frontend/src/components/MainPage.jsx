import React, { useState } from 'react';

const BatonPlatform = () => {
  const [code, setCode] = useState(`# Ваш код для обработки данных
# Входные данные в переменной df (DataFrame)

# Пример: вычисление статистик
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

  const [outputData, setOutputData] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);
    setOutputData('');
    
    // Имитация обработки данных
    setTimeout(() => {
      setIsLoading(false);
      // Генерируем пример результата
      setOutputData(`A,B,C,D,sum,mean,std
1,2,3,4,10,2.5,1.29
5,6,7,8,26,6.5,1.29
9,10,11,12,42,10.5,1.29
13,14,15,16,58,14.5,1.29
2,4,6,8,20,5.0,2.58
1,3,5,7,16,4.0,2.58`);
    }, 2000);
  };

  const handleRunExample = () => {
    setCode(`# Кластеризация K-means
from sklearn.cluster import KMeans
import numpy as np

def process_data(df):
    # Преобразуем данные для кластеризации
    data = df.values
    kmeans = KMeans(n_clusters=2, random_state=42)
    clusters = kmeans.fit_predict(data)
    
    # Добавляем кластеры к результату
    result = df.copy()
    result['cluster'] = clusters
    result['distance_to_center'] = np.min(kmeans.transform(data), axis=1)
    return result

output_df = process_data(df)`);
    
    setInputData(`feature1,feature2,feature3
1.2,2.3,0.8
2.1,1.8,1.2
5.6,6.1,5.9
6.2,5.8,6.3
10.1,11.2,9.8
11.3,10.7,11.1
1.5,2.1,1.1
5.9,6.3,6.0`);
  };

  const handleGenerateSampleData = () => {
    setInputData(`price,volume,rating,sales
100,50,4.5,200
150,30,4.2,150
200,25,4.7,180
80,60,4.1,220
120,45,4.6,190
90,55,4.3,210
180,35,4.8,170`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Заголовок */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent animate-pulse">
            Baton
          </h1>
        </div>

        {/* Верхняя часть - код и данные */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-6">
          {/* Левая колонка - редактор кода */}
          <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl border border-gray-700/50 shadow-2xl">
            <div className="flex justify-between items-center p-4 border-b border-gray-700/50">
              <h2 className="text-lg font-semibold text-cyan-400">
                <span className="text-xl">📝</span> Код обработки (Python)
              </h2>
              <button
                onClick={handleRunExample}
                className="px-4 py-2 bg-cyan-500/20 text-cyan-400 rounded-xl border border-cyan-500/30 hover:bg-cyan-500/30 transition-all duration-300 text-sm"
              >
                Пример алгоритма
              </button>
            </div>
            <div className="p-1">
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className="w-full h-80 bg-gray-900/80 text-gray-100 font-mono text-sm p-4 rounded-lg border border-gray-600/50 focus:outline-none focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 transition-all duration-300 resize-none"
                spellCheck="false"
                placeholder="# Введите ваш Python код для обработки данных..."
              />
            </div>
          </div>

          {/* Правая колонка - входные данные */}
          <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl border border-gray-700/50 shadow-2xl">
            <div className="flex justify-between items-center p-4 border-b border-gray-700/50">
              <h2 className="text-lg font-semibold text-green-400">
                <span className="text-xl">📊</span> Входные данные (CSV)
              </h2>
              <button
                onClick={handleGenerateSampleData}
                className="px-4 py-2 bg-green-500/20 text-green-400 rounded-xl border border-green-500/30 hover:bg-green-500/30 transition-all duration-300 text-sm"
              >
                Пример данных
              </button>
            </div>
            <div className="p-1">
              <textarea
                value={inputData}
                onChange={(e) => setInputData(e.target.value)}
                className="w-full h-80 bg-gray-900/80 text-gray-100 font-mono text-sm p-4 rounded-lg border border-gray-600/50 focus:outline-none focus:border-green-500/50 focus:ring-2 focus:ring-green-500/20 transition-all duration-300 resize-none"
                spellCheck="false"
                placeholder="Введите CSV данные..."
              />
            </div>
          </div>
        </div>

        {/* Кнопка отправки */}
        <div className="flex justify-center mb-6">
          <button
            onClick={handleSubmit}
            disabled={isLoading || !code.trim() || !inputData.trim()}
            className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white py-4 px-8 rounded-2xl font-semibold hover:from-cyan-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:ring-offset-2 focus:ring-offset-gray-900 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02] flex items-center justify-center text-lg min-w-64"
          >
            {isLoading ? (
              <>
                <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin mr-3"></div>
                Обработка на воркерах...
              </>
            ) : (
              <>
                <svg className="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Отправить код на выполнение
              </>
            )}
          </button>
        </div>

        {/* Нижняя часть - результаты */}
        <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl border border-gray-700/50 shadow-2xl">
          <div className="flex justify-between items-center p-4 border-b border-gray-700/50">
            <h2 className="text-lg font-semibold text-yellow-400">
              <span className="text-xl">🎯</span> Результаты обработки (CSV)
            </h2>
            <div className="text-sm text-gray-400">
              {isLoading ? 'Обработка...' : outputData ? 'Готово' : 'Ожидание данных'}
            </div>
          </div>
          <div className="p-1">
            <textarea
              value={outputData}
              readOnly
              className="w-full h-64 bg-gray-900/80 text-yellow-100 font-mono text-sm p-4 rounded-lg border border-gray-600/50 focus:outline-none resize-none"
              placeholder="Здесь появятся результаты обработки..."
            />
          </div>
        </div>

        {/* Статистика */}
        <div className="grid grid-cols-4 gap-4 mt-6">
          <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl p-4 border border-cyan-500/20 text-center">
            <div className="text-cyan-400 text-2xl font-bold">12</div>
            <div className="text-gray-400 text-sm">Активных воркеров</div>
          </div>
          <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl p-4 border border-green-500/20 text-center">
            <div className="text-green-400 text-2xl font-bold">2.3s</div>
            <div className="text-gray-400 text-sm">Среднее время</div>
          </div>
          <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl p-4 border border-yellow-500/20 text-center">
            <div className="text-yellow-400 text-2xl font-bold">{inputData.split('\n').length}</div>
            <div className="text-gray-400 text-sm">Строк данных</div>
          </div>
          <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl p-4 border border-purple-500/20 text-center">
            <div className="text-purple-400 text-2xl font-bold">{inputData.split('\n')[0]?.split(',').length || 0}</div>
            <div className="text-gray-400 text-sm">Колонок</div>
          </div>
        </div>
      </div>

      {/* Анимированные элементы фона */}
      <div className="fixed top-0 left-0 w-full h-full -z-10 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>
    </div>
  );
};

export default BatonPlatform;