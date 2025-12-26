import { useState } from "react";
import { Check, Copy } from "lucide-react";
import { Button } from "./ui/button";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

const LANGUAGE_MAP = {
  cpp: "cpp",
  c: "c",
  "c++": "cpp",
  arduino: "cpp",
  ino: "cpp",
  python: "python",
  py: "python",
  javascript: "javascript",
  js: "javascript",
  json: "json",
  bash: "bash",
  shell: "bash",
  sh: "bash",
  text: "text",
  markdown: "markdown",
  md: "markdown",
  yaml: "yaml",
  yml: "yaml",
  html: "html",
  css: "css",
};

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

  const normalizedLanguage = LANGUAGE_MAP[language?.toLowerCase()] || "text";

  // Custom style overrides for oneDark theme
  const customStyle = {
    ...oneDark,
    'pre[class*="language-"]': {
      ...oneDark['pre[class*="language-"]'],
      background: "rgba(0, 0, 0, 0.6)",
      margin: 0,
      padding: "1rem",
      paddingTop: "2rem",
      borderRadius: "0.25rem",
      border: "1px solid rgba(255, 255, 255, 0.1)",
      fontSize: "0.875rem",
      lineHeight: "1.5",
    },
    'code[class*="language-"]': {
      ...oneDark['code[class*="language-"]'],
      background: "transparent",
      fontSize: "0.875rem",
    },
  };

  return (
    <div className="relative group" data-testid="code-block">
      <div className="absolute top-2 right-2 z-10 flex items-center gap-2">
        {language && (
          <span className="text-xs text-neutral-500 font-mono bg-neutral-800/80 px-2 py-1 rounded">
            {language}
          </span>
        )}
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
      
      <SyntaxHighlighter
        language={normalizedLanguage}
        style={customStyle}
        showLineNumbers={code.split('\n').length > 5}
        wrapLines={true}
        customStyle={{
          background: "rgba(0, 0, 0, 0.6)",
          margin: 0,
          borderRadius: "0.25rem",
        }}
        lineNumberStyle={{
          minWidth: "2.5em",
          paddingRight: "1em",
          color: "#525252",
          userSelect: "none",
        }}
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
};

export default CodeBlock;
