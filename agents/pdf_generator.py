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
    "| Laptop Stand      | 2   | 1,250.00         | 2,500.00    |",
    "| Wireless Mouse    | 3   | 600.00           | 1,800.00    |",
    "| External SSD      | 1   | 7,500.00         | 7,500.00    |",
    "| HDMI Cable        | 5   | 215.00           | 1,075.00    |",
    "| USB Hub           | 2   | 1,500.00         | 3,000.00    |",
    "------------------------------------------------------------",
    "Total Amount: INR 15,875.00",
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
