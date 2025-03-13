import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from Project.models import LedgerEntry
from Project import db

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load Gemini Pro Vision model
model = genai.GenerativeModel('gemini-1.5-flash')


def input_image_details(uploaded_file):
    """Converts uploaded invoice image into a format Gemini API can process."""
    if uploaded_file:
        bytes_data = uploaded_file.read()
        return [{"mime_type": uploaded_file.mimetype, "data": bytes_data}]
    else:
        raise FileNotFoundError("No file uploaded")


def get_gemini_response(image_parts):
    """Sends invoice image to Gemini API and retrieves structured invoice data."""
    user_prompt = '''You are an expert in processing invoices. Extract the following key information from the provided invoice in a structured format. If any information is missing or unclear, return "Not Specified."

1. **Sender Information**:
   - Name:
   - Address:

2. **Receiver Information**:
   - Name:
   - Billing Address:
   - Shipping Address (if different from billing address):

3. **Invoice Details**:
   - Invoice Number:
   - Invoice Date:
   - Due Date:
   - Purchase Order (P.O.) Number (if available):
   - Reference Number (if applicable):  # Added for other invoice types

4. **Line Items**:
   - For each line item, extract:
     - Quantity:
     - Description:
     - Unit Price:
     - Total Amount:
     - Tax Amount (if applicable):  # Added to handle tax-based invoices
     - Discount (if applicable):  # Added to handle credit memos

5. **Totals**:
   - Subtotal:
   - Tax Amount (if applicable):
   - Discount (if applicable):  # Added for discounts in credit memos
   - Total Amount: (Sum the sub-amounts or amounts of Line items to Calculate the Total Amount if Total not sperately mention on Invoice, since this variable can not be null)

6. **Payment Terms**:
   - Payment Due Date (if specified):
   - Payable To (if specified):
   - Payment Status (Paid or Unpaid By Checking Due Date or Stamp)

7. **Invoice Type**:
   Classify the invoice into one of the following categories based on its context:

  "Service Invoice" → If the invoice is issued for providing services, such as consulting, freelancing, professional work, or any non-tangible service.
  "Stock Purchase Invoice" → If the invoice relates to buying common stocks or financial investments, usually from a brokerage or financial institution.
  "Real Estate Purchase Invoice" → If the invoice is for purchasing land, buildings, or property, issued by a real estate seller or broker.
  "Equipment Purchase Invoice" → If the invoice involves the purchase of machinery, office equipment, or industrial tools, from a supplier.
  "Raw Materials Purchase Invoice" → If the invoice is for buying raw materials or components used in production or manufacturing.
  "Salary Invoice" → If the invoice represents salary or wages paid to employees, including payroll details, deductions, and net pay.

   Classification Rules:
  Check the sender’s role:
   
  If the sender is a business, contractor, or freelancer providing services, classify it as Service Invoice.
  If the sender is a brokerage or financial institution, classify it as Stock Purchase Invoice.
  If the sender is a real estate company or property seller, classify it as Real Estate Purchase Invoice.
  If the sender is a vendor supplying office or industrial equipment, classify it as Equipment Purchase Invoice.
  If the sender is a supplier of raw materials, classify it as Raw Materials Purchase Invoice.
  If the sender is an employer paying an employee, classify it as Salary Invoice.

Return the extracted information in **strict JSON format** for easy integration into systems.'''

    try:
        response = model.generate_content(
            ["Processing Invoice...", image_parts[0], user_prompt])

        raw_response = response.text.strip()
        print("\n🔍 RAW RESPONSE FROM GEMINI API:")
        print(raw_response)  # Debugging log

        # Extract JSON safely
        json_start = raw_response.find('{')
        json_end = raw_response.rfind('}') + 1
        json_data = raw_response[json_start:json_end]

        parsed_data = json.loads(json_data)  # Convert string to JSON
        return parsed_data

    except json.JSONDecodeError:
        print("\n❌ Invalid JSON Response from Gemini API")
        raise ValueError(
            "Invalid response from Gemini API. Could not parse JSON.")

    except Exception as e:
        print(f"\n❌ Unexpected Error in API Response: {str(e)}")
        raise ValueError("Error retrieving response from Gemini API.")


def retrieve_financial_data():
    """
    Retrieves total revenue, expenses, and net profit from the database.
    """
    revenues = db.session.query(LedgerEntry).filter(
        LedgerEntry.account_name.like('%Revenue%')).all()
    expenses = db.session.query(LedgerEntry).filter(
        LedgerEntry.account_name.like('%Expense%')).all()

    total_revenue = sum(entry.credit for entry in revenues)
    total_expense = sum(entry.debit for entry in expenses)
    net_profit = total_revenue - total_expense

    return {
        "total_revenue": total_revenue,
        "total_expense": total_expense,
        "net_profit": net_profit
    }


def generate_financial_insight():
    """
    Uses Google's Gemini AI to analyze revenue, expenses, and profit.
    """
    financial_data = retrieve_financial_data()

    if not financial_data:
        return "No financial data found."

    prompt = f"""
    You are a professional financial analyst. Based on the following data, generate a concise financial summary:
    
    **Period:** (Specify the reporting period)
    **Total Revenue:** ${financial_data['total_revenue']}
    **Total Expenses:** ${financial_data['total_expense']}
    **Net Profit (Loss):** ${financial_data['net_profit']}
    
    Provide a summary with key insights and actionable recommendations.
    """

    response = model.generate_content(prompt)

    return response.text if response and response.text else "No insights generated."
