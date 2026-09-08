# data_exchange.py
from PySide6.QtCore import QObject, Signal

class DataExchange(QObject):
    # 通用信号：第一个参数是属性名(str)，第二个参数是新值(object)
    data_changed = Signal(str, object)

    def __init__(self):
        super().__init__()
        # 用一个字典保存所有数据的值
        self._data = {}

    # 当访问一个不存在的属性时，Python 会调用 __getattr__
    def __getattr__(self, name):
        # 如果这个名字在字典里，就返回它的值
        if name in self._data:
            return self._data[name]
        # 否则抛出正常的属性错误
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    # 当给任意属性赋值时，Python 会调用 __setattr__
    def __setattr__(self, name, value):
        # 如果属性名以下划线开头，说明是内部属性（比如 _data），按正常方式设置
        if name.startswith('_'):
            super().__setattr__(name, value)
            return
        # 否则把它当作数据属性，存入字典
        old_value = self._data.get(name)
        if old_value != value:  # 只有值真的变了才发信号
            self._data[name] = value
            self.data_changed.emit(name, value)

# 创建全局唯一实例
exchange = DataExchange()

exchange.packet_path = ''
exchange.output_dir = ''
exchange.channels = []
exchange.messages = {}
exchange.selected_channel = ''
exchange.selected_messages = []