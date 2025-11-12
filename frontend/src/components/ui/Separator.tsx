interface SeparatorProps {
  orientation?: 'horizontal' | 'vertical';
  className?: string;
}

export const Separator = ({ orientation = 'horizontal', className = '' }: SeparatorProps) => {
  if (orientation === 'vertical') {
    return (
      <div className={`w-px h-full bg-border-glass ${className}`} />
    );
  }

  return (
    <div className={`h-px w-full bg-border-glass ${className}`} />
  );
};