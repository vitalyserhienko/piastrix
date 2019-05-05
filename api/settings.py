import os

PIASTRIX_PAY_URL_RU = 'https://pay.piastrix.com/ru/pay'
PIASTRIX_PAY_URL_EN = 'https://pay.piastrix.com/en/pay'
PIASTRIX_BILL_URL = 'https://core.piastrix.com/bill/create'
PIASTRIX_INVOICE_URL = 'https://core.piastrix.com/invoice/create'
SECRET = os.environ.get('SECRET_KEY_PAYMENT')
SHOP_ID = os.environ.get('SHOP_ID')
PAYWAY = 'payeer_rub'
