"""module for text encoding/decoding to/from base64 """
import base64


def encode(string, return_type='b'):
    """encode string to base64"""
    if return_type is 'b':
        return base64.b64encode(string.encode('utf-8'))
    elif return_type is 'str':
        return base64.b64encode(string.encode('utf-8')).decode('utf-8')
    raise Exception('invalid return_type')


def decode(string, return_type='b'):
    """decode string from base64"""
    if return_type == 'b':
        return base64.b64decode(string)
    elif return_type == 'str':
        return base64.b64decode(string).decode('utf-8')
    raise Exception('invalid return_type')
