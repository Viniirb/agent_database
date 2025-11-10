import { useEffect } from 'react';
import { AppLayout } from './components/layout/AppLayout';
import { ChatContainer } from './components/chat/ChatContainer';
import { ToastContainer } from './components/ui/Toast';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ChatProvider } from './contexts/ChatContext';
import { storageService } from './services/storage';

function App() {
  useEffect(() => {
    const theme = storageService.getTheme();
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, []);

  return (
    <ErrorBoundary>
      <ChatProvider>
        <div className="h-screen bg-background text-foreground">
          <AppLayout>
            <ChatContainer />
          </AppLayout>
          <ToastContainer />
        </div>
      </ChatProvider>
    </ErrorBoundary>
  );
}

export default App;