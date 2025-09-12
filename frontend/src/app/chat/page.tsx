"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { FileText, Send, Upload, ArrowLeft, Bot, User, Loader2 } from "lucide-react"
import Link from "next/link"

interface Message {
  id: string
  type: "user" | "assistant"
  content: string
  timestamp: Date
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "assistant",
      content:
        "Hi! I'm here to help you understand terms and conditions. You can paste a URL to a T&C page, or ask me questions about legal documents.",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [urlInput, setUrlInput] = useState("")

  const handleSendMessage = async () => {
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: input,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    // Simulate AI response
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content:
          "I understand you're asking about terms and conditions. While this is a demo, in the full version I would analyze the document and provide clear explanations of complex legal language, highlight important clauses, and help you understand what you're agreeing to.",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMessage])
      setIsLoading(false)
    }, 1500)
  }

  const handleAnalyzeUrl = async () => {
    if (!urlInput.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: `Please analyze this T&C page: ${urlInput}`,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setUrlInput("")
    setIsLoading(true)

    // Simulate URL analysis
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: `I've analyzed the terms and conditions from ${urlInput}. Here's what I found:\n\n**Key Points:**\n• Data collection includes personal information and usage patterns\n• Service can be terminated with 30 days notice\n• User content may be used for service improvement\n• Disputes resolved through binding arbitration\n\n**Potential Concerns:**\n• Broad data sharing with third parties\n• Limited liability protection for the company\n• Automatic renewal clauses\n\nWould you like me to explain any of these points in more detail?`,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMessage])
      setIsLoading(false)
    }, 2000)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
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
          <Badge variant="secondary">Demo Mode</Badge>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* URL Input Section */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5" />
              Analyze Terms & Conditions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2">
              <Input
                placeholder="Paste URL to terms and conditions page..."
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                className="flex-1"
              />
              <Button onClick={handleAnalyzeUrl} disabled={!urlInput.trim() || isLoading}>
                Analyze
              </Button>
            </div>
            <p className="text-sm text-muted-foreground mt-2">
              Currently supports HTML pages that are not client-side rendered
            </p>
          </CardContent>
        </Card>

        {/* Chat Messages */}
        <Card className="mb-4">
          <CardContent className="p-0">
            <div className="h-96 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${message.type === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`flex gap-3 max-w-[80%] ${message.type === "user" ? "flex-row-reverse" : "flex-row"}`}
                  >
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                        message.type === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted text-muted-foreground"
                      }`}
                    >
                      {message.type === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                    </div>
                    <div
                      className={`rounded-lg p-3 ${
                        message.type === "user" ? "bg-primary text-primary-foreground" : "bg-muted text-foreground"
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      <p className="text-xs opacity-70 mt-1">{message.timestamp.toLocaleTimeString()}</p>
                    </div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex gap-3 justify-start">
                  <div className="flex gap-3 max-w-[80%]">
                    <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 bg-muted text-muted-foreground">
                      <Bot className="h-4 w-4" />
                    </div>
                    <div className="rounded-lg p-3 bg-muted text-foreground">
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span className="text-sm">Analyzing...</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Chat Input */}
        <Card>
          <CardContent className="p-4">
            <div className="flex gap-2">
              <Textarea
                placeholder="Ask me about terms and conditions, privacy policies, or legal documents..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                className="flex-1 min-h-[60px] resize-none"
                disabled={isLoading}
              />
              <Button onClick={handleSendMessage} disabled={!input.trim() || isLoading} size="lg" className="px-4">
                <Send className="h-4 w-4" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-2">Press Enter to send, Shift+Enter for new line</p>
          </CardContent>
        </Card>

        {/* Example Questions */}
        <div className="mt-6">
          <h3 className="text-sm font-medium text-muted-foreground mb-3">Try asking:</h3>
          <div className="flex flex-wrap gap-2">
            {[
              "What data does this company collect?",
              "Can I delete my account?",
              "What happens if I cancel?",
              "Are there any hidden fees?",
              "How is my data shared?",
            ].map((question) => (
              <Button
                key={question}
                variant="outline"
                size="sm"
                onClick={() => setInput(question)}
                disabled={isLoading}
                className="text-xs"
              >
                {question}
              </Button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

