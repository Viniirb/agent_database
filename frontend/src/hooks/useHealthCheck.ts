import { useState, useEffect } from 'react';

const HEALTH_CHECK_INTERVAL = 300000; // 5 minutos (300000ms)
const BACKEND_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const useHealthCheck = () => {
  const [isOnline, setIsOnline] = useState(false);
  const [isChecking, setIsChecking] = useState(true);

  const checkHealth = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000), // 5 segundos timeout
      });

      if (response.ok) {
        const data = await response.json();
        setIsOnline(data.status === 'healthy');
      } else {
        setIsOnline(false);
      }
    } catch (error) {
      setIsOnline(false);
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    // Check imediato
    checkHealth();

    // Polling a cada 30 segundos
    const interval = setInterval(checkHealth, HEALTH_CHECK_INTERVAL);

    return () => clearInterval(interval);
  }, []);

  return { isOnline, isChecking };
};