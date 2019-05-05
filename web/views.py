from flask import render_template, request, session
from flask import Blueprint

from app import app
from web.utils import get_transaction_identifier
from web.forms import RegistrationForm
from api.constants import CurrencyCodes
from api.methods import PiastrixMethodFactory

log = app.logger

pages = Blueprint(name='pages', import_name=__name__,
                  template_folder='templates')


@pages.route('/', methods=['GET', 'POST'])
def payment():
    _id = get_transaction_identifier()
    form = RegistrationForm(request.form, meta={'csrf_context': session})
    if request.method == 'POST' and form.validate():
        try:
            currency_code = getattr(CurrencyCodes, form.currency.data).value
        except AttributeError:
            message = 'Invalid currency code'
            return render_template('forms/main.html',
                                   form=form, message=message)
        _data = form.data.copy()
        log.info(f'> {_id} > Received data from form {_data}')
        _data.update({'currency': currency_code})
        method = PiastrixMethodFactory(currency_code, _id=_id)
        method = method.get_method()
        method = method(_data, _id=_id)
        return method.request()
    elif form.csrf_token.errors:
        log.error(f'> {_id} > Form submitted without CSRF')
        pass
    return render_template('forms/main.html', form=form)
