from jinja2 import Template
from schemas import InvoiceData

def generate_tally_xml(invoice: InvoiceData, company_name: str = "My Company") -> str:
    """
    Loads the Tally XML template and renders it dynamically with the extracted invoice data.
    """
    try:
        with open("tally_template.xml", "r", encoding="utf-8") as f:
            template_content = f.read()
            
        jinja_template = Template(template_content)
        rendered_xml = jinja_template.render(invoice=invoice, company_name=company_name)
        return rendered_xml
    except Exception as e:
        raise RuntimeError(f"Failed to render Tally XML template: {str(e)}")