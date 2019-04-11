class ResponseEntity:

    def __init__(self):
        self.request_url = None
        self.request_body = None
        # http error message
        self.error_message = None
        # http status code, when defined, return as http_status_code
        self.error_code = None
        # body from http raw response
        self.return_body = None

    @staticmethod
    def create_success_entity(request_url, request_body, return_body):
        entity = ResponseEntity()
        entity.request_url = request_url
        entity.request_body = request_body
        entity.return_body = return_body
        return entity

    @staticmethod
    def create_failed_entity(request_url, request_body, error_code, error_message, return_body):
        entity = ResponseEntity()
        entity.request_url = request_url
        entity.request_body = request_body
        entity.return_body = return_body
        entity.error_code = error_code
        entity.error_message = error_message
        return entity
