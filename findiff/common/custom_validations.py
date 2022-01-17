from django.utils.encoding import force_text
from rest_framework import status
from rest_framework.exceptions import APIException


class NonFieldError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '状态异常'
    default_code = 'non_field_errors'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        self.detail = {code: force_text(detail)}
