import gradio as gr
from app.components.token_dashboard import create_token_dashboard

with gr.Blocks() as demo:
    create_token_dashboard()
    
if __name__ == "__main__":
    demo.launch() 