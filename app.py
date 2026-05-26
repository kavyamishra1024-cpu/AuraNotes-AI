from flask import Flask, render_template, request, send_from_directory, send_file
import os
import pdfplumber
from fpdf import FPDF
import re
import io
import random

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# EXTRACT TEXT FROM PDF
# =========================

def extract_text(file_path):

    text = ""

    if file_path.endswith(".pdf"):

        with pdfplumber.open(file_path) as pdf:

            for page in pdf.pages:

                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

    return text.strip()

# =========================
# ESTIMATED REVISION TIME
# =========================

def calculate_revision_time(text):

    words = len(text.split())

    mins = max(1, round(words / 200))

    return mins

# =========================
# SUMMARY GENERATOR
# =========================

def generate_summary(notes_text, style="exam"):

    if not notes_text:
        return "No notes found."

    sentences = notes_text.split(".")

    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    if style == "revision":

        selected = sentences[:5]

        return "\n".join([f"⚡ {s}" for s in selected])

    elif style == "beginner":

        selected = sentences[:6]

        return "\n".join([f"📘 {s}" for s in selected])

    elif style == "exam":

        selected = sentences[:8]

        return "\n".join([f"📝 {s}" for s in selected])

    else:

        return "\n".join([f"• {s}" for s in sentences[:6]])

# =========================
# QUIZ GENERATOR
# =========================

def generate_quiz(notes_text):

    lines = notes_text.split("\n")

    lines = [l.strip() for l in lines if len(l.strip()) > 25]

    questions = []

    for i, line in enumerate(lines[:5]):

        q = f"Q{i+1}. Explain: {line[:60]}?"
        a = f"Answer: {line}"

        questions.append(q)
        questions.append(a)

    return "\n\n".join(questions)

# =========================
# VIVA GENERATOR
# =========================

def generate_viva(notes_text):

    keywords = notes_text.split()

    viva = []

    for i in range(5):

        word = random.choice(keywords)

        viva.append(f"Q{i+1}. What do you understand about '{word}'?")
        viva.append(f"Answer: '{word}' is an important concept from the notes.")

    return "\n\n".join(viva)

# =========================
# FLASHCARDS
# =========================

# =========================
# SMART FLASHCARDS
# =========================

# =========================
# FLASHCARDS
# =========================

# =========================
# SMART FLASHCARDS
# =========================

# =========================
# FLASHCARDS
# =========================

def generate_flashcards(notes_text):

    sentences = notes_text.split(".")

    sentences = [
        s.strip()
        for s in sentences
        if len(s.strip()) > 40
    ]

    flashcards = []

    for sentence in sentences[:6]:

        words = sentence.split()

        # Short keyword/topic
        topic = " ".join(words[:2])

        # Small explanation
        explanation = " ".join(words[:15]) + "..."

        flashcards.append(f"Front: {topic}")
        flashcards.append(f"Back: {explanation}")

    return "\n\n".join(flashcards)
# =========================
# PDF GENERATION
# =========================

def create_pdf(filename, summary, quiz="", viva="", flashcards=""):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Arial", "B", 18)

    pdf.cell(0, 10, "AuraNotes AI", ln=True, align="C")

    pdf.ln(10)

    pdf.set_font("Arial", "", 11)

    clean_summary = re.sub(r'[^\x00-\x7F]+', '', summary)

    pdf.multi_cell(0, 8, clean_summary)

    if quiz:

        pdf.ln(8)

        pdf.set_font("Arial", "B", 14)

        pdf.cell(0, 10, "Quiz", ln=True)

        pdf.set_font("Arial", "", 11)

        clean_quiz = re.sub(r'[^\x00-\x7F]+', '', quiz)

        pdf.multi_cell(0, 8, clean_quiz)

    if viva:

        pdf.ln(8)

        pdf.set_font("Arial", "B", 14)

        pdf.cell(0, 10, "Viva Questions", ln=True)

        pdf.set_font("Arial", "", 11)

        clean_viva = re.sub(r'[^\x00-\x7F]+', '', viva)

        pdf.multi_cell(0, 8, clean_viva)

    if flashcards:

        pdf.ln(8)

        pdf.set_font("Arial", "B", 14)

        pdf.cell(0, 10, "Flashcards", ln=True)

        pdf.set_font("Arial", "", 11)

        clean_flash = re.sub(r'[^\x00-\x7F]+', '', flashcards)

        pdf.multi_cell(0, 8, clean_flash)

    return pdf.output(dest="S").encode("latin-1")

# =========================
# FILE ROUTE
# =========================

@app.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# =========================
# DOWNLOAD PDF
# =========================

@app.route("/download-pdf", methods=["POST"])
def download_pdf():

    filename = request.form.get("filename", "")

    summary = request.form.get("summary", "")

    quiz = request.form.get("quiz", "")

    viva = request.form.get("viva", "")

    flashcards = request.form.get("flashcards", "")

    pdf_bytes = create_pdf(
        filename,
        summary,
        quiz,
        viva,
        flashcards
    )

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="AuraNotesAI.pdf"
    )

# =========================
# HOME ROUTE
# =========================

@app.route("/", methods=["GET", "POST"])
def home():

    filename = None
    extracted_text = None
    summary = None
    quiz = None
    viva = None
    flashcards = None
    revision_time = None

    style = request.form.get("style", "exam")

    action = request.form.get("action")

    file = request.files.get("file")

    if file and file.filename != "":

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            file.filename
        )

        file.save(filepath)

        filename = file.filename

        extracted_text = extract_text(filepath)

    if action in ["summarize", "quiz", "viva", "flashcards"]:

        filename = request.form.get("filename")

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        extracted_text = extract_text(filepath)

        revision_time = calculate_revision_time(extracted_text)

        if action == "summarize":

            summary = generate_summary(
                extracted_text,
                style
            )

        elif action == "quiz":

            quiz = generate_quiz(extracted_text)

        elif action == "viva":

            viva = generate_viva(extracted_text)

        elif action == "flashcards":

            flashcards = generate_flashcards(extracted_text)

    return render_template(
        "index.html",
        filename=filename,
        extracted_text=extracted_text,
        summary=summary,
        quiz=quiz,
        viva=viva,
        flashcards=flashcards,
        revision_time=revision_time,
        style=style
    )

# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    app.run(debug=True)