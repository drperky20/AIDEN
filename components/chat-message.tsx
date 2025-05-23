"use client"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"
import { Bot, User } from "lucide-react"

interface ChatMessageProps {
  message: string
  isUser: boolean
  timestamp?: Date
}

export function ChatMessage({ message, isUser, timestamp }: ChatMessageProps) {
  return (
    <div className={cn(
      "flex items-start gap-3 mb-6 animate-slide-up",
      isUser ? "flex-row-reverse" : "flex-row"
    )}>
      <Avatar className={cn(
        "w-8 h-8 ring-2 ring-offset-2 ring-offset-background",
        isUser ? "ring-primary" : "ring-accent"
      )}>
        <AvatarFallback className={cn(
          "text-xs font-medium",
          isUser 
            ? "bg-primary text-primary-foreground" 
            : "bg-gradient-to-br from-purple-500 to-blue-500 text-white"
        )}>
          {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
        </AvatarFallback>
      </Avatar>
      
      <div className={cn(
        "max-w-[70%] px-4 py-3 text-sm leading-relaxed",
        isUser 
          ? "message-user" 
          : "message-assistant"
      )}>
        <div className="whitespace-pre-wrap break-words">
          {message}
        </div>
        
        {timestamp && (
          <div className={cn(
            "text-xs mt-2 opacity-60",
            isUser ? "text-primary-foreground" : "text-muted-foreground"
          )}>
            {timestamp.toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </div>
        )}
      </div>
    </div>
  )
} 