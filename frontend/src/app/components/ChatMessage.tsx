import { MessageCircle, Code } from 'lucide-react';

export function ChatMessage({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-4 mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div 
          className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center"
          style={{ backgroundColor: '#4F6D7A' }}
        >
          <Code className="w-5 h-5 text-white" />
        </div>
      )}
      
      <div 
        className={`max-w-[70%] rounded-lg p-4 ${
          isUser ? 'rounded-br-none' : 'rounded-bl-none'
        }`}
        style={{ 
          backgroundColor: isUser ? '#4F6D7A' : 'white',
          color: isUser ? 'white' : '#4F6D7A',
          boxShadow: '0 2px 8px rgba(79, 109, 122, 0.1)'
        }}
      >
        <p className="whitespace-pre-wrap break-words">{message.content}</p>
      </div>

      {isUser && (
        <div 
          className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center"
          style={{ backgroundColor: '#4F6D7A' }}
        >
          <MessageCircle className="w-5 h-5 text-white" />
        </div>
      )}
    </div>
  );
}
