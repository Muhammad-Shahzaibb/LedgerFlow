from Project import db, login_manager
from Project import bcrypt
from flask_login import UserMixin


@login_manager.user_loader
def load_user(company_id):
    return Company.query.get(int(company_id))


class Company(db.Model, UserMixin):
    __tablename__ = 'companies'
    company_id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    # Store plain text password
    Password = db.Column(db.String(255), nullable=False)
    invoices = db.relationship('Invoice', backref='invoice', lazy=True)

    def get_id(self):
        return str(self.company_id)

    def check_password_correction(self, attempted_password):
        return self.Password == attempted_password


class Invoice(db.Model):
    __tablename__ = 'invoices'
    invoice_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey(
        'companies.company_id'), nullable=False)
    sender = db.Column(db.String(255), nullable=False)
    receiver = db.Column(db.String(255), nullable=False)
    invoice_number = db.Column(db.String(50), nullable=False)
    invoice_date = db.Column(db.String(50), nullable=False)
    due_date = db.Column(db.String(50), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)

    # Support multiple invoice types
    invoice_type = db.Column(db.Enum('Service Invoice', 'Stock Purchase Invoice', 'Real Estate Purchase Invoice',
                             'Equipment Purchase Invoice', 'Raw Materials Purchase Invoice', 'Salary Invoice', name='invoice_types'), nullable=False)

    status = db.Column(db.Enum('Paid', 'Unpaid', 'Pending',
                       'Cancelled'), nullable=False)

    # Relationship with Ledger Entries
    ledger_entries = db.relationship(
        'LedgerEntry', backref='invoice', lazy=True)


class LineItem(db.Model):
    __tablename__ = 'LineItem'
    line_item_id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey(
        'invoices.invoice_id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, nullable=True)
    unit_price = db.Column(db.Numeric(10, 2), nullable=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)


class LedgerEntry(db.Model):
    __tablename__ = 'ledger_entries'
    entry_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey(
        'companies.company_id'), nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey(
        'invoices.invoice_id'), nullable=False)
    account_name = db.Column(db.String(255), nullable=False)
    debit = db.Column(db.Numeric(10, 2), nullable=False)
    credit = db.Column(db.Numeric(10, 2), nullable=False)
    entry_date = db.Column(db.String(50), nullable=False)
