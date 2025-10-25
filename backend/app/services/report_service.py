"""
Report service for generating interview analysis reports in various formats.
"""
import os
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from jinja2 import Template
from app.schemas.analysis import AnalysisResult, FeedbackItem, FeedbackCategory
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ReportService:
    """Service for generating interview analysis reports."""
    
    def __init__(self):
        """Initialize report service."""
        self.report_dir = os.path.join(settings.UPLOAD_DIRECTORY, "reports")
        os.makedirs(self.report_dir, exist_ok=True)
    
    async def generate_pdf_report(
        self,
        analysis_result: AnalysisResult,
        user_name: str,
        interview_title: str
    ) -> str:
        """
        Generate PDF report for interview analysis.
        
        Args:
            analysis_result: Analysis results
            user_name: User's name
            interview_title: Interview title
            
        Returns:
            str: Path to generated PDF file
        """
        try:
            # Generate unique filename
            filename = f"interview_report_{uuid.uuid4()}.pdf"
            file_path = os.path.join(self.report_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            story.append(Paragraph("Interview Analysis Report", title_style))
            story.append(Spacer(1, 12))
            
            # Header information
            header_data = [
                ['Candidate:', user_name],
                ['Interview:', interview_title],
                ['Date:', analysis_result.created_at.strftime('%Y-%m-%d %H:%M:%S')],
                ['Overall Score:', f"{analysis_result.overall_score:.1%}"]
            ]
            
            header_table = Table(header_data, colWidths=[2*inch, 4*inch])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (1, 0), (1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(header_table)
            story.append(Spacer(1, 20))
            
            # Executive Summary
            story.append(Paragraph("Executive Summary", styles['Heading2']))
            story.append(Paragraph(analysis_result.summary, styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Strengths
            story.append(Paragraph("Key Strengths", styles['Heading2']))
            for strength in analysis_result.strengths:
                story.append(Paragraph(f"• {strength}", styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Areas for Improvement
            story.append(Paragraph("Areas for Improvement", styles['Heading2']))
            for area in analysis_result.areas_for_improvement:
                story.append(Paragraph(f"• {area}", styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Detailed Feedback
            story.append(Paragraph("Detailed Feedback", styles['Heading2']))
            
            for feedback_item in analysis_result.feedback_items:
                # Category header
                story.append(Paragraph(
                    f"{feedback_item.category.value.replace('_', ' ').title()}: {feedback_item.score:.1%}",
                    styles['Heading3']
                ))
                
                # Feedback text
                story.append(Paragraph(feedback_item.feedback_text, styles['Normal']))
                
                # Strengths
                if feedback_item.strengths:
                    story.append(Paragraph("Strengths:", styles['Heading4']))
                    for strength in feedback_item.strengths:
                        story.append(Paragraph(f"• {strength}", styles['Normal']))
                
                # Areas for improvement
                if feedback_item.areas_for_improvement:
                    story.append(Paragraph("Areas for Improvement:", styles['Heading4']))
                    for area in feedback_item.areas_for_improvement:
                        story.append(Paragraph(f"• {area}", styles['Normal']))
                
                # Suggestions
                if feedback_item.suggestions:
                    story.append(Paragraph("Suggestions:", styles['Heading4']))
                    for suggestion in feedback_item.suggestions:
                        story.append(Paragraph(f"• {suggestion}", styles['Normal']))
                
                story.append(Spacer(1, 12))
            
            # Recommendations
            story.append(Paragraph("Recommendations", styles['Heading2']))
            for recommendation in analysis_result.recommendations:
                story.append(Paragraph(f"• {recommendation}", styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF report generated: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            raise Exception(f"Failed to generate PDF report: {str(e)}")
    
    async def generate_html_report(
        self,
        analysis_result: AnalysisResult,
        user_name: str,
        interview_title: str
    ) -> str:
        """
        Generate HTML report for interview analysis.
        
        Args:
            analysis_result: Analysis results
            user_name: User's name
            interview_title: Interview title
            
        Returns:
            str: Path to generated HTML file
        """
        try:
            # Generate unique filename
            filename = f"interview_report_{uuid.uuid4()}.html"
            file_path = os.path.join(self.report_dir, filename)
            
            # HTML template
            html_template = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Interview Analysis Report</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                    .header { background-color: #f4f4f4; padding: 20px; border-radius: 5px; margin-bottom: 30px; }
                    .score { font-size: 24px; font-weight: bold; color: #2c3e50; }
                    .section { margin-bottom: 30px; }
                    .feedback-item { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
                    .strengths { color: #27ae60; }
                    .improvements { color: #e74c3c; }
                    .recommendations { background-color: #ecf0f1; padding: 15px; border-radius: 5px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Interview Analysis Report</h1>
                    <p><strong>Candidate:</strong> {{ user_name }}</p>
                    <p><strong>Interview:</strong> {{ interview_title }}</p>
                    <p><strong>Date:</strong> {{ analysis_date }}</p>
                    <p class="score">Overall Score: {{ overall_score }}%</p>
                </div>
                
                <div class="section">
                    <h2>Executive Summary</h2>
                    <p>{{ summary }}</p>
                </div>
                
                <div class="section">
                    <h2>Key Strengths</h2>
                    <ul>
                        {% for strength in strengths %}
                        <li class="strengths">{{ strength }}</li>
                        {% endfor %}
                    </ul>
                </div>
                
                <div class="section">
                    <h2>Areas for Improvement</h2>
                    <ul>
                        {% for area in areas_for_improvement %}
                        <li class="improvements">{{ area }}</li>
                        {% endfor %}
                    </ul>
                </div>
                
                <div class="section">
                    <h2>Detailed Feedback</h2>
                    {% for feedback in feedback_items %}
                    <div class="feedback-item">
                        <h3>{{ feedback.category.value.replace('_', ' ').title() }}: {{ feedback.score }}%</h3>
                        <p>{{ feedback.feedback_text }}</p>
                        
                        {% if feedback.strengths %}
                        <h4>Strengths:</h4>
                        <ul>
                            {% for strength in feedback.strengths %}
                            <li class="strengths">{{ strength }}</li>
                            {% endfor %}
                        </ul>
                        {% endif %}
                        
                        {% if feedback.areas_for_improvement %}
                        <h4>Areas for Improvement:</h4>
                        <ul>
                            {% for area in feedback.areas_for_improvement %}
                            <li class="improvements">{{ area }}</li>
                            {% endfor %}
                        </ul>
                        {% endif %}
                        
                        {% if feedback.suggestions %}
                        <h4>Suggestions:</h4>
                        <ul>
                            {% for suggestion in feedback.suggestions %}
                            <li>{{ suggestion }}</li>
                            {% endfor %}
                        </ul>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
                
                <div class="section">
                    <h2>Recommendations</h2>
                    <div class="recommendations">
                        <ul>
                            {% for recommendation in recommendations %}
                            <li>{{ recommendation }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Render template
            template = Template(html_template)
            html_content = template.render(
                user_name=user_name,
                interview_title=interview_title,
                analysis_date=analysis_result.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                overall_score=f"{analysis_result.overall_score:.1%}",
                summary=analysis_result.summary,
                strengths=analysis_result.strengths,
                areas_for_improvement=analysis_result.areas_for_improvement,
                feedback_items=analysis_result.feedback_items,
                recommendations=analysis_result.recommendations
            )
            
            # Write HTML file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML report generated: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            raise Exception(f"Failed to generate HTML report: {str(e)}")
    
    async def generate_json_report(
        self,
        analysis_result: AnalysisResult,
        user_name: str,
        interview_title: str
    ) -> str:
        """
        Generate JSON report for interview analysis.
        
        Args:
            analysis_result: Analysis results
            user_name: User's name
            interview_title: Interview title
            
        Returns:
            str: Path to generated JSON file
        """
        try:
            # Generate unique filename
            filename = f"interview_report_{uuid.uuid4()}.json"
            file_path = os.path.join(self.report_dir, filename)
            
            # Prepare report data
            report_data = {
                "report_info": {
                    "candidate_name": user_name,
                    "interview_title": interview_title,
                    "generated_at": datetime.utcnow().isoformat(),
                    "analysis_id": analysis_result.id,
                    "interview_id": analysis_result.interview_id
                },
                "overall_score": analysis_result.overall_score,
                "summary": analysis_result.summary,
                "strengths": analysis_result.strengths,
                "areas_for_improvement": analysis_result.areas_for_improvement,
                "recommendations": analysis_result.recommendations,
                "detailed_feedback": [
                    {
                        "category": feedback.category.value,
                        "score": feedback.score,
                        "feedback_text": feedback.feedback_text,
                        "strengths": feedback.strengths,
                        "areas_for_improvement": feedback.areas_for_improvement,
                        "suggestions": feedback.suggestions
                    }
                    for feedback in analysis_result.feedback_items
                ],
                "detailed_analysis": analysis_result.detailed_analysis
            }
            
            # Write JSON file
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"JSON report generated: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error generating JSON report: {e}")
            raise Exception(f"Failed to generate JSON report: {str(e)}")
    
    async def generate_report(
        self,
        analysis_result: AnalysisResult,
        user_name: str,
        interview_title: str,
        format_type: str = "pdf"
    ) -> str:
        """
        Generate report in specified format.
        
        Args:
            analysis_result: Analysis results
            user_name: User's name
            interview_title: Interview title
            format_type: Report format (pdf, html, json)
            
        Returns:
            str: Path to generated report file
        """
        try:
            if format_type.lower() == "pdf":
                return await self.generate_pdf_report(analysis_result, user_name, interview_title)
            elif format_type.lower() == "html":
                return await self.generate_html_report(analysis_result, user_name, interview_title)
            elif format_type.lower() == "json":
                return await self.generate_json_report(analysis_result, user_name, interview_title)
            else:
                raise Exception(f"Unsupported report format: {format_type}")
                
        except Exception as e:
            logger.error(f"Error generating {format_type} report: {e}")
            raise Exception(f"Failed to generate {format_type} report: {str(e)}")
    
    async def cleanup_old_reports(self, days_old: int = 30) -> int:
        """
        Clean up old report files.
        
        Args:
            days_old: Number of days after which to delete reports
            
        Returns:
            int: Number of files deleted
        """
        try:
            import time
            current_time = time.time()
            cutoff_time = current_time - (days_old * 24 * 60 * 60)
            
            deleted_count = 0
            
            for filename in os.listdir(self.report_dir):
                file_path = os.path.join(self.report_dir, filename)
                
                if os.path.isfile(file_path):
                    file_time = os.path.getmtime(file_path)
                    
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old report files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old reports: {e}")
            return 0
