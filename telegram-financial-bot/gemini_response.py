from fpdf import FPDF
import mimetypes
import os
from pathlib import Path
from textwrap import dedent
import tempfile
import gradio as gr
from dotenv import load_dotenv
from google import genai
from google.genai import types as T
import pandas as pd

# -----------------------------------------------------------------------------------------------------
# Load environment variables containing API keys and model details
load_dotenv(verbose=True)
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
MODEL_ID = os.environ.get("MODEL_ID")

# Initialize the Gemini AI client with the Google API key
client = genai.Client(api_key=GOOGLE_API_KEY)

# -----------------------------------------------------------------------------------------------------
# Create a new chat session with Gemini AI
my_chat = client.chats.create(
    model=MODEL_ID,
    config={
        "system_instruction": dedent("""
        You are an helpful polite Financial AI Assitant. Answer user queries with below guidelines.
        Guidelines:
         - Only respond to finance-related questions.
         - Only handle files that are PDF, CSV, and Image formats.
         - 
        """),
        "temperature": 0.5,
        "max_output_tokens": 1000,
        "top_p": 0.8,
        "top_k": 40,
    },
    history=[] # Chat history placeholder
)


def get_mime_type(file_path):
    """
    Determine the MIME type of a given file.
    Treat CSV files as plain text for compatibility.
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    if file_path.endswith(".csv"):
        mime_type = "text/plain"  # Treat CSV as text
    return mime_type


def get_file_bytes(file_path):
    """
    Extract file content appropriately for sending to Gemini AI:
    - Convert CSVs to string representation.
    - Return binary content wrapped with appropriate MIME type for other files.
    """
    mime_type = get_mime_type(file_path)

    if mime_type == "text/csv":
        df = pd.read_csv(file_path)  
        return df.to_string()  # Convert CSV to readable string format

    with open(file_path, "rb") as file:
        file_bytes = file.read()

    return T.Part.from_bytes(data=file_bytes, mime_type=mime_type) if mime_type else None

# -----------------------------------------------------------------------------------------------------
# Global variable to store latest PDF path
latest_pdf_path = None

def get_latest_pdf_path():
    """Get the latest generated PDF path."""
    global latest_pdf_path
    return latest_pdf_path

def create_pdf_output(text, filename="FinGPT_Response.pdf"):
    """
    Generate a PDF file containing the chatbot's response text.
    Saves the file temporarily and returns the file path.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(190, 10, text)

    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, filename)

    pdf.output(pdf_path)
    return pdf_path  # Returns path for download


# -----------------------------------------------------------------------------------------------------
def gemini_response(gr_message, history):
    """
    Main function to process user input and files, send to Gemini AI chatbot,
    generate response, and produce a downloadable PDF of the answer.
    """

    global latest_pdf_path  

    # Extract the text and files from the input
    text_message = gr_message.get("text", "")
    file_list = gr_message.get("files", [])

    # Return last generated PDF 
    if text_message.strip().lower() == "generate pdf":
        if latest_pdf_path:
            return {"text": "Here is your PDF", "files": [latest_pdf_path]}
        else:
            return {"text": "No PDF has been generated yet."}
    
    # Prepare attachments from files for Gemini input
    message_attachments = []
    for f in file_list:
        file_path = Path(f)
        if file_path.exists():
            file_data = get_file_bytes(file_path=f)
            if file_data is not None:
                message_attachments.append(file_data)

    # Combine text and attachments into message for Gemini chatbot
    message = [str(text_message)] + message_attachments

    # Send message and receive response from Gemini AI
    response = my_chat.send_message(message)
    response_text = response.text.strip()

    # Generate PDF from the chatbot's response and store path globally
    latest_pdf_path = create_pdf_output(response_text)

    # Otherwise return just the text
    return response.text

