from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

# Directory to save PDFs
output_dir = "pdf_samples"
os.makedirs(output_dir, exist_ok=True)

# Number of files to create
num_files = 5000

for i in range(1, num_files + 1):
    file_name = f"file_{i:04d}.pdf"  # file_0001.pdf to file_5000.pdf
    file_path = os.path.join(output_dir, file_name)
    
    c = canvas.Canvas(file_path, pagesize=A4)
    c.setFont("Helvetica", 12)
    c.drawString(100, 800, f"This is PDF file number {i}")
    c.save()

print(f"Generated {num_files} PDF files in '{output_dir}' folder.")
