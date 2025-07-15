from docxtpl import DocxTemplate

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