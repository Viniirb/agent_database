import { motion } from 'framer-motion';
import { Menu, Moon, Sun } from 'lucide-react';
import { useState, useEffect } from 'react';
import { storageService } from '../../services/storage';

export const Header = () => {
  const [theme, setTheme] = useState<'light' | 'dark'>(
    storageService.getTheme()
  );

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
    <header className="h-14 border-b border-gray-800 flex items-center justify-between px-6 bg-gray-950">
      <div className="flex items-center gap-3">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="lg:hidden p-2 hover:bg-gray-900 rounded-lg"
        >
          <Menu size={18} className="text-gray-300" />
        </motion.button>

        <div className="text-lg font-light text-gray-200 tracking-wide">
          Agent Database
        </div>
      </div>

      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={toggleTheme}
        className="p-2 hover:bg-gray-900 rounded-lg transition-colors"
      >
        {theme === 'dark' ? (
          <Sun size={18} className="text-gray-400" />
        ) : (
          <Moon size={18} className="text-gray-400" />
        )}
      </motion.button>
    </header>
  );
}