"use client"

import ReactMarkdown from "react-markdown"
import { useTheme } from "next-themes"

interface MarkdownRendererProps {
  content: string
  className?: string
}

// Custom CodeBlock component
function CodeBlock({ children, className }: { children: string; className?: string }) {
  const { theme } = useTheme()
  const language = className?.replace("language-", "") || "text"

  return (
    <div className="relative">
      <div className="flex items-center justify-between bg-muted px-3 py-2 rounded-t-md border-b">
        <span className="text-xs font-mono text-muted-foreground uppercase">{language}</span>
      </div>
      <pre className="bg-muted/50 p-3 rounded-b-md overflow-x-auto">
        <code className="text-sm font-mono text-foreground whitespace-pre">{children}</code>
      </pre>
    </div>
  )
}

export function MarkdownRenderer({ content, className = "" }: MarkdownRendererProps) {
  return (
    <div className={`prose prose-sm max-w-none dark:prose-invert ${className}`}>
      <ReactMarkdown
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || "")
            return !inline && match ? (
              <CodeBlock className={className}>{String(children).replace(/\n$/, "")}</CodeBlock>
            ) : (
              <code className="bg-muted px-1 py-0.5 rounded text-sm" {...props}>
                {children}
              </code>
            )
          },
          h1: ({ children }) => <h1 className="text-lg font-semibold mb-2">{children}</h1>,
          h2: ({ children }) => <h2 className="text-base font-semibold mb-2">{children}</h2>,
          h3: ({ children }) => <h3 className="text-sm font-semibold mb-1">{children}</h3>,
          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
          ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
          li: ({ children }) => <li className="text-sm">{children}</li>,
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-primary pl-4 italic my-2">{children}</blockquote>
          ),
          a: ({ children, href }) => (
            <a href={href} className="text-primary hover:underline" target="_blank" rel="noopener noreferrer">
              {children}
            </a>
          ),
          strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
          em: ({ children }) => <em className="italic">{children}</em>,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}

