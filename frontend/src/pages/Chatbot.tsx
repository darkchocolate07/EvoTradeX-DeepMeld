import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';
import { useStockContext } from '../context/StockContext';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! I\'m your investment assistant. How can I help you today?',
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { stocks, totalValue } = useStockContext();

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Sample responses based on keywords
  const getBotResponse = (userMessage: string): string => {
    const message = userMessage.toLowerCase();
    
    if (message.includes('portfolio') && message.includes('value')) {
      return `Your portfolio is currently valued at $${totalValue.toFixed(2)}.`;
    }
    
    if (message.includes('best') && message.includes('performing')) {
      const bestStock = [...stocks].sort((a, b) => {
        const aReturn = ((a.currentPrice - a.purchasePrice) / a.purchasePrice) * 100;
        const bReturn = ((b.currentPrice - b.purchasePrice) / b.purchasePrice) * 100;
        return bReturn - aReturn;
      })[0];
      
      const returnPercentage = ((bestStock.currentPrice - bestStock.purchasePrice) / bestStock.purchasePrice) * 100;
      
      return `Your best performing stock is ${bestStock.name} (${bestStock.ticker}) with a return of ${returnPercentage.toFixed(2)}%.`;
    }
    
    if (message.includes('worst') && message.includes('performing')) {
      const worstStock = [...stocks].sort((a, b) => {
        const aReturn = ((a.currentPrice - a.purchasePrice) / a.purchasePrice) * 100;
        const bReturn = ((b.currentPrice - b.purchasePrice) / b.purchasePrice) * 100;
        return aReturn - bReturn;
      })[0];
      
      const returnPercentage = ((worstStock.currentPrice - worstStock.purchasePrice) / worstStock.purchasePrice) * 100;
      
      return `Your worst performing stock is ${worstStock.name} (${worstStock.ticker}) with a return of ${returnPercentage.toFixed(2)}%.`;
    }
    
    if (message.includes('recommend') || message.includes('suggestion')) {
      return 'Based on your portfolio and risk profile, I would recommend diversifying more into technology and healthcare sectors. These sectors have shown strong growth potential and could complement your existing investments.';
    }
    
    if (message.includes('market') && message.includes('outlook')) {
      return 'The market outlook for the next quarter appears cautiously optimistic. Economic indicators suggest moderate growth, though inflation concerns remain. Consider maintaining a balanced portfolio with some defensive positions.';
    }
    
    if (message.includes('risk') && message.includes('reduce')) {
      return 'To reduce risk in your portfolio, consider adding more defensive stocks, increasing bond allocation, or investing in low-volatility ETFs. Diversification across sectors and asset classes is key to risk management.';
    }
    
    if (message.includes('dividend')) {
      return 'For dividend-focused investing, look into utilities, consumer staples, and established financial companies. REITs also offer attractive dividend yields. Your current portfolio has a weighted average dividend yield of approximately 1.8%.';
    }
    
    if (message.includes('hello') || message.includes('hi') || message.includes('hey')) {
      return 'Hello! How can I assist with your investment portfolio today?';
    }
    
    if (message.includes('thank')) {
      return 'You\'re welcome! Is there anything else I can help you with?';
    }

    if(message.includes('tesla')){
        setTimeout(() => {window.location.href = window.location.hostname + "/stock/4"},1000)
        return 'Based on current news, and past market data ,Tesla Inc. (TSLA) should perform well in the coming few days.';
    }
    
    // Default response
    return 'I\'m not sure I understand. Could you rephrase your question? You can ask me about your portfolio value, best/worst performing stocks, market outlook, or investment recommendations.';
  };

  const handleSend = () => {
    if (input.trim() === '') return;
    
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
      timestamp: new Date(),
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);
    
    // Simulate bot typing delay
    setTimeout(() => {
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: getBotResponse(input),
        sender: 'bot',
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, botMessage]);
      setIsTyping(false);
    }, 1000 + Math.random() * 1000); // Random delay between 1-2 seconds
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-screen p-6">
      <h1 className="text-2xl font-bold mb-6">Investment Assistant</h1>
      
      <div className="card flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`mb-4 flex ${
                message.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  message.sender === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-white'
                }`}
              >
                <div className="flex items-center mb-1">
                  {message.sender === 'bot' ? (
                    <Bot className="h-4 w-4 mr-2" />
                  ) : (
                    <User className="h-4 w-4 mr-2" />
                  )}
                  <span className="text-xs opacity-75">
                    {message.timestamp.toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                </div>
                <p className="whitespace-pre-wrap">{message.text}</p>
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="flex justify-start mb-4">
              <div className="bg-gray-700 text-white rounded-lg p-3">
                <div className="flex items-center">
                  <Bot className="h-4 w-4 mr-2" />
                  <div className="typing-indicator">
                    <span className="dot"></span>
                    <span className="dot"></span>
                    <span className="dot"></span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        <div className="border-t border-gray-700 p-4">
          <div className="flex">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="flex-1 bg-gray-700 text-white rounded-l-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              rows={1}
            />
            <button
              onClick={handleSend}
              disabled={input.trim() === ''}
              className={`bg-blue-600 hover:bg-blue-700 text-white px-4 rounded-r-md flex items-center justify-center ${
                input.trim() === '' ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
          <p className="text-xs text-gray-400 mt-2">
            Ask about your portfolio, stock recommendations, market trends, or investment strategies.
          </p>
        </div>
      </div>
      
      <style jsx>{`
        .typing-indicator {
          display: flex;
          align-items: center;
        }
        
        .dot {
          display: inline-block;
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background-color: #a0a0a0;
          margin-right: 4px;
          animation: typing 1.4s infinite ease-in-out;
        }
        
        .dot:nth-child(1) {
          animation-delay: 0s;
        }
        
        .dot:nth-child(2) {
          animation-delay: 0.2s;
        }
        
        .dot:nth-child(3) {
          animation-delay: 0.4s;
          margin-right: 0;
        }
        
        @keyframes typing {
          0%, 60%, 100% {
            transform: translateY(0);
          }
          30% {
            transform: translateY(-6px);
          }
        }
      `}</style>
    </div>
  );
};

export default Chatbot;