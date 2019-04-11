import exceptions


class ProxyException(exceptions.Exception):
    return_http_code = None
    return_code = None
    return_message = None

    def __init__(self, code=-1, message='proxy error', http_code=500):
        super(ProxyException, self).__init__()
        self.return_http_code = http_code
        self.return_code = code
        self.return_message = message

    def get_return_body(self):
        body = {'errorCode': self.return_code, 'message': self.return_message}
        return body
