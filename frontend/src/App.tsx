import { useEffect } from 'react';
import { ChatContainer } from './components/chat/ChatContainer';
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
    <div className="h-screen bg-background text-foreground">
      <ChatContainer />
    </div>
  );
}

export default App;