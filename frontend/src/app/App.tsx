import { useState } from 'react';
import { RepoInput } from './components/RepoInput';
import { ProcessingState } from './components/ProcessingState';
import { ChatInterface } from './components/ChatInterface';
import { processRepo, queryRepo } from "./api/client.ts";


export default function App() {
  const [state, setState] = useState('input');
  const [repoUrl, setRepoUrl] = useState('');

  async function handleProcessRepo (url) {
    if(!url) return;
    setRepoUrl(url);
    try {
      setState('processing');
      await processRepo(url);
      setState('chat');
    } catch (err) {
      alert(`Error processing repository: ${err.message}`);
      setState('input');
    }
  };

  const handleReset = () => {
    setState('input');
    setRepoUrl('');
  };

  return (
    <>
      {state === 'input' && <RepoInput onProcessRepo={handleProcessRepo} />}
      {state === 'processing' && <ProcessingState repoUrl={repoUrl} />}
      {state === 'chat' && <ChatInterface repoUrl={repoUrl} onReset={handleReset} />}
    </>
  );
}
