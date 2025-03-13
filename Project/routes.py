from flask import Flask, render_template, redirect, url_for, flash, request, json
from datetime import datetime
from Project.forms import InvoiceUploadForm
from Project.models import Company, Invoice, LineItem, db, LedgerEntry
from flask_login import login_required, current_user
from Project import app
from flask import render_template, redirect, url_for, flash, request, jsonify
from Project.models import Company, Invoice
from Project.forms import RegisterForm, LoginForm
from Project import db
from flask_login import login_user, logout_user
from Project.Invoice_Processor import input_image_details, get_gemini_response, generate_financial_insight


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/register', methods=['POST', 'GET'])
def register_company():
    form = RegisterForm()
    if form.validate_on_submit():
        new_company = Company(
            company_name=form.company_name.data,
            Email=form.Email.data,
            Password=form.password1.data
        )
        db.session.add(new_company)
        db.session.commit()
        login_user(new_company)
        flash(
            f"Account created successfully! You are now logged in as {new_company.company_name}", category='success')
        return redirect(url_for('upload_invoice'))
    if form.errors != {}:  # If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(
                f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = Company.query.filter_by(Email=form.Email.data).first()

        if attempted_user:
            if attempted_user.check_password_correction(attempted_password=form.password.data):
                login_user(attempted_user)
                flash(
                    f'Success! You are logged in as: {attempted_user.company_name}', category='success')
                return redirect(url_for('upload_invoice'))
            else:
                flash('Incorrect password. Please try again.', category='danger')
        else:
            flash(
                'No account found with that email. Please check and try again.', category='danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home"))


@app.route('/upload_invoice', methods=['GET', 'POST'])
@login_required
def upload_invoice():
    form = InvoiceUploadForm()

    if form.validate_on_submit():
        uploaded_file = form.invoice_file.data
        if uploaded_file:
            try:
                # Process invoice image and extract data
                image_data = input_image_details(uploaded_file)
                extracted_data = get_gemini_response(image_data)

                # Ensure response is a dictionary
                if not isinstance(extracted_data, dict):
                    raise ValueError(
                        "Unexpected response format from Gemini API.")

                # def parse_date(date_str):
                #     try:
                #         return datetime.strptime(date_str, "%d/%m/%Y").date()
                #     except ValueError:
                #         return None  # Handle invalid date format

                # Create new invoice record
                new_invoice = Invoice(
                    company_id=current_user.company_id,
                    sender=extracted_data["Sender Information"].get(
                        "Name", "Not Specified"),
                    receiver=extracted_data["Receiver Information"].get(
                        "Name", "Not Specified"),
                    invoice_number=extracted_data["Invoice Details"].get(
                        "Invoice Number", "Not Specified"),
                    invoice_date=extracted_data["Invoice Details"].get(
                        "Invoice Date", "Not Specified"),
                    due_date=extracted_data["Invoice Details"].get(
                        "Due Date", "Not Specified"),
                    total_amount=extracted_data["Totals"].get(
                        "Total Amount", 0.0),
                    invoice_type=extracted_data.get("Invoice Type"),
                    status=extracted_data["Payment Terms"].get(
                        "Payment Status", "Unpaid")
                )
                db.session.add(new_invoice)
                db.session.commit()

                # Save line items
                for item in extracted_data.get("Line Items", []):
                    new_line_item = LineItem(
                        invoice_id=new_invoice.invoice_id,
                        description=item.get("Description", "Not Specified"),
                        quantity=item.get("Quantity", 0),
                        unit_price=item.get("Unit Price", 0.0),
                        total_amount=item.get("Total Amount", 0.0)
                    )
                    db.session.add(new_line_item)

                db.session.commit()

                # Record Ledger Entries
                create_ledger_entries(new_invoice)

                flash(
                    "Invoice uploaded and ledger updated successfully! Click below to View the Ledger", "success")
                return redirect(url_for('upload_invoice'))

            except ValueError as e:
                flash(f"Error processing invoice: {str(e)}", "danger")
            except Exception as e:
                flash(f"Unexpected error: {str(e)}", "danger")
        else:
            flash("No file uploaded. Please upload an invoice.", "danger")

    return render_template('upload_invoice.html', form=form)


def create_ledger_entries(invoice):
    # Common Accounts
    cash = "Cash"
    accounts_receivable = "Accounts Receivable"
    accounts_payable = "Accounts Payable"
    sales_revenue = "Service Revenue"
    stock_purchase = "Common Stocks"
    real_estate_purchase = "Real Estate Purchase"
    equipment_purchase = "Equipment Expense"
    raw_materials_purchase = "Raw Materials Expense"
    salary_expense = "Salary Expense"
    tax_payable = "Tax Payable"

    # Determine whether to use cash or A/P, A/R
    if invoice.status == "Paid":
        payment_account = cash  # Paid invoices use cash
    else:
        payment_account = (
            accounts_receivable if invoice.invoice_type == "Service Invoice" else accounts_payable
        )  # Unpaid invoices use A/P or A/R

    ledger_entries = []

    if invoice.invoice_type == "Service Invoice":
        # Customer owes money or paid for services (Receivable or Cash)
        ledger_entries.append(LedgerEntry(
            company_id=invoice.company_id,
            invoice_id=invoice.invoice_id,
            account_name=payment_account,
            debit=invoice.total_amount,
            credit=0.00,
            entry_date=invoice.invoice_date
        ))

        # Service Revenue earned
        ledger_entries.append(LedgerEntry(
            company_id=invoice.company_id,
            invoice_id=invoice.invoice_id,
            account_name=sales_revenue,
            debit=0.00,
            credit=invoice.total_amount,
            entry_date=invoice.invoice_date
        ))

    elif invoice.invoice_type == "Stock Purchase Invoice":

        # Investment in stocks
        ledger_entries.append(LedgerEntry(
            company_id=invoice.company_id,
            invoice_id=invoice.invoice_id,
            account_name=stock_purchase,
            debit=invoice.total_amount,
            credit=0.00,
            entry_date=invoice.invoice_date
        ))

        # Business pays or owes for stock purchase
        ledger_entries.append(LedgerEntry(
            company_id=invoice.company_id,
            invoice_id=invoice.invoice_id,
            account_name=payment_account,
            debit=0.00,
            credit=invoice.total_amount,
            entry_date=invoice.invoice_date
        ))

    elif invoice.invoice_type == "Real Estate Purchase Invoice":

        # Asset recorded as Real Estate Purchase
        ledger_entries.append(LedgerEntry(
            company_id=invoice.company_id,
            invoice_id=invoice.invoice_id,
            account_name=real_estate_purchase,
            debit=invoice.total_amount,
            credit=0.00,
            entry_date=invoice.invoice_date
        ))

        # Business pays or owes for property purchase
        ledger_entries.append(LedgerEntry(
            company_id=invoice.company_id,
            invoice_id=invoice.invoice_id,
            account_name=payment_account,
            debit=0.00,
            credit=invoice.total_amount,
            entry_date=invoice.invoice_date
        ))

    elif invoice.invoice_type == "Equipment Purchase Invoice":

        # Asset recorded as Equipment Purchase
        ledger_entries.append(LedgerEntry(
            company_id=invoice.company_id,
            invoice_id=invoice.invoice_id,
            account_name=equipment_purchase,
            debit=invoice.total_amount,
            credit=0.00,
            entry_date=invoice.invoice_date
        ))

        # Business pays or owes for equipment
        ledger_entries.append(LedgerEntry(
            company_id=invoice.company_id,
            invoice_id=invoice.invoice_id,
            account_name=payment_account,
            debit=0.00,
            credit=invoice.total_amount,
            entry_date=invoice.invoice_date
        ))

    elif invoice.invoice_type == "Raw Materials Purchase Invoice":

        # Expense recorded as Raw Materials Purchase
        ledger_entries.append(LedgerEntry(
            company_id=invoice.company_id,
            invoice_id=invoice.invoice_id,
            account_name=raw_materials_purchase,
            debit=invoice.total_amount,
            credit=0.00,
            entry_date=invoice.invoice_date
        ))

        # Business pays or owes for raw materials
        ledger_entries.append(LedgerEntry(
            company_id=invoice.company_id,
            invoice_id=invoice.invoice_id,
            account_name=payment_account,
            debit=0.00,
            credit=invoice.total_amount,
            entry_date=invoice.invoice_date
        ))

    elif invoice.invoice_type == "Salary Invoice":
        # Business pays salary expense

        # Expense recorded as Salary Expense
        ledger_entries.append(LedgerEntry(
            company_id=invoice.company_id,
            invoice_id=invoice.invoice_id,
            account_name=salary_expense,
            debit=invoice.total_amount,
            credit=0.00,
            entry_date=invoice.invoice_date
        ))

        ledger_entries.append(LedgerEntry(
            company_id=invoice.company_id,
            invoice_id=invoice.invoice_id,
            account_name=payment_account,
            debit=0.00,
            credit=invoice.total_amount,
            entry_date=invoice.invoice_date
        ))

    # Save all entries
    db.session.add_all(ledger_entries)
    db.session.commit()


@app.route('/ledger', methods=['GET'])
@login_required
def ledger():
    # Fetch all ledger entries for the current user's company
    ledger_entries = db.session.query(LedgerEntry).join(Invoice).filter(
        Invoice.company_id == current_user.company_id
    ).all()

    return render_template('ledger.html', ledger_entries=ledger_entries)


@app.route('/financial_insights', methods=['POST'])
def financial_insights():
    insight = generate_financial_insight()

    # Return JSON instead of rendering a template
    return jsonify({"insight": insight})
