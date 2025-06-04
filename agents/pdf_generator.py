from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

lines = [
    "Invoice #: INV-2025-0789",
    "Date: 2025-06-01",
    "Customer ID: CUST-00987",
    "Customer Name: Rahul Sharma",
    "",
    "Items:",
    "------------------------------------------------------------",
    "| Item              | Qty | Unit Price (INR) | Total (INR) |",
    "|-------------------|-----|------------------|-------------|",
    "| Laptop Stand      | 2   | 1,000.00         | 2,000.00    |",
    "| Wireless Mouse    | 2   | 500.00           | 1,000.00    |",
    "| External SSD      | 1   | 4,500.00         | 4,500.00    |",
    "| HDMI Cable        | 5   | 200.00           | 1,000.00    |",
    "| USB Hub           | 2   | 500.00           | 1,000.00    |",
    "------------------------------------------------------------",
    "Total Amount: INR 9,500.00",
    "Payment Status: Paid",
    "Currency: INR",
    "",
    "Shipping Address:",
    "Rahul Sharma",
    "123 Tech Street",
    "Bangalore, Karnataka 560001",
    "India"
]

for line in lines:
    pdf.cell(0, 10, txt=line, ln=True)

pdf.output("sample_invoice.pdf")

