import { useState } from "react";
import { Check, Copy } from "lucide-react";
import { Button } from "./ui/button";

const CodeBlock = ({ code, language = "cpp" }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  return (
    <div className="relative group" data-testid="code-block">
      <div className="absolute top-2 right-2 z-10">
        <Button
          variant="ghost"
          size="sm"
          onClick={handleCopy}
          className="h-8 w-8 p-0 bg-neutral-800/80 hover:bg-neutral-700 opacity-0 group-hover:opacity-100 transition-opacity"
          data-testid="copy-code-btn"
        >
          {copied ? (
            <Check size={14} className="text-emerald-400" />
          ) : (
            <Copy size={14} className="text-neutral-400" />
          )}
        </Button>
      </div>
      
      {language && (
        <div className="absolute top-2 left-3 text-xs text-neutral-500 font-mono">
          {language}
        </div>
      )}
      
      <pre className="bg-black/60 border border-white/10 rounded-sm p-4 pt-8 overflow-x-auto">
        <code className="text-sm text-neutral-200 font-mono whitespace-pre">
          {code}
        </code>
      </pre>
    </div>
  );
};

export default CodeBlock;
