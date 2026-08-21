from pydantic import BaseModel, Field
from typing import List, Optional

class InvoiceItem(BaseModel):
    item_name: str = Field(description="Name or description of the product or service")
    hsn_code: Optional[str] = Field(default="", description="HSN or SAC code if present")
    quantity: float = Field(default=1.0, description="Quantity billed")
    unit_price: float = Field(description="Unit price before tax")
    tax_rate: float = Field(description="GST rate percentage, e.g., 18 for 18%")
    taxable_amount: float = Field(description="Total taxable amount for this line item")

class InvoiceData(BaseModel):
    vendor_name: str = Field(description="Supplier or company name billing the invoice")
    vendor_gstin: Optional[str] = Field(default="", description="15-digit GST number of vendor")
    invoice_number: str = Field(description="Unique invoice/bill reference number")
    invoice_date: str = Field(description="Invoice date strictly in YYYYMMDD format")
    items: List[InvoiceItem]
    subtotal: float = Field(description="Sum of all taxable values before tax")
    cgst: float = Field(default=0.0, description="Central GST amount")
    sgst: float = Field(default=0.0, description="State GST amount")
    igst: float = Field(default=0.0, description="Integrated GST amount")
    total_amount: float = Field(description="Final grand total payable")