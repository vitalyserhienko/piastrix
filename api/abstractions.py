class SignGenerator:

    def generate(self):
        raise NotImplementedError


class MethodBase:

    def request(self, *args, **kwargs):
        raise NotImplementedError

    def process_response(self, *args, **kwargs):
        raise NotImplementedError


class MethodFactory:

    def get_method(self):
        raise NotImplementedError
