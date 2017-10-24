import base64


def encode(string, return_type='b'):
    if return_type is 'b':
        return base64.b64encode(string.encode('utf-8'))
    elif return_type is 'str':
        return base64.b64encode(string.encode('utf-8')).decode('utf-8')
    raise Exception('invalid return_type')


def decode(string, return_type='b'):
    if return_type is 'b':
        return base64.b64decode(string)
    elif return_type is 'str':
        return base64.b64decode(string).decode('utf-8')
    raise Exception('invalid return_type')
