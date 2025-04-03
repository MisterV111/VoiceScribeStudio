"""
Token Usage Dashboard Component

This module provides a Gradio interface for displaying token usage metrics
and API cost estimates based on the token tracking database.
"""

import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime
import numpy as np
from app.utils.token_counter import token_tracker

def create_token_dashboard():
    """
    Create a Gradio interface for token usage metrics visualization.
    
    Returns:
        gr.Blocks: A Gradio Blocks interface for the token dashboard
    """
    
    def refresh_data(time_period, include_tests):
        """Get data and update visualizations"""
        summary = token_tracker.get_usage_summary(days=int(time_period), include_tests=include_tests)
        
        if 'error' in summary and summary['error']:
            return (
                f"Error retrieving data: {summary['error']}",
                None, None, None, None, None
            )
        
        # Create total usage text
        total_requests = summary.get('total_requests', 0)
        total_cost = summary.get('total_cost', 0)
        
        # Create usage text
        usage_text = f"""
        ## Token Usage Summary (Past {time_period} Days)
        
        **Total API Cost:** ${total_cost:.2f}
        **Total Requests:** {total_requests}
        """
        
        # Process model usage data
        if not summary.get('model_usage'):
            return (
                "No data available for the selected period.",
                None, None, None, None, None
            )
            
        model_data = []
        
        for model, usage in summary['model_usage'].items():
            model_data.append({
                "Model": model,
                "Input Tokens": usage.get('input_tokens', 0),
                "Output Tokens": usage.get('output_tokens', 0),
                "Total Tokens": usage.get('total_tokens', 0),
                "Requests": usage.get('request_count', 0),
                "Cost": usage.get('estimated_cost', 0)
            })
        
        # Model usage bar chart
        model_df = pd.DataFrame(model_data)
        model_token_fig = px.bar(
            model_df, 
            x="Model", 
            y=["Input Tokens", "Output Tokens"], 
            title="Token Usage by Model",
            barmode="group",
            color_discrete_sequence=["#3366cc", "#dc3912"]
        )
        model_token_fig.update_layout(
            xaxis_title="Model",
            yaxis_title="Token Count",
            legend_title="Token Type"
        )
        
        # Model cost bar chart
        model_cost_fig = px.bar(
            model_df,
            x="Model",
            y="Cost",
            title="Estimated Cost by Model",
            color="Model"
        )
        model_cost_fig.update_layout(
            xaxis_title="Model",
            yaxis_title="Cost (USD)",
            yaxis_tickformat="$,.2f"
        )
        
        # Template usage pie chart if template data exists
        template_fig = None
        if summary.get('template_usage'):
            template_data = []
            for template, usage in summary['template_usage'].items():
                if template:  # Skip None templates
                    template_data.append({
                        "Template": template,
                        "Tokens": usage.get('total_tokens', 0),
                        "Requests": usage.get('request_count', 0)
                    })
            
            if template_data:
                template_df = pd.DataFrame(template_data)
                template_fig = px.pie(
                    template_df,
                    values="Tokens",
                    names="Template",
                    title="Token Usage by Template",
                    hole=0.4
                )
                template_fig.update_traces(textposition='inside', textinfo='percent+label')
        
        # Create fallback rate gauge
        fallback_rate = summary.get('fallback_rate', 0) * 100
        fallback_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=fallback_rate,
            title={'text': "Fallback Rate (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 5], 'color': "green"},
                    {'range': [5, 15], 'color': "yellow"},
                    {'range': [15, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 15
                }
            }
        ))
        
        # Daily usage line chart
        daily_fig = None
        if summary.get('daily_usage'):
            daily_df = pd.DataFrame(summary['daily_usage'])
            if not daily_df.empty:
                daily_fig = px.line(
                    daily_df, 
                    x="date", 
                    y="tokens",
                    title="Daily Token Usage",
                    markers=True
                )
                daily_fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Total Tokens"
                )
        
        return usage_text, model_token_fig, model_cost_fig, template_fig, fallback_fig, daily_fig
    
    # Create the dashboard interface
    with gr.Blocks(title="Token Usage Dashboard") as dashboard:
        gr.Markdown("# Token Usage Analytics Dashboard")
        gr.Markdown("This dashboard provides analytics on token usage across different models and templates.")
        
        with gr.Row():
            with gr.Column(scale=1):
                time_period = gr.Dropdown(
                    label="Time Period", 
                    choices=[("7 Days", "7"), ("30 Days", "30"), ("90 Days", "90"), ("365 Days", "365")], 
                    value="30"
                )
                include_tests = gr.Checkbox(label="Include Test Runs", value=False)
                refresh_btn = gr.Button("Refresh Data")
            
            with gr.Column(scale=3):
                usage_summary = gr.Markdown("Loading data...")
        
        # Charts and visualizations
        with gr.Row():
            model_token_chart = gr.Plot(label="Token Usage by Model")
            model_cost_chart = gr.Plot(label="Cost by Model")
            
        with gr.Row():
            template_chart = gr.Plot(label="Token Usage by Template")
            fallback_gauge = gr.Plot(label="Fallback Rate")
        
        with gr.Row():
            daily_usage_chart = gr.Plot(label="Daily Token Usage")
        
        # Event handlers
        refresh_btn.click(
            refresh_data, 
            inputs=[time_period, include_tests], 
            outputs=[usage_summary, model_token_chart, model_cost_chart, template_chart, fallback_gauge, daily_usage_chart]
        )
        
        # Initial load - automatically reload every time the component is loaded
        dashboard.load(
            refresh_data,
            inputs=[time_period, include_tests],
            outputs=[usage_summary, model_token_chart, model_cost_chart, template_chart, fallback_gauge, daily_usage_chart]
        )
        
    return dashboard 