import { Component, type ReactNode } from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error) {
    console.error('Error caught by boundary:', error);
  }

  reset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="h-screen flex items-center justify-center bg-background">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center px-4 max-w-md"
          >
            <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-accent-red/10 flex items-center justify-center">
              <AlertCircle size={32} className="text-accent-red" />
            </div>

            <h1 className="text-2xl font-semibold text-foreground mb-2">
              Algo deu errado
            </h1>

            <p className="text-foreground-muted mb-4">
              Ocorreu um erro inesperado. Tente recarregar a página.
            </p>

            {this.state.error && (
              <div className="mb-6 p-3 rounded-lg bg-accent-red/5 border border-accent-red/20">
                <p className="text-xs text-accent-red font-mono break-words">
                  {this.state.error.message}
                </p>
              </div>
            )}

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={this.reset}
              className="inline-flex items-center gap-2 px-6 py-3 bg-accent-blue text-white rounded-lg hover:bg-accent-blue/90 transition-colors font-medium"
            >
              <RefreshCw size={18} />
              Tentar Novamente
            </motion.button>
          </motion.div>
        </div>
      );
    }

    return this.props.children;
  }
}
