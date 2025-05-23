"use client"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Bot } from "lucide-react"

export function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 mb-6 animate-slide-up">
      <Avatar className="w-8 h-8 ring-2 ring-offset-2 ring-offset-background ring-accent">
        <AvatarFallback className="text-xs font-medium bg-gradient-to-br from-purple-500 to-blue-500 text-white">
          <Bot className="w-4 h-4" />
        </AvatarFallback>
      </Avatar>
      
      <div className="message-assistant px-4 py-3">
        <div className="flex items-center gap-1">
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:-0.3s]"></div>
            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:-0.15s]"></div>
            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
          </div>
          <span className="text-xs text-muted-foreground ml-2">AI is thinking...</span>
        </div>
      </div>
    </div>
  )
} 