import random
import requests

from flask import redirect, render_template

from app import app
from api import settings
from api.constants import CurrencyCodes
from api.exceptions import PiastrixGeneralError, PiasrixResponceError
from api.abstractions import MethodBase, MethodFactory
from api.signature import PiastrixSignGenerator

log = app.logger


class PiastrixMethodFactory(MethodFactory):

    def __init__(self, currency, **kwargs):
        self.currency = currency
        self._id = kwargs.get('_id')

    def get_method(self):
        if self.currency == CurrencyCodes.EUR.value:
            return PiastrixMethodPay
        elif self.currency == CurrencyCodes.USD.value:
            return PiastrixMethodBill
        elif self.currency == CurrencyCodes.RUB.value:
            return PiastrixMethodInvoice
        log.error(f'> {self._id} > No valid Method '
                  f'for currency: {self.currency}')


class PiastrixMethodBase(MethodBase):

    def __init__(self, *args, **kwargs):
        self._id = kwargs.get('_id')

    def request(self, method, *args, **kwargs):
        if method == 'POST':
            return requests.post(*args, **kwargs)
        elif method == 'GET':
            return requests.get(*args, *kwargs)

    def process_response(self, responce):
        if getattr(responce, 'status_code') == 200:
            json_data = responce.json()
            log.info(f'> {self._id} > Received responce: {json_data}')
            if json_data.get('result'):
                return json_data
            elif json_data.get('error_code'):
                log.error(f'> {self._id} > Error processing '
                          f'response: {json_data}')
                raise PiasrixResponceError(**json_data)
        raise PiastrixGeneralError


class PiastrixMethodPay(PiastrixMethodBase):

    __required_keys = ('amount', 'currency', 'shop_id', 'shop_order_id')

    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self._prepare_data()
        self.generator = PiastrixSignGenerator(self.data,
                                               self.__required_keys, **kwargs)
        self.url = settings.PIASTRIX_PAY_URL_EN
        self.headers = {
            'Content-Type': 'application/json',
        }

    def _prepare_data(self):
        random_order_id = random.randint(1, 200000)

        self.data.update(
            {
                'shop_id': settings.SHOP_ID,
                'shop_order_id': random_order_id
            }
        )

    def request(self, *args, **kwargs):
        self.data.update({'sign': self.generator.generate()})
        log.info(f'> {self._id} > Redirecting user to pay form')
        return render_template('forms/piastrix/pay.html', **self.data)


class PiastrixMethodBill(PiastrixMethodBase):

    __required_keys = ('shop_currency', 'shop_amount', 'payer_currency',
                       'shop_id', 'shop_order_id')

    def __init__(self, data: dict, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self._prepare_data()
        self.generator = PiastrixSignGenerator(self.data,
                                               self.__required_keys, **kwargs)
        self.url = settings.PIASTRIX_BILL_URL
        self.headers = {
            'Content-Type': 'application/json',
        }

    def _prepare_data(self):
        random_order_id = random.randint(1, 200000)
        amount = self.data.pop('amount')
        currency = self.data.pop('currency')
        self.data.pop('description')
        self.data.update(
            {
                'shop_amount': amount,
                'payer_currency': currency,
                'shop_currency': currency,
                'shop_id': settings.SHOP_ID,
                'shop_order_id': random_order_id
            }
        )

    def request(self, *args, **kwargs):
        self.data.update({'sign': self.generator.generate()})
        responce = super().request(method='POST', url=self.url,
                                   headers=self.headers, json=self.data)
        responce = self.process_response(responce)
        redirect_url = responce.get('data', {}).get('url')

        if redirect_url:
            log.info(f'> {self._id} > Redirecting user to url: {redirect_url}')
            return redirect(redirect_url, code=302)


class PiastrixMethodInvoice(PiastrixMethodBase):

    __required_keys = ('amount', 'currency', 'payway',
                       'shop_id', 'shop_order_id')

    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self._prepate_data()
        self.generator = PiastrixSignGenerator(self.data,
                                               self.__required_keys, **kwargs)
        self.url = settings.PIASTRIX_INVOICE_URL
        self.headers = {
            'Content-Type': 'application/json',
        }

    def _prepate_data(self):
        random_order_id = random.randint(1, 200000)
        self.data.pop('description')
        self.data.update(
            {
                'shop_id': settings.SHOP_ID,
                'shop_order_id': random_order_id,
                'payway': settings.PAYWAY,
            }
        )

    def request(self, *args, **kwargs):
        self.data.update({'sign': self.generator.generate()})
        responce = super().request(method='POST', url=self.url,
                                   headers=self.headers, json=self.data)
        responce = self.process_response(responce)
        log.info(f'> {self._id} > Redirecting user to invoice form')
        return render_template('forms/payeer/invoice.html',
                               **{**responce.get('data'),
                                  **responce.get('data', {}).get('data')})
