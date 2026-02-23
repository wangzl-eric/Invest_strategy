"""PDF report generation and scheduled reporting."""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from io import BytesIO
import pandas as pd

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate PDF reports for portfolio analytics."""
    
    def __init__(self):
        if not HAS_REPORTLAB:
            logger.warning("ReportLab not installed - PDF generation disabled")
            self.enabled = False
        else:
            self.enabled = True
            self.styles = getSampleStyleSheet()
            self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        if not self.enabled:
            return
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6
        ))
    
    def generate_performance_report(
        self,
        account_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_charts: bool = True
    ) -> BytesIO:
        """
        Generate a comprehensive performance report PDF.
        
        Returns BytesIO buffer with PDF content.
        """
        if not self.enabled:
            raise RuntimeError("PDF generation not available (ReportLab not installed)")
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("Portfolio Performance Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Report metadata
        metadata = [
            ["Account ID:", account_id],
            ["Report Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Period:", f"{start_date.strftime('%Y-%m-%d') if start_date else 'All'} to {end_date.strftime('%Y-%m-%d') if end_date else 'Latest'}"],
        ]
        
        metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(metadata_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Performance metrics section
        story.append(Paragraph("Performance Metrics", self.styles['CustomHeading']))
        
        # Get metrics (this would call your data processor)
        # For now, placeholder
        metrics_data = [
            ["Metric", "Value"],
            ["Total Return", "N/A"],
            ["Sharpe Ratio", "N/A"],
            ["Sortino Ratio", "N/A"],
            ["Max Drawdown", "N/A"],
            ["Volatility", "N/A"],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[3*inch, 3*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(metrics_table)
        story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_trade_report(
        self,
        account_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> BytesIO:
        """Generate a trade history report PDF."""
        if not self.enabled:
            raise RuntimeError("PDF generation not available")
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        story.append(Paragraph("Trade History Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Add trade data table
        # This would fetch actual trade data from database
        story.append(Paragraph("Trade History", self.styles['CustomHeading']))
        story.append(Paragraph("Trade data would be displayed here.", self.styles['CustomBody']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer


class ScheduledReportService:
    """Service for scheduling and sending reports."""
    
    def __init__(self):
        self.report_generator = ReportGenerator()
    
    def schedule_daily_report(
        self,
        account_id: str,
        recipient_email: str,
        report_time: str = "09:00"  # Default 9 AM
    ):
        """Schedule a daily report to be sent via email."""
        # This would integrate with APScheduler
        logger.info(f"Scheduled daily report for {account_id} to {recipient_email} at {report_time}")
        # TODO: Implement actual scheduling
    
    def generate_and_send_report(
        self,
        account_id: str,
        report_type: str,
        recipient_email: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ):
        """Generate a report and send via email."""
        try:
            if report_type == "performance":
                pdf_buffer = self.report_generator.generate_performance_report(
                    account_id, start_date, end_date
                )
            elif report_type == "trades":
                pdf_buffer = self.report_generator.generate_trade_report(
                    account_id, start_date, end_date
                )
            else:
                raise ValueError(f"Unknown report type: {report_type}")
            
            # Send email with PDF attachment
            # This would use your email service
            logger.info(f"Generated {report_type} report for {account_id}")
            # TODO: Implement email sending
            
        except Exception as e:
            logger.error(f"Error generating/sending report: {e}", exc_info=True)
            raise


# Global instances
report_generator = ReportGenerator()
scheduled_report_service = ScheduledReportService()
