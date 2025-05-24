"use client"

import { useState, useRef, useEffect } from "react"
import { ChatMessage } from "@/components/chat-message"
import { ChatInput } from "@/components/chat-input"
import { TypingIndicator } from "@/components/typing-indicator"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { Moon, Sun, Bot } from "lucide-react"

interface Message {
  id: string
  content: string
  isUser: boolean
  timestamp: Date
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isDarkMode, setIsDarkMode] = useState(false)
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]')
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight
      }
    }
  }, [messages, isLoading])

  // Toggle dark mode
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [isDarkMode])

  async function handleSendMessage(content: string) {
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      isUser: true,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      const formData = new FormData()
      formData.append('message', content)

      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (data.success) {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: data.response,
          isUser: false,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, assistantMessage])
      } else {
        throw new Error(data.error || 'Failed to get response')
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        isUser: false,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-mesh">
      {/* Header */}
      <header className="glass-nav px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-semibold text-lg">AIDEN</h1>
            <p className="text-xs text-muted-foreground">AI Assistant</p>
          </div>
        </div>
        
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsDarkMode(!isDarkMode)}
          className="rounded-full"
        >
          {isDarkMode ? (
            <Sun className="w-5 h-5" />
          ) : (
            <Moon className="w-5 h-5" />
          )}
        </Button>
      </header>

      {/* Chat Messages */}
      <ScrollArea 
        ref={scrollAreaRef}
        className="flex-1 px-6 py-4 custom-scrollbar"
      >
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center mb-4">
              <Bot className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-xl font-semibold mb-2">Welcome to AIDEN</h2>
            <p className="text-muted-foreground max-w-md">
              I'm your AI assistant powered by Gemini. Ask me anything, and I'll do my best to help you with web search capabilities!
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message.content}
                isUser={message.isUser}
                timestamp={message.timestamp}
              />
            ))}
            {isLoading && <TypingIndicator />}
          </div>
        )}
      </ScrollArea>

      {/* Chat Input */}
      <ChatInput
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
      />
    </div>
  )
}
