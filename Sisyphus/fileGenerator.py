from docxtpl import DocxTemplate
import subprocess
import os

def generate_docx(template_path, context, output_path):
    """
    Generates a DOCX file from a template and context.

    :param template_path: Path to the DOCX template file.
    :param context: Dictionary containing the context for rendering the template.
    :param output_path: Path where the generated DOCX file will be saved.
    """
    try:
        # Load the template
        doc = DocxTemplate(template_path)
        
        # Render the template with the provided context
        doc.render(context)
        
        # Save the generated document
        doc.save(output_path)
        print(f"Document generated successfully at {output_path}")
    
    except Exception as e:
        print(f"An error occurred while generating the document: {e}")

def convert_docx_to_pdf(docx_path, pdf_path):
    # Get the output directory from the output_path

    # Call LibreOffice's soffice to convert DOCX to PDF
    try:
        subprocess.run([
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", pdf_path,
            docx_path
        ], check=True)
        print(f"PDF generated at {pdf_path}")
    except Exception as e:
        print(f"Error converting DOCX to PDF: {e}")