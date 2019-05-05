import hashlib

from app import app
from api import settings
from api.abstractions import SignGenerator

log = app.logger


class PiastrixSignGenerator(SignGenerator):

    def __init__(self, data: dict, keys_required: tuple, **kwargs):
        self.data = data
        self.keys_required = keys_required
        self._id = kwargs.get('_id')

    def _keys_is_valid(self):
        data_keys = self.data.keys()
        return all(key in data_keys for key in self.keys_required)

    def _prepare_string(self):
        if self._keys_is_valid():
            # sorted_values = [str(kv[1]) for kv in
            #                  sorted(self.data.items(), key=lambda kv: kv[0])]
            sorted_values = [str(self.data.get(arg))
                             for arg in self.keys_required]
            _string = ':'.join(sorted_values) + settings.SECRET
            log.info(f'> {self._id} > Constructing string for secret key: '
                     f'{_string} by data: {self.data}')
            return _string
        else:
            log.error(f'> {self._id} > Error during string preparation '
                      f'for secret generation by data: {self.data}')
            raise ValueError

    def generate(self):
        _secret_string = self._prepare_string()
        _hash = hashlib.sha256(_secret_string.encode('utf-8')).hexdigest()
        log.info(f'> {self._id} > Generating secret key: '
                 f'{_hash} by data: {self.data}')
        return _hash
