"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Send } from "lucide-react"
import { cn } from "@/lib/utils"

interface ChatInputProps {
  onSendMessage: (message: string) => void
  isLoading?: boolean
  disabled?: boolean
}

export function ChatInput({ onSendMessage, isLoading = false, disabled = false }: ChatInputProps) {
  const [message, setMessage] = useState("")

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (message.trim() && !isLoading && !disabled) {
      onSendMessage(message.trim())
      setMessage("")
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e as any)
    }
  }

  return (
    <form 
      onSubmit={handleSubmit}
      className="flex items-center gap-2 p-4 glass-nav border-t"
    >
      <Input
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your message..."
        disabled={isLoading || disabled}
        className={cn(
          "flex-1 glass-input border-0 shadow-lg",
          "placeholder:text-muted-foreground/60",
          "focus-visible:ring-2 focus-visible:ring-primary/20"
        )}
      />
      <Button
        type="submit"
        size="icon"
        disabled={!message.trim() || isLoading || disabled}
        className={cn(
          "shrink-0 shadow-lg bg-gradient-to-r from-purple-500 to-blue-500",
          "hover:from-purple-600 hover:to-blue-600",
          "disabled:opacity-50 disabled:cursor-not-allowed"
        )}
      >
        <Send className={cn(
          "w-4 h-4 transition-transform",
          isLoading && "animate-pulse"
        )} />
      </Button>
    </form>
  )
} 