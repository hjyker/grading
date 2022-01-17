class Config(object):
    ''' 可用.操作符取属性的参数实例 '''

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return self.__dict__
