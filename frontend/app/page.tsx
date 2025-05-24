"use client"

import { useState, useRef, useEffect } from "react"
import { ChatMessage } from "@/components/chat-message"
import { ChatInput } from "@/components/chat-input"
import { TypingIndicator } from "@/components/typing-indicator"
import { ToolActivity } from "@/components/tool-activity"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { Moon, Sun, Bot, Settings } from "lucide-react"

// Backend API URL configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Message {
  id: string
  content: string
  isUser: boolean
  timestamp: Date
}

interface ToolEvent {
  id: string
  type: "tool_start" | "tool_end" | "llm_chunk" | "error" | "info"
  name?: string
  input?: string
  result?: string
  detail?: string
}

type ChatItem = Message | ToolEvent;

function isMessage(item: ChatItem): item is Message {
  return 'isUser' in item;
}

function isToolEvent(item: ChatItem): item is ToolEvent {
  return 'type' in item;
}

export default function ChatPage() {
  const [chatItems, setChatItems] = useState<ChatItem[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [useStreaming, setUseStreaming] = useState(true) // Toggle between streaming and non-streaming
  const [backendError, setBackendError] = useState<string | null>(null)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const eventSourceRef = useRef<EventSource | null>(null)

  // Clean up EventSource on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }
    }
  }, [])

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]')
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight
      }
    }
  }, [chatItems, isLoading])

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

    setChatItems(prev => [...prev, userMessage])
    setIsLoading(true)
    setBackendError(null)
    
    // If streaming is enabled, use EventSource/SSE
    if (useStreaming) {
      try {
        // Clean up any existing connection
        if (eventSourceRef.current) {
          eventSourceRef.current.close()
          eventSourceRef.current = null
        }
        
        const params = new URLSearchParams()
        params.append('message', content)
        
        // Create new EventSource connection with error handling
        const eventSourceUrl = `${API_URL}/chat-stream?${params.toString()}`
        const eventSource = new EventSource(eventSourceUrl)
        eventSourceRef.current = eventSource
        
        eventSource.onmessage = (event) => {
          try {
            const eventData = JSON.parse(event.data)
            
            // Handle different event types
            if (eventData.type === "tool_start" || eventData.type === "tool_end" || eventData.type === "info") {
              // Handle tool events
              const toolEvent: ToolEvent = {
                id: Date.now().toString() + Math.random().toString(36).substring(2, 9),
                type: eventData.type,
                name: eventData.name,
                input: eventData.input,
                result: eventData.result,
                detail: eventData.detail
              }
              setChatItems(prev => [...prev, toolEvent])
            } 
            else if (eventData.type === "llm_chunk") {
              // Just show a "thinking" indicator for now - or could accumulate chunks
              const thinkingEvent: ToolEvent = {
                id: Date.now().toString() + Math.random().toString(36).substring(2, 9),
                type: "llm_chunk",
                detail: "Thinking..."
              }
              setChatItems(prev => {
                // Only add if there isn't already a thinking indicator
                if (!prev.some(item => isToolEvent(item) && item.type === "llm_chunk")) {
                  return [...prev, thinkingEvent]
                }
                return prev
              })
            } 
            else if (eventData.type === "error") {
              // Handle errors
              const errorEvent: ToolEvent = {
                id: Date.now().toString() + Math.random().toString(36).substring(2, 9),
                type: "error",
                detail: eventData.detail || "An error occurred"
              }
              setChatItems(prev => [...prev, errorEvent])
              setIsLoading(false)
              eventSource.close()
              eventSourceRef.current = null
            } 
            else if (eventData.type === "final_response") {
              // Add the final response as a message
              const finalMessage: Message = {
                id: Date.now().toString(),
                content: eventData.content,
                isUser: false,
                timestamp: new Date()
              }
              
              // Remove any temporary "thinking" indicators
              setChatItems(prev => [
                ...prev.filter(item => !(isToolEvent(item) && item.type === "llm_chunk")),
                finalMessage
              ])
              
              setIsLoading(false)
              eventSource.close()
              eventSourceRef.current = null
            }
          } catch (error) {
            console.error("Error parsing event data:", error)
          }
        }
        
        eventSource.onerror = (error) => {
          console.error("EventSource error:", error)
          setIsLoading(false)
          
          // Close and nullify the event source
          eventSource.close()
          eventSourceRef.current = null
          
          const errorEvent: ToolEvent = {
            id: Date.now().toString() + Math.random().toString(36).substring(2, 9),
            type: "error",
            detail: "Connection error. Please try again or check if the backend server is running."
          }
          setChatItems(prev => [...prev, errorEvent])
          
          // Set backend error state
          setBackendError("Could not connect to the backend server. Please check if it's running.")
        }
      } catch (error) {
        console.error("Error setting up EventSource:", error)
        setIsLoading(false)
        
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: `Sorry, I couldn't connect to the backend: ${error instanceof Error ? error.message : 'Unknown error'}`,
          isUser: false,
          timestamp: new Date()
        }
        setChatItems(prev => [...prev, errorMessage])
        setBackendError("Failed to set up streaming connection")
      }
      
      return
    }

    // Non-streaming fallback using the original /chat endpoint
    try {
      const formData = new FormData()
      formData.append('message', content)

      const response = await fetch(`${API_URL}/chat`, {
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
        setChatItems(prev => [...prev, assistantMessage])
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
      setChatItems(prev => [...prev, errorMessage])
      setBackendError("Could not connect to the backend server")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-mesh">
      {/* Header */}
      <header className="glass-nav px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg aiden-logo flex items-center justify-center">
            <img src="/aiden-logo.svg" alt="AIDEN" className="w-6 h-6" />
          </div>
          <div>
            <h1 className="font-semibold text-lg">AIDEN</h1>
            <p className="text-xs text-muted-foreground">AI Agent Platform</p>
          </div>
        </div>
        
        <div className="flex gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setUseStreaming(!useStreaming)}
            className="rounded-full"
            title={useStreaming ? "Disable streaming" : "Enable streaming"}
          >
            <Settings className={`w-5 h-5 ${useStreaming ? "text-accent" : "text-muted-foreground"}`} />
          </Button>
          
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
        </div>
      </header>

      {/* Backend Error Banner */}
      {backendError && (
        <div className="bg-red-500 text-white px-4 py-2 text-sm text-center">
          {backendError} 
          <button 
            className="ml-2 underline" 
            onClick={() => setBackendError(null)}
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Chat Messages */}
      <ScrollArea 
        ref={scrollAreaRef}
        className="flex-1 px-6 py-4 custom-scrollbar"
      >
        {chatItems.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-2xl aiden-logo flex items-center justify-center mb-4 aiden-glow">
              <img src="/aiden-logo.svg" alt="AIDEN" className="w-12 h-12" />
            </div>
            <h2 className="text-xl font-semibold mb-2">Welcome to AIDEN Agent Platform</h2>
            <p className="text-muted-foreground max-w-md">
              I'm your AI agent with memory, web search, and interactive tools. Ask me anything, and see my thought process in real-time!
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {chatItems.map((item) => (
              isMessage(item) ? (
                <ChatMessage
                  key={item.id}
                  message={item.content}
                  isUser={item.isUser}
                  timestamp={item.timestamp}
                />
              ) : (
                <ToolActivity
                  key={item.id}
                  type={item.type}
                  name={item.name}
                  input={item.input}
                  result={item.result}
                  detail={item.detail}
                />
              )
            ))}
            {isLoading && !useStreaming && <TypingIndicator />}
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
