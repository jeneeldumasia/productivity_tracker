import datetime
import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors

def generate_weekly_report_pdf(file_path, week_start_date, weekly_data_df, config):
    """
    Generates a formatted PDF report for the selected week's productivity data.
    """
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # --- 1. Title ---
    title = f"Productivity Report for the Week of {week_start_date.strftime('%Y-%m-%d')}"
    story.append(Paragraph(title, styles['h1']))
    story.append(Spacer(1, 0.2 * inch))

    # --- 2. Summary Metrics ---
    if not weekly_data_df.empty:
        productive_apps = config.get('productivity_apps', [])
        productive_mask = weekly_data_df['app_name'].str.contains('|'.join(productive_apps), case=False, na=False)
        
        total_seconds = weekly_data_df['duration_seconds'].sum()
        productive_seconds = weekly_data_df[productive_mask]['duration_seconds'].sum()
        focus_score = (productive_seconds / total_seconds * 100) if total_seconds > 0 else 0

        summary_text = f"<b>Total Time Tracked:</b> {str(datetime.timedelta(seconds=int(total_seconds)))}<br/>"
        summary_text += f"<b>Total Productive Time:</b> {str(datetime.timedelta(seconds=int(productive_seconds)))}<br/>"
        summary_text += f"<b>Weekly Focus Score:</b> {focus_score:.1f}%"
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))
    
    # --- 3. Matplotlib Chart Image ---
    # Create the chart in memory
    from ui.pages.weekly_report_page import WeeklyReportPage # Import locally to avoid circular deps
    
    # We need a temporary figure to generate the chart
    from matplotlib.figure import Figure
    fig = Figure(figsize=(8, 4))
    ax = fig.subplots()
    
    # Re-generate the bar chart logic here
    productive_df = weekly_data_df[productive_mask]
    if not productive_df.empty:
        daily_productive_time = productive_df.groupby(productive_df['start_time'].dt.date)['duration_seconds'].sum() / 3600
        date_range = pd.to_datetime(pd.date_range(start=week_start_date, periods=7)).date
        daily_productive_time = daily_productive_time.reindex(date_range, fill_value=0)
        days_of_week = [d.strftime('%a') for d in daily_productive_time.index]
        
        ax.bar(days_of_week, daily_productive_time.values, color='#4CAF50')
        ax.set_ylabel("Productive Time (Hours)")
        ax.set_title("Productive Time per Day")
        fig.tight_layout()

        # Save chart to an in-memory buffer
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=300)
        img_buffer.seek(0)
        
        story.append(Image(img_buffer, width=6*inch, height=3*inch))
        story.append(Spacer(1, 0.2 * inch))

    # --- 4. Top 5 Applications Table ---
    if not weekly_data_df.empty:
        story.append(Paragraph("Top 5 Applications Used", styles['h2']))
        top_5_apps = weekly_data_df.groupby('app_name')['duration_seconds'].sum().nlargest(5)
        
        table_data = [['Rank', 'Application', 'Time Spent']]
        for i, (app, duration) in enumerate(top_5_apps.items()):
            table_data.append([i + 1, app, str(datetime.timedelta(seconds=int(duration)))])
            
        t = Table(table_data, colWidths=[0.5*inch, 4*inch, 1.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t)

    # --- Build the PDF ---
    doc.build(story)