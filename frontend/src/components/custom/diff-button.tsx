"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Copy, FileText } from "lucide-react"
import { toast } from "sonner"

interface GitDiffButtonProps {
  diffContent: string
  buttonText?: string
}

export function GitDiffButton({ diffContent, buttonText = "View Diff" }: GitDiffButtonProps) {
  const [isOpen, setIsOpen] = useState(false)

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(diffContent)
      toast("Copied!", {
        description: "Git diff copied to clipboard",
      })
    } catch {

      toast.error("Failed to copy",{
        description: "Could not copy diff to clipboard",
      })
    }
  }

  const formatDiffLine = (line: string, index: number) => {
    if (line.startsWith("---") || line.startsWith("+++")) {
      return (
        <div key={index} className="text-muted-foreground font-mono text-sm py-1">
          {line}
        </div>
      )
    }

    if (line.startsWith("@@")) {
      return (
        <div
          key={index}
          className="text-blue-600 dark:text-blue-400 font-mono text-sm py-1 bg-blue-50 dark:bg-blue-950/30 px-2 rounded"
        >
          {line}
        </div>
      )
    }

    if (line.startsWith("+")) {
      return (
        <div
          key={index}
          className="text-green-700 dark:text-green-400 font-mono text-sm py-1 bg-green-50 dark:bg-green-950/30 px-2"
        >
          <span className="text-green-600 dark:text-green-500 mr-2">+</span>
          {line.slice(1)}
        </div>
      )
    }

    if (line.startsWith("-")) {
      return (
        <div
          key={index}
          className="text-red-700 dark:text-red-400 font-mono text-sm py-1 bg-red-50 dark:bg-red-950/30 px-2"
        >
          <span className="text-red-600 dark:text-red-500 mr-2">-</span>
          {line.slice(1)}
        </div>
      )
    }

    return (
      <div key={index} className="text-foreground font-mono text-sm py-1 px-2">
        <span className="text-muted-foreground mr-2"> </span>
        {line}
      </div>
    )
  }

  const diffLines = diffContent.split("\n")

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" className="gap-2 bg-transparent">
          <FileText className="h-4 w-4" />
          {buttonText}
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            Git Diff
            <Button variant="ghost" size="sm" onClick={copyToClipboard} className="gap-2">
              <Copy className="h-4 w-4" />
              Copy
            </Button>
          </DialogTitle>
          <DialogDescription>Review the changes between the old and new versions</DialogDescription>
        </DialogHeader>
        <ScrollArea className="h-[60vh] w-full rounded-md border">
          <div className="p-4 space-y-1">{diffLines.map((line, index) => formatDiffLine(line, index))}</div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}

