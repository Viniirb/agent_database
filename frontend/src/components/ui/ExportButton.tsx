import { Download } from 'lucide-react';
import { Button } from './Button';
import { cn } from '@/lib/utils';

interface ExportButtonProps {
  conversationId: string;
  format?: 'json' | 'markdown' | 'txt';
  className?: string;
}

export function ExportButton({ conversationId, format = 'markdown', className }: ExportButtonProps) {
  const handleExport = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/conversations/${conversationId}/export?format=${format}`,
        {
          method: 'GET',
        }
      );

      if (!response.ok) {
        throw new Error('Falha ao exportar conversa');
      }

      // Obtém nome do arquivo do header
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `conversation_${conversationId}.${format}`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }

      // Download do arquivo
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      console.log('success', `Conversa exportada como ${format.toUpperCase()}`);
    } catch (error) {
      console.error('Erro ao exportar:', error);
      console.log('error', 'Erro ao exportar conversa');
    }
  };

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={handleExport}
      title={`Exportar como ${format.toUpperCase()}`}
      className={cn("p-2", className)}
    >
      <Download className="h-4 w-4" />
    </Button>
  );
}
