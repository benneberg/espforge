import { useState } from "react";
import { Check, RefreshCw, MessageSquare, ChevronDown, ChevronUp } from "lucide-react";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Card } from "./ui/card";
import CodeBlock from "./CodeBlock";

const StageContent = ({ 
  stage, 
  stageData, 
  isCurrentStage, 
  onGenerate, 
  onApprove, 
  isGenerating 
}) => {
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [isExpanded, setIsExpanded] = useState(isCurrentStage);

  const parseContent = (content) => {
    if (!content) return null;
    
    // Split content into sections and code blocks
    const parts = [];
    const lines = content.split('\n');
    let currentBlock = [];
    let inCodeBlock = false;
    let codeLanguage = '';
    
    lines.forEach((line, idx) => {
      if (line.startsWith('```')) {
        if (inCodeBlock) {
          // End of code block
          parts.push({
            type: 'code',
            content: currentBlock.join('\n'),
            language: codeLanguage
          });
          currentBlock = [];
          inCodeBlock = false;
          codeLanguage = '';
        } else {
          // Start of code block
          if (currentBlock.length > 0) {
            parts.push({
              type: 'markdown',
              content: currentBlock.join('\n')
            });
            currentBlock = [];
          }
          inCodeBlock = true;
          codeLanguage = line.slice(3).trim() || 'text';
        }
      } else {
        currentBlock.push(line);
      }
    });
    
    // Don't forget remaining content
    if (currentBlock.length > 0) {
      parts.push({
        type: inCodeBlock ? 'code' : 'markdown',
        content: currentBlock.join('\n'),
        language: codeLanguage
      });
    }
    
    return parts;
  };

  const renderContent = (content) => {
    const parts = parseContent(content);
    if (!parts) return null;
    
    return parts.map((part, idx) => {
      if (part.type === 'code') {
        return <CodeBlock key={idx} code={part.content} language={part.language} />;
      }
      return (
        <div 
          key={idx} 
          className="markdown-content"
          dangerouslySetInnerHTML={{ 
            __html: part.content
              .replace(/^## (.+)$/gm, '<h2>$1</h2>')
              .replace(/^### (.+)$/gm, '<h3>$1</h3>')
              .replace(/^- (.+)$/gm, '<li>$1</li>')
              .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
              .replace(/`([^`]+)`/g, '<code>$1</code>')
              .replace(/\n\n/g, '</p><p>')
              .replace(/^(.+)$/gm, (match) => {
                if (match.startsWith('<')) return match;
                return `<p>${match}</p>`;
              })
          }}
        />
      );
    });
  };

  const handleGenerateWithFeedback = () => {
    onGenerate(feedback);
    setFeedback("");
    setShowFeedback(false);
  };

  return (
    <Card 
      className={`bg-neutral-900/40 border-white/10 overflow-hidden ${
        isCurrentStage ? 'border-primary/30 glow-primary' : ''
      }`}
      data-testid={`stage-${stage}`}
    >
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 hover:bg-white/5 transition-colors"
        data-testid={`stage-header-${stage}`}
      >
        <div className="flex items-center gap-3">
          <div className={`stage-dot ${
            stageData?.user_approved ? 'completed' : 
            isCurrentStage ? 'current' : 'pending'
          }`} />
          <span className="font-heading font-bold text-neutral-100 capitalize">
            {stage.replace('_', ' ')}
          </span>
          {stageData?.user_approved && (
            <Check size={16} className="text-emerald-500" />
          )}
        </div>
        {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
      </button>

      {/* Content */}
      {isExpanded && (
        <div className="px-4 pb-4 animate-fade-in">
          {stageData?.content ? (
            <div className="space-y-4">
              {renderContent(stageData.content)}
              
              {/* Actions */}
              {isCurrentStage && !stageData.user_approved && (
                <div className="flex flex-col gap-3 pt-4 border-t border-white/10">
                  <div className="flex gap-2">
                    <Button
                      onClick={() => onApprove(true)}
                      className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white"
                      data-testid={`approve-${stage}`}
                    >
                      <Check size={16} className="mr-2" />
                      Approve & Continue
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => onGenerate()}
                      disabled={isGenerating}
                      data-testid={`regenerate-${stage}`}
                    >
                      <RefreshCw size={16} className={isGenerating ? 'animate-spin' : ''} />
                    </Button>
                  </div>
                  
                  <Button
                    variant="ghost"
                    onClick={() => setShowFeedback(!showFeedback)}
                    className="text-neutral-400"
                    data-testid={`feedback-toggle-${stage}`}
                  >
                    <MessageSquare size={16} className="mr-2" />
                    Add feedback & regenerate
                  </Button>
                  
                  {showFeedback && (
                    <div className="space-y-2 animate-fade-in">
                      <Textarea
                        value={feedback}
                        onChange={(e) => setFeedback(e.target.value)}
                        placeholder="What would you like to change or improve?"
                        className="bg-black/50 border-white/10 min-h-[80px]"
                        data-testid={`feedback-input-${stage}`}
                      />
                      <Button 
                        onClick={handleGenerateWithFeedback}
                        disabled={!feedback.trim() || isGenerating}
                        className="w-full"
                        data-testid={`submit-feedback-${stage}`}
                      >
                        {isGenerating ? (
                          <RefreshCw size={16} className="mr-2 animate-spin" />
                        ) : (
                          <RefreshCw size={16} className="mr-2" />
                        )}
                        Regenerate with Feedback
                      </Button>
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              {isCurrentStage ? (
                <Button
                  onClick={() => onGenerate()}
                  disabled={isGenerating}
                  className="bg-primary text-black hover:bg-primary/90 glow-primary-strong"
                  data-testid={`generate-${stage}`}
                >
                  {isGenerating ? (
                    <>
                      <RefreshCw size={16} className="mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>Generate {stage.replace('_', ' ')}</>
                  )}
                </Button>
              ) : (
                <p className="text-neutral-500 text-sm">
                  Complete previous stages first
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </Card>
  );
};

export default StageContent;
