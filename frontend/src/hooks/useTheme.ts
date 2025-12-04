import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type Theme = 'light' | 'dark' | 'system';

interface ThemeState {
  theme: Theme;
  actualTheme: 'light' | 'dark';
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

const getSystemTheme = (): 'light' | 'dark' => {
  if (typeof window === 'undefined') return 'dark';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

const resolveTheme = (theme: Theme): 'light' | 'dark' => {
  if (theme === 'system') {
    return getSystemTheme();
  }
  return theme;
};

const applyTheme = (actualTheme: 'light' | 'dark') => {
  const root = window.document.documentElement;
  root.classList.remove('light', 'dark');
  root.classList.add(actualTheme);
  
  // Atualiza meta theme-color
  const metaThemeColor = document.querySelector('meta[name="theme-color"]');
  if (metaThemeColor) {
    metaThemeColor.setAttribute('content', actualTheme === 'dark' ? '#0f172a' : '#ffffff');
  }
};

export const useTheme = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: 'system',
      actualTheme: getSystemTheme(),
      
      setTheme: (theme: Theme) => {
        const actualTheme = resolveTheme(theme);
        applyTheme(actualTheme);
        set({ theme, actualTheme });
      },
      
      toggleTheme: () => {
        const { actualTheme } = get();
        const newTheme = actualTheme === 'dark' ? 'light' : 'dark';
        applyTheme(newTheme);
        set({ theme: newTheme, actualTheme: newTheme });
      },
    }),
    {
      name: 'theme-storage',
      onRehydrateStorage: () => (state) => {
        if (state) {
          const actualTheme = resolveTheme(state.theme);
          applyTheme(actualTheme);
          state.actualTheme = actualTheme;
        }
      },
    }
  )
);

// Listen for system theme changes
if (typeof window !== 'undefined') {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    const { theme } = useTheme.getState();
    if (theme === 'system') {
      const newActualTheme = e.matches ? 'dark' : 'light';
      applyTheme(newActualTheme);
      useTheme.setState({ actualTheme: newActualTheme });
    }
  });
}
