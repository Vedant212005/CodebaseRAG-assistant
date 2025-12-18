import { useState } from 'react';
import { Github, ArrowRight } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';

export function RepoInput({ onProcessRepo }) {
  const [repoUrl, setRepoUrl] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (repoUrl.trim()) {
      onProcessRepo(repoUrl.trim());
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-4" style={{ backgroundColor: '#C0D6DF' }}>
      <div className="w-full max-w-2xl">
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full mb-6" style={{ backgroundColor: '#4F6D7A' }}>
            <Github className="w-10 h-10 text-white" />
          </div>
          <h1 className="mb-4" style={{ color: '#4F6D7A' }}>CodeBase Assistant</h1>
          <p className="text-lg opacity-80" style={{ color: '#4F6D7A' }}>
            Analyze and chat with any GitHub repository
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <label htmlFor="repo-url" className="block mb-3" style={{ color: '#4F6D7A' }}>
              GitHub Repository URL
            </label>
            <Input
              id="repo-url"
              type="url"
              placeholder="https://github.com/username/repository"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              className="mb-6 border-2 focus:ring-2"
              style={{ borderColor: '#C0D6DF' }}
              required
            />
            <Button
              type="submit"
              className="w-full flex items-center justify-center gap-2 transition-all hover:shadow-lg"
              style={{ backgroundColor: '#4F6D7A' }}
              disabled={!repoUrl.trim()}
            >
              Process Repository
              <ArrowRight className="w-5 h-5" />
            </Button>
          </div>
        </form>

        <div className="mt-8 text-center">
          <p className="text-sm opacity-70" style={{ color: '#4F6D7A' }}>
            Session-based • No login required • Chat with your code
          </p>
        </div>
      </div>
    </div>
  );
}
