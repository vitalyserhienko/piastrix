from wtforms.csrf.session import SessionCSRF
from wtforms import Form
from wtforms import validators
from wtforms import SelectField, TextAreaField, StringField

from app.settings import SECRET_KEY_CSRF


class BaseForm(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = SECRET_KEY_CSRF


class RegistrationForm(BaseForm):
    amount = StringField('Sum',
                         default='0.00',
                         render_kw={'type': 'number', 'step': '0.01'},
                         validators=[
                             validators.required(),
                             validators.none_of(('0.00', '00.00', '00'),
                                                message='sum must be '
                                                        'greater than 0'),
                             validators.Regexp(r'\d+\.\d{2}',
                                               message='Only digits with two '
                                                       'symbols after coma '
                                                       'allowed')], )
    currency = SelectField('Currency',
                           choices=[('USD', 'USD'),
                                    ('EUR', 'EUR'),
                                    ('RUB', 'RUB')],
                           validators=[validators.required(), ], )
    description = TextAreaField('Description',
                                validators=[validators.required(),
                                            validators.length(max=100)], )
