import { FileText } from "lucide-react";
import Link from "next/link";

export function Logo() {
    return (
      <Link href="/">
        <div className="flex items-center space-x-2">
          <FileText className="h-6 w-6 text-primary" />
          <span className="text-2xl font-bold text-foreground">Demistify</span>
        </div>
      </Link>
    )
}
