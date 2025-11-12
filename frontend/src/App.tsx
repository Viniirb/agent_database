import { AppLayout } from './components/layout/AppLayout';
import { ChatContainer } from './components/chat/ChatContainer';
import { ToastContainer } from './components/ui/Toast';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ChatProvider, useActiveConversation } from './contexts/ChatContext';
import { generateId } from './utils/uuid';

function AppContent() {
  const { setActiveConversationId } = useActiveConversation();

  const handleNewChat = () => {
    const newConversationId = generateId();
    setActiveConversationId(newConversationId);
  };

  return (
    <div className="h-screen text-foreground">
      <AppLayout onNewChat={handleNewChat}>
        <ChatContainer />
      </AppLayout>
      <ToastContainer />
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <ChatProvider>
        <AppContent />
      </ChatProvider>
    </ErrorBoundary>
  );
}

export default App;