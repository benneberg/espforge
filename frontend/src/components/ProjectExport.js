import { useState } from "react";
import { Download, FileText, FileJson, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "./ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import jsPDF from "jspdf";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const ProjectExport = ({ project }) => {
  const [exporting, setExporting] = useState(false);

  const downloadMarkdown = async () => {
    setExporting(true);
    try {
      const response = await fetch(`${API}/projects/${project.id}/export/markdown`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${project.name.replace(/\s+/g, '_')}_export.md`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success("Markdown exported successfully!");
    } catch (err) {
      console.error("Export failed:", err);
      toast.error("Failed to export markdown");
    } finally {
      setExporting(false);
    }
  };

  const downloadJSON = async () => {
    setExporting(true);
    try {
      const response = await fetch(`${API}/projects/${project.id}/export/json`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${project.name.replace(/\s+/g, '_')}_export.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success("JSON exported successfully!");
    } catch (err) {
      console.error("Export failed:", err);
      toast.error("Failed to export JSON");
    } finally {
      setExporting(false);
    }
  };

  const downloadPDF = async () => {
    setExporting(true);
    try {
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4'
      });

      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margin = 20;
      const contentWidth = pageWidth - (margin * 2);
      let yPos = margin;

      // Helper to add text with word wrap
      const addText = (text, fontSize = 10, isBold = false, color = [0, 0, 0]) => {
        pdf.setFontSize(fontSize);
        pdf.setFont('helvetica', isBold ? 'bold' : 'normal');
        pdf.setTextColor(color[0], color[1], color[2]);
        
        const lines = pdf.splitTextToSize(text, contentWidth);
        lines.forEach(line => {
          if (yPos > pageHeight - margin) {
            pdf.addPage();
            yPos = margin;
          }
          pdf.text(line, margin, yPos);
          yPos += fontSize * 0.4;
        });
        yPos += 2;
      };

      // Title
      pdf.setFillColor(245, 158, 11);
      pdf.rect(0, 0, pageWidth, 40, 'F');
      pdf.setTextColor(0, 0, 0);
      pdf.setFontSize(24);
      pdf.setFont('helvetica', 'bold');
      pdf.text(project.name, margin, 25);
      pdf.setFontSize(10);
      pdf.setFont('helvetica', 'normal');
      pdf.text(`ESP32 IoT Project • ${project.target_hardware}`, margin, 33);
      
      yPos = 50;

      // Project Info
      addText('PROJECT IDEA', 12, true, [245, 158, 11]);
      addText(project.idea, 10, false, [60, 60, 60]);
      yPos += 5;

      if (project.description) {
        addText('DESCRIPTION', 12, true, [245, 158, 11]);
        addText(project.description, 10, false, [60, 60, 60]);
        yPos += 5;
      }

      // Stages
      const stageTitles = {
        requirements: 'REQUIREMENTS',
        hardware: 'HARDWARE SELECTION',
        architecture: 'FIRMWARE ARCHITECTURE',
        code: 'GENERATED CODE',
        explanation: 'EXPLANATION',
        iteration: 'ITERATIONS'
      };

      const stages = project.stages || {};
      Object.entries(stageTitles).forEach(([key, title]) => {
        const stageData = stages[key];
        if (stageData?.content) {
          // Add page break before code section
          if (key === 'code') {
            pdf.addPage();
            yPos = margin;
          }
          
          addText(title, 12, true, [245, 158, 11]);
          
          // For code, use monospace-like formatting
          if (key === 'code') {
            pdf.setFontSize(8);
            const codeLines = stageData.content.split('\n');
            codeLines.forEach(line => {
              if (yPos > pageHeight - margin) {
                pdf.addPage();
                yPos = margin;
              }
              pdf.setFont('courier', 'normal');
              pdf.setTextColor(40, 40, 40);
              pdf.text(line.substring(0, 100), margin, yPos);
              yPos += 3;
            });
          } else {
            // Clean markdown formatting for other sections
            const cleanContent = stageData.content
              .replace(/#{1,6}\s/g, '')
              .replace(/\*\*/g, '')
              .replace(/\*/g, '')
              .replace(/```[\s\S]*?```/g, '[Code Block]');
            addText(cleanContent, 10, false, [60, 60, 60]);
          }
          yPos += 8;
        }
      });

      // Footer
      const totalPages = pdf.internal.getNumberOfPages();
      for (let i = 1; i <= totalPages; i++) {
        pdf.setPage(i);
        pdf.setFontSize(8);
        pdf.setTextColor(150, 150, 150);
        pdf.text(`ESP32 IoT Copilot • Page ${i} of ${totalPages}`, margin, pageHeight - 10);
        pdf.text(new Date().toLocaleDateString(), pageWidth - margin - 20, pageHeight - 10);
      }

      pdf.save(`${project.name.replace(/\s+/g, '_')}_export.pdf`);
      toast.success("PDF exported successfully!");
    } catch (err) {
      console.error("PDF export failed:", err);
      toast.error("Failed to export PDF");
    } finally {
      setExporting(false);
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="outline" 
          size="sm"
          disabled={exporting}
          data-testid="export-btn"
        >
          {exporting ? (
            <Loader2 size={16} className="animate-spin mr-2" />
          ) : (
            <Download size={16} className="mr-2" />
          )}
          Export
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={downloadMarkdown} data-testid="export-md">
          <FileText size={14} className="mr-2" />
          Export as Markdown
        </DropdownMenuItem>
        <DropdownMenuItem onClick={downloadPDF} data-testid="export-pdf">
          <FileText size={14} className="mr-2 text-red-400" />
          Export as PDF
        </DropdownMenuItem>
        <DropdownMenuItem onClick={downloadJSON} data-testid="export-json">
          <FileJson size={14} className="mr-2 text-blue-400" />
          Export as JSON
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default ProjectExport;
