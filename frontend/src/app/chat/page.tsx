"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { MarkdownRenderer } from "@/components/custom/markdown-rendered"
import { FileText, Send, ArrowLeft, Bot, User, Loader2 } from "lucide-react"
import Link from "next/link"
import { api } from "@/lib/utils"

interface Message {
  id: string
  type: "user" | "assistant"
  content: string
  diff?: string
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "assistant",
      content:
        "Hi! I'm here to help you understand terms and conditions. You can paste a URL to a T&C page, or ask me questions about legal documents.\n\nI can help with:\n- **Analyzing** complex legal language\n- **Highlighting** important clauses\n- **Explaining** what you're agreeing to\n- **Identifying** potential concerns",
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const hasLatestDiff = () => {
    const latestAssistantMessage = messages.filter((m) => m.type === "assistant").pop()
    return latestAssistantMessage?.diff && latestAssistantMessage.diff.trim() !== ""
  }

  const handleViewDiff = () => {
    const latestAssistantMessage = messages.filter((m) => m.type === "assistant").pop()
    if (latestAssistantMessage?.diff) {
      console.log("Diff data:", latestAssistantMessage.diff)
      window.open("/diff", "_blank")
    }
  }

  const handleSendMessage = async () => {
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: input,
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    const session_id = localStorage.getItem("demistify_session_id") || ""

    const response = await api.post("/chat", { text: input, session_id })
    const data = response.data.data
    console.log("Response data:", data)

    setTimeout(() => {
      const hasDiff = Math.random() > 0.5
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content:
          data.response || "Sorry, we couldn't process your request at this time. Please try again later.",
        diff: hasDiff ? "Sample diff data - changes detected in T&C document" : undefined,
      }
      setMessages((prev) => [...prev, assistantMessage])
      setIsLoading(false)
    }, 1500)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
              <ArrowLeft className="h-5 w-5" />
              <span className="text-sm text-muted-foreground">Back to Home</span>
            </Link>
            <div className="flex items-center space-x-2">
              <FileText className="h-8 w-8 text-primary" />
              <span className="text-2xl font-bold text-foreground">Demistify Chat</span>
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 flex flex-col container mx-auto px-4 py-4 max-w-4xl">
        <Card className="flex-1 flex flex-col mb-4">
          <CardContent className="p-0 flex-1 flex flex-col">
            <div className="flex-1 overflow-y-auto p-6 space-y-6 min-h-0 max-h-[calc(100vh-280px)] scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-4 ${message.type === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`flex gap-4 max-w-[85%] ${message.type === "user" ? "flex-row-reverse" : "flex-row"}`}
                  >
                    <div
                      className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 border-2 ${
                        message.type === "user"
                          ? "bg-primary text-primary-foreground border-primary/20"
                          : "bg-secondary text-secondary-foreground border-secondary/20"
                      }`}
                    >
                      {message.type === "user" ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
                    </div>
                    <div
                      className={`rounded-2xl px-4 py-3 shadow-sm ${
                        message.type === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-secondary/50 text-foreground border border-border"
                      }`}
                    >
                      {message.type === "user" ? (
                        <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
                      ) : (
                        <MarkdownRenderer content={message.content} />
                      )}
                    </div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex gap-4 justify-start">
                  <div className="flex gap-4 max-w-[85%]">
                    <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 bg-secondary text-secondary-foreground border-2 border-secondary/20">
                      <Bot className="h-5 w-5" />
                    </div>
                    <div className="rounded-2xl px-4 py-3 bg-secondary/50 text-foreground border border-border">
                      <div className="flex items-center gap-3">
                        <Loader2 className="h-4 w-4 animate-spin text-primary" />
                        <span className="text-sm">Analyzing...</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex gap-3">
              <Textarea
                placeholder="Ask me about terms and conditions, privacy policies, or legal documents..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                className="flex-1 min-h-[80px] resize-none text-sm leading-relaxed"
                disabled={isLoading}
              />
              <div className="flex flex-col gap-3">
                <Button
                  onClick={handleSendMessage}
                  disabled={!input.trim() || isLoading}
                  size="lg"
                  className="px-6 h-12"
                >
                  <Send className="h-4 w-4" />
                </Button>
                {hasLatestDiff() && (
                  <Button
                    onClick={handleViewDiff}
                    variant="secondary"
                    size="lg"
                    className="px-6 h-12"
                    title="View document changes"
                  >
                    <FileText className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
            <p className="text-xs text-muted-foreground mt-3 leading-relaxed">
              Press Enter to send, Shift+Enter for new line
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

