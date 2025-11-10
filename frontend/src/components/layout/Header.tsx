import { motion } from 'framer-motion';
import { 
  Menu, 
  Moon, 
  Sun, 
  Database,
  Activity
} from 'lucide-react';
import { useState, useEffect } from 'react';
import { storageService } from '../../services/storage';

export const Header = () => {
  const [theme, setTheme] = useState<'light' | 'dark'>(
    storageService.getTheme()
  );
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    storageService.setTheme(theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  return (
    <header className="h-16 border-b border-border flex items-center justify-between px-6 bg-background/80 backdrop-blur-md">
      <div className="flex items-center gap-4">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="lg:hidden p-2 hover:bg-background-hover rounded-lg"
        >
          <Menu size={20} />
        </motion.button>

        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-blue to-accent-purple flex items-center justify-center">
            <Database size={18} className="text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-foreground">
              Agent Database
            </h1>
            <p className="text-xs text-foreground-subtle">
              Powered by AI
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <motion.div
          animate={{ opacity: isOnline ? 1 : 0.5 }}
          className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-background-card"
        >
          <motion.div
            animate={{ scale: isOnline ? [1, 1.2, 1] : 1 }}
            transition={{ repeat: Infinity, duration: 2 }}
            className={`w-2 h-2 rounded-full ${
              isOnline ? 'bg-accent-green' : 'bg-accent-red'
            }`}
          />
          <span className="text-xs text-foreground-muted">
            {isOnline ? 'Online' : 'Offline'}
          </span>
        </motion.div>

        <motion.button
          whileHover={{ scale: 1.05, rotate: 10 }}
          whileTap={{ scale: 0.95 }}
          onClick={toggleTheme}
          className="p-2 hover:bg-background-hover rounded-lg transition-colors"
        >
          {theme === 'dark' ? (
            <Sun size={20} className="text-foreground-muted" />
          ) : (
            <Moon size={20} className="text-foreground-muted" />
          )}
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="p-2 hover:bg-background-hover rounded-lg transition-colors"
        >
          <Activity size={20} className="text-foreground-muted" />
        </motion.button>
      </div>
    </header>
  );
}