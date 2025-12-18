import { useState, useRef, useEffect } from 'react';
import { Send, Github, RefreshCw } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { ChatMessage } from './ChatMessage';
import { queryRepo } from "../api/client.ts";

export function ChatInterface({ repoUrl, onReset }) {
  const [messages, setMessages] = useState([
    {
      id: '1',
      role: 'assistant',
      content: `Repository processed successfully! I'm ready to answer your questions about the codebase. What would you like to know?`
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const repoName = repoUrl.split('/').slice(-2).join('/').replace('.git', '');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Simulate backend API call
    try{
      const res = await queryRepo(userMessage.content);
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: res.response
      };
      setMessages(prev => [...prev, assistantMessage]);
      setIsLoading(false);
      inputRef.current?.focus();
    } catch (err) {
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Error: ${err.message}`
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
      inputRef.current?.focus();
    }
    
  };

  return (
    <div className="flex flex-col h-screen" style={{ backgroundColor: '#C0D6DF' }}>
      {/* Header */}
      <div className="shadow-md" style={{ backgroundColor: '#4F6D7A' }}>
        <div className="max-w-5xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Github className="w-6 h-6 text-white" />
              <div>
                <h2 className="text-white">CodeBase Assistant</h2>
                <p className="text-sm text-white/80">{repoName}</p>
              </div>
            </div>
            <Button
              onClick={onReset}
              variant="ghost"
              className="text-white hover:bg-white/10 flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              New Session
            </Button>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto px-6 py-8">
          {messages.map(message => (
            <ChatMessage key={message.id} message={message} />
          ))}
          {isLoading && (
            <div className="flex gap-4 mb-6">
              <div 
                className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center"
                style={{ backgroundColor: '#4F6D7A' }}
              >
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              </div>
              <div 
                className="rounded-lg rounded-bl-none p-4"
                style={{ backgroundColor: 'white', color: '#4F6D7A' }}
              >
                <p className="opacity-70">Analyzing...</p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t bg-white" style={{ borderColor: '#C0D6DF' }}>
        <div className="max-w-5xl mx-auto px-6 py-4">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <Input
              ref={inputRef}
              type="text"
              placeholder="Ask a question about the repository..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={isLoading}
              className="flex-1 border-2 focus:ring-2"
              style={{ borderColor: '#C0D6DF' }}
            />
            <Button
              type="submit"
              disabled={!inputValue.trim() || isLoading}
              className="px-6 flex items-center gap-2 transition-all hover:shadow-lg"
              style={{ backgroundColor: '#4F6D7A' }}
            >
              <Send className="w-5 h-5" />
              Send
            </Button>
          </form>
          <p className="text-xs mt-3 text-center opacity-60" style={{ color: '#4F6D7A' }}>
            Press Enter to send • Session-based chat
          </p>
        </div>
      </div>
    </div>
  );
}
