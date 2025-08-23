
import gradio as gr
import PyPDF2
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from textwrap import wrap

# 1. Configure Gemini API
genai.configure(api_key="AIzaSyBD2NWu31Oj4IXI83AImrVmuKRb8c5uG7c")
model = genai.GenerativeModel("gemini-1.5-flash")

# 2. Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# 3. Function to generate quiz
def generate_quiz(pdf_file, num_questions=5):
    if pdf_file is None:
        return "Please upload a PDF first.", None, None
    
    text = extract_text_from_pdf(pdf_file)
    
    prompt = f"""
    You are a quiz generator AI. Create {num_questions} mixed quiz questions 
    (MCQs and True/False) from the following text:

    {text[:6000]}  

    Format strictly like this:

    Q1. Question text here
    A) Option 1
    B) Option 2
    C) Option 3
    D) Option 4
    Answer: C) Option 3

    OR (for true/false)

    Q2. (True/False) Statement here
    Answer: True
    """
    
    response = model.generate_content(prompt)
    quiz_text = response.text.strip()
    
    # Save as TXT
    txt_filename = "quiz_output.txt"
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write(quiz_text)
    
    # Save as PDF with proper formatting
    pdf_filename = "quiz_output.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter
    margin = 50
    y = height - 50

    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y, "AI-Generated Quiz")
    y -= 40
    c.setFont("Helvetica", 12)

    for line in quiz_text.split("\n"):
        wrapped_lines = wrap(line, width=90)
        for wline in wrapped_lines:
            if y < 50:
                c.showPage()
                y = height - 50
                # Re-add title on new page
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(width / 2, y, "AI-Generated Quiz (contd.)")
                y -= 40
                c.setFont("Helvetica", 12)
            c.drawString(margin, y, wline)
            y -= 18  # more spacing for readability
        if line.strip() == "":
            y -= 10  # extra spacing between questions

    c.save()
    
    return quiz_text, txt_filename, pdf_filename

# 4. Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## 📘 Quiz Generator from PDF (Gemini + Gradio)")
    
    with gr.Row():
        pdf_input = gr.File(label="Upload PDF", type="filepath")
        num_q = gr.Slider(3, 30, value=5, step=1, label="Number of Questions")
    
    output = gr.Textbox(label="Generated Quiz", lines=20)
    file_txt = gr.File(label="Download Quiz (TXT)")
    file_pdf = gr.File(label="Download Quiz (PDF)")
    generate_btn = gr.Button("Generate Quiz")
    
    generate_btn.click(
        fn=generate_quiz,
        inputs=[pdf_input, num_q],
        outputs=[output, file_txt, file_pdf]
    )

# Launch with public shareable link
demo.launch(share=True)
