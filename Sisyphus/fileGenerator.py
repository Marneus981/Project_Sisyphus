from docxtpl import DocxTemplate
import subprocess
import os
import time

def context_cleaner(context):
    """
    Recursively clean the context dictionary for docxtpl compatibility.
    - Ensures all keys are strings.
    - Converts non-serializable values to strings.
    - Removes keys with None values.
    """
    if isinstance(context, dict):
        cleaned = {}
        for k, v in context.items():
            key = str(k)
            if v is None:
                continue
            elif isinstance(v, (str, int, float, bool)):
                cleaned[key] = v
            elif isinstance(v, (list, tuple)):
                cleaned[key] = [context_cleaner(item) for item in v]
            elif isinstance(v, dict):
                cleaned[key] = context_cleaner(v)
            else:
                cleaned[key] = str(v)
        return cleaned
    else:
        return context

def odt_to_pdf(out_dir, odt_path):
    """
    Converts an ODT file to PDF using LibreOffice in headless mode.
    
    :param out_dir: Directory where the output PDF will be saved.
    :param odt_path: Path to the ODT file to be converted.
    """
    if not os.path.exists(odt_path):
        raise FileNotFoundError(f"ODT file does not exist at {odt_path}")
    
    try:
        result = subprocess.run([
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", out_dir,
            odt_path
        ], check=True, capture_output=True, text=True)
        print("LibreOffice output:")
        print(result.stdout)
        print(result.stderr)
    except Exception as e:
        print(f"An error occurred while converting ODT to PDF: {e}")
def docx_to_odt(out_dir, docx_path):
    """
    Converts a DOCX file to ODT using LibreOffice in headless mode.
    
    :param out_dir: Directory where the output ODT will be saved.
    :param docx_path: Path to the DOCX file to be converted.
    """
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"DOCX file does not exist at {docx_path}")
    
    try:
        result = subprocess.run([
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            "--headless",
            "--convert-to", "odt",
            "--outdir", out_dir,
            docx_path
        ], check=True, capture_output=True, text=True)
        print("LibreOffice output:")
        print(result.stdout)
        print(result.stderr)
    except Exception as e:
        print(f"An error occurred while converting DOCX to ODT: {e}")

def template_to_docx(template_path, context, output_path):
    """
    Generates a DOCX document from a template and context.
    
    :param template_path: Path to the DOCX template file.
    :param context: Dictionary containing the context for rendering the template.
    :param output_path: Path where the generated DOCX file will be saved.
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file does not exist at {template_path}")
    
    try:
        doc = DocxTemplate(template_path)
        doc.render(context)
        doc.save(output_path)
        print(f"Document generated successfully at {output_path}")
    except Exception as e:
        print(f"An error occurred while generating the document: {e}")

def generate_docx(template_path, context, output_path):
    nu_context = context_cleaner(context)
    template_to_docx(template_path, nu_context, output_path)
    time.sleep(1)  # Ensure the file is saved before conversion
        #Convert docx to odt
        # odt_path = output_path.replace('.docx', '.odt')
        # docx_to_odt(os.path.dirname(output_path), output_path)
        # time.sleep(1)  # Ensure the file is saved before conversion
        # #Convert odt to pdf
        # pdf_path = output_path.replace('.docx', '.pdf')
        # odt_to_pdf(os.path.dirname(output_path), odt_path)
        # time.sleep(1)  # Ensure the file is saved before conversion
    print(f"DOCX generated successfully at {output_path}")

def convert_docx_to_pdf(docx_path):
    docx_to_odt(os.path.dirname(docx_path), docx_path)
    time.sleep(1)  # Ensure the file is saved before conversion
    odt_path = docx_path.replace('.docx', '.odt')
    odt_to_pdf(os.path.dirname(docx_path), odt_path)
    time.sleep(1)  # Ensure the file is saved before conversion
    print(f"PDF generated successfully at {odt_path.replace('.odt', '.pdf')}")