import { Loader } from 'lucide-react';

export function ProcessingState({ repoUrl }) {
  const repoName = repoUrl.split('/').slice(-2).join('/').replace('.git', '');

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-4" style={{ backgroundColor: '#C0D6DF' }}>
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full mb-6" style={{ backgroundColor: '#4F6D7A' }}>
          <Loader className="w-10 h-10 text-white animate-spin" />
        </div>
        <h2 className="mb-3" style={{ color: '#4F6D7A' }}>Processing Repository</h2>
        <p className="text-lg mb-8 opacity-80" style={{ color: '#4F6D7A' }}>
          {repoName}
        </p>
        <div className="flex gap-2 justify-center">
          <div className="w-2 h-2 rounded-full animate-bounce" style={{ backgroundColor: '#4F6D7A', animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 rounded-full animate-bounce" style={{ backgroundColor: '#4F6D7A', animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 rounded-full animate-bounce" style={{ backgroundColor: '#4F6D7A', animationDelay: '300ms' }}></div>
        </div>
        <p className="mt-8 text-sm opacity-70" style={{ color: '#4F6D7A' }}>
          This may take a few moments...
        </p>
      </div>
    </div>
  );
}
