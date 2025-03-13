from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError, InputRequired
from Project.models import Company
from flask_wtf.file import FileField, FileRequired


class InvoiceUploadForm(FlaskForm):
    invoice_file = FileField(
        'Upload Invoice (PDF/JPEG/PNG)', validators=[FileRequired()])
    submit = SubmitField('Upload')


class RegisterForm(FlaskForm):
    def validate_company_name(self, company_name_to_check):
        company = Company.query.filter_by(
            company_name=company_name_to_check.data).first()
        if company:
            raise ValidationError(
                'Company with this name already exists! Please try a different name')

    def validate_Email(self, email_address_to_check):
        email_address = Company.query.filter_by(
            Email=email_address_to_check.data).first()
        if email_address:
            raise ValidationError(
                'Email Address already exists! Please try a different email address')

    company_name = StringField(label='Company Name:', validators=[
                               Length(min=2, max=30), DataRequired()])
    Email = StringField(label='Email Address:', validators=[
                        Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[
                              Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[
                              EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')


class LoginForm(FlaskForm):
    Email = StringField(label='Email address:', validators=[
                        Email(), DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')


class InvoiceUploadForm(FlaskForm):
    invoice_file = FileField(
        'Upload Invoice (PDF/JPEG/PNG)', validators=[InputRequired()])
    submit = SubmitField('Upload')
