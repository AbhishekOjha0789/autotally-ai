from schemas import InvoiceData

def validate_invoice_math(invoice: InvoiceData) -> tuple[bool, str]:
    """
    Validates that Subtotal + CGST + SGST + IGST = Total Amount.
    Allows a strict 1-rupee rounding tolerance.
    """
    calculated_total = invoice.subtotal + invoice.cgst + invoice.sgst + invoice.igst
    difference = abs(calculated_total - invoice.total_amount)
    
    if difference > 1.0:
        return False, (
            f"Math mismatch! Subtotal ({invoice.subtotal}) + Taxes "
            f"({invoice.cgst + invoice.sgst + invoice.igst}) = {calculated_total}, "
            f"but total is stated as {invoice.total_amount}."
        )
    
    return True, "Math validation passed successfully."