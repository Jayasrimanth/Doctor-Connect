import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Send, Bot, User, Loader2 } from "lucide-react";
import { toast } from "sonner";
import chatBackground from "@/assets/chat-background.jpg";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const Chat = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! I'm your medical appointment assistant. I'll help you book an appointment with the right doctor. May I have your full name please?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // Call the Node.js backend API
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001';
      console.log('Sending message to:', `${API_URL}/api/chat`);
      
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: input, 
          history: messages.map(m => ({ role: m.role, content: m.content }))
        })
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: `HTTP ${response.status}` }));
        throw new Error(errorData.error || errorData.details || `API error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Response data:', data);
      
      if (data.success) {
        setMessages(prev => [...prev, { role: "assistant", content: data.response }]);
        
        // If appointment is confirmed, optionally navigate to doctors page
        if (data.shouldTransition) {
          setTimeout(() => {
            navigate("/doctors");
          }, 2000);
        }
      } else {
        throw new Error(data.error || data.details || 'Failed to get response');
      }
      
      setIsLoading(false);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to send message. Please try again.';
      toast.error(errorMessage);
      setIsLoading(false);
      
      // Add error message to chat for debugging
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: `Sorry, I encountered an error: ${errorMessage}. Please make sure all services are running.` 
      }]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background Image with Overlay */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: `url(${chatBackground})` }}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-primary/85 via-primary/75 to-secondary/70"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-6 animate-fade-in">
            <h1 className="text-4xl font-bold mb-2 text-white drop-shadow-lg">Medical Assistant</h1>
            <p className="text-white/90 drop-shadow">Chat with our AI to book your appointment</p>
          </div>

          {/* Chat Container */}
          <Card className="shadow-2xl animate-slide-up bg-white/95 backdrop-blur-sm border-white/20">
            {/* Messages Area */}
            <div className="h-[500px] overflow-y-auto p-6 space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex gap-3 ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  } animate-fade-in`}
                >
                  {message.role === "assistant" && (
                    <div className="bg-primary/10 w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0">
                      <Bot className="h-5 w-5 text-primary" />
                    </div>
                  )}
                  <div
                    className={`max-w-[75%] px-4 py-3 rounded-lg ${
                      message.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-foreground"
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  </div>
                  {message.role === "user" && (
                    <div className="bg-secondary/10 w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0">
                      <User className="h-5 w-5 text-secondary" />
                    </div>
                  )}
                </div>
              ))}
              
              {isLoading && (
                <div className="flex gap-3 justify-start animate-fade-in">
                  <div className="bg-primary/10 w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0">
                    <Bot className="h-5 w-5 text-primary" />
                  </div>
                  <div className="bg-muted px-4 py-3 rounded-lg">
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></span>
                      <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></span>
                      <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-border p-4">
              <div className="flex gap-2">
                <Input
                  placeholder="Type your message..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={isLoading}
                  className="flex-1"
                />
                <Button
                  onClick={handleSend}
                  disabled={isLoading || !input.trim()}
                  size="icon"
                  className="flex-shrink-0"
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          </Card>

          {/* Help Text */}
          <p className="text-center text-sm text-white/80 mt-4 drop-shadow">
            Our AI assistant will guide you through the booking process step by step
          </p>
        </div>
      </div>
    </div>
  );
};

export default Chat;
