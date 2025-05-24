"use client"

import { cn } from "@/lib/utils"
import { Bot, Search, Loader2, AlertCircle } from "lucide-react"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

interface ToolActivityProps {
  type: "tool_start" | "tool_end" | "llm_chunk" | "error" | "info"
  name?: string
  input?: string
  result?: string
  detail?: string
}

export function ToolActivity({ type, name, input, result, detail }: ToolActivityProps) {
  return (
    <div className="flex items-start gap-3 mb-4 animate-slide-up opacity-80">
      <Avatar className="w-8 h-8 ring-2 ring-offset-2 ring-offset-background ring-accent">
        <AvatarFallback className="bg-gradient-to-br from-purple-500 to-blue-500 text-white">
          <Bot className="w-4 h-4" />
        </AvatarFallback>
      </Avatar>
      
      <div className="tool-activity bg-muted px-4 py-3 rounded-lg text-sm flex items-center gap-3 max-w-[70%]">
        {type === "tool_start" && (
          <>
            <Search className="w-4 h-4 text-accent-foreground animate-pulse" />
            <div>
              <span className="font-medium">Using tool: {name}</span>
              {input && <div className="text-xs text-muted-foreground mt-1">{input}</div>}
            </div>
          </>
        )}
        
        {type === "tool_end" && (
          <>
            <Search className="w-4 h-4 text-green-500" />
            <div>
              <span className="font-medium">Tool {name} completed</span>
              {result && (
                <div className="text-xs text-muted-foreground mt-1 whitespace-pre-wrap break-words max-h-28 overflow-y-auto">
                  {result}
                </div>
              )}
            </div>
          </>
        )}
        
        {type === "error" && (
          <>
            <AlertCircle className="w-4 h-4 text-destructive" />
            <span className="text-destructive">{detail || "An error occurred"}</span>
          </>
        )}
        
        {type === "info" && (
          <>
            <AlertCircle className="w-4 h-4 text-blue-500" />
            <span>{detail || "Information"}</span>
          </>
        )}

        {type === "llm_chunk" && (
          <div className="flex items-center">
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            <span>Thinking...</span>
          </div>
        )}
      </div>
    </div>
  )
} 