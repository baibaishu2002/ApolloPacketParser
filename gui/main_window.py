import sys
from pathlib import Path
from PySide6.QtCore import QFile, QIODevice, Slot, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QLineEdit,
    QFileDialog,
    QListWidget,
    QTreeWidget,
    QTreeWidgetItem,
)
from PySide6.QtGui import QAction

# 将项目根目录加入模块搜索路径，确保无论从何处启动都能导入 data_exchange / parsers
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data_exchange import exchange
import parsers.apollo_parser as apollo_parser


# 定义主窗口类
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 加载UI文件（基于本文件位置定位，不依赖当前工作目录）
        loader = QUiLoader()
        ui_path = str(Path(__file__).resolve().parent / "ui" / "main_window.ui")
        main_ui_file = QFile(ui_path)
        if not main_ui_file.open(QIODevice.ReadOnly):
            print("无法打开UI文件")
            sys.exit(-1)
        self.window = loader.load(main_ui_file)  # 加载UI文件并实例化为窗口对象
        main_ui_file.close()  # 关闭UI文件

        exchange.data_changed.connect(self.on_data_changed)
        # ---------- 菜单栏bar ----------
        # 控件寻找
        self.action_exit = self.window.findChild(
            QAction, "actionExit"
        )  # 找到"actionExit"
        self.action_about = self.window.findChild(
            QAction, "actionAbout"
        )  # 找到"actionAbout"
        self.action_select_packet = self.window.findChild(QAction, "actionSelectPacket")
        self.action_select_output = self.window.findChild(QAction, "actionSelectOutput")
        # 绑定动作
        self.action_exit.triggered.connect(self.window.close)
        self.action_about.triggered.connect(self.about_click)
        self.action_select_packet.triggered.connect(self.select_packet)
        self.action_select_output.triggered.connect(self.select_output_dir)

        # ---------- 主要部分 ----------
        # 按钮寻找
        self.btn_select_packet = self.window.findChild(QPushButton, "btnSelectPacket")
        self.btn_select_output = self.window.findChild(QPushButton, "btnSelectOutput")
        self.btn_parse_channel = self.window.findChild(QPushButton, "btnParseChannel")
        self.btn_parse_message = self.window.findChild(QPushButton, "btnParseMessage")
        self.btn_export_csv = self.window.findChild(QPushButton, "btnExportCSV")
        self.btn_export_jpg = self.window.findChild(QPushButton, "btnExportJPG")
        self.btn_export_pcd = self.window.findChild(QPushButton, "btnExportPCD")
        # 输入框寻找
        self.line_edit_packet = self.window.findChild(QLineEdit, "lineEditPacketPath")
        self.line_edit_output = self.window.findChild(QLineEdit, "lineEditOutputDir")
        # Channel列表list寻找
        self.list_widget_channel = self.window.findChild(
            QListWidget, "listWidgetChannel"
        )
        # Message字段树寻找
        self.tree_widget_message = self.window.findChild(
            QTreeWidget, "treeWidgetMessage"
        )
        # 绑定动作
        self.btn_select_packet.clicked.connect(self.select_packet)
        self.btn_select_output.clicked.connect(self.select_output_dir)
        self.btn_parse_channel.clicked.connect(self.parse_channels)
        self.btn_parse_message.clicked.connect(self.parse_message)
        self.btn_export_csv.clicked.connect(self.export_csv)
        self.btn_export_jpg.clicked.connect(self.export_jpg)
        self.btn_export_pcd.clicked.connect(self.export_pcd)

    # 菜单栏about执行函数
    @Slot()
    def about_click(self):
        QMessageBox.information(self.window, "关于", "Apollo 数据包解析工具 V0.0.1")

    @Slot()
    def select_packet(self):
        """选择数据包文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.window,
            "选择数据包文件",
            "",  # 默认打开的文件路径，空字符串表示不指定初始目录
            "All Files (*)",  # 文件类型过滤器
        )
        if file_path:
            exchange.packet_path = file_path

    @Slot()
    def select_output_dir(self):
        """选择输出文件夹路径"""
        dir_path = QFileDialog.getExistingDirectory(
            self.window, "选择输出文件夹", ""  # 默认路径
        )
        if dir_path:
            exchange.output_dir = dir_path

    @Slot()
    def parse_channels(self):
        "解析出所有channel"
        try:
            apollo_parser.get_all_channels()
            if exchange.channels == {}:
                QMessageBox.warning(self.window, "解析错误", "该数据包中无内容")
        except:
            QMessageBox.warning(self.window, "解析错误", "数据包解析失败\n\n可能是数据包损坏或选择了错误的数据包")

    @Slot()
    def parse_message(self):
        "解析exchange.channels中第一帧的message"
        exchange.selected_channel = self.list_widget_channel.currentItem().text()
        apollo_parser.get_messages()
        if exchange.messages == {}:
            QMessageBox.warning(self.window, "解析错误", "该 Channel 中无内容")

    @Slot()
    def export_csv(self):
        exchange.selected_messages = self._get_selected_messages()
        try:
            if apollo_parser.export_csv():
                QMessageBox.information(self.window, "导出完成", "导出完成")
        except:
            QMessageBox.warning(self.window, "导出失败", "导出失败")

    @Slot()
    def export_jpg(self):
        exchange.selected_channel = self.list_widget_channel.currentItem().text()
        try:
            if apollo_parser.export_jpg():
                QMessageBox.information(self.window, "导出完成", "导出完成")
            else:
                QMessageBox.warning(self.window, "导出失败", "导出失败")
        except:
            QMessageBox.warning(self.window, "导出失败", "导出失败")

    @Slot()
    def export_pcd(self):
        exchange.selected_channel = self.list_widget_channel.currentItem().text()
        try:
            if apollo_parser.export_pcd():
                QMessageBox.information(self.window, "导出完成", "导出完成")
            else:
                QMessageBox.warning(self.window, "导出失败", "导出失败")
        except:
            QMessageBox.warning(self.window, "导出失败", "导出失败")
        

    @Slot(str, object)
    def on_data_changed(self, name, value):
        """根据属性名更新对应的控件"""
        if name == "packet_path":
            self.line_edit_packet.setText(value)
            exchange.channels = []
            exchange.messages = {}
            exchange.selected_channel = ""
            exchange.selected_messages = []
        elif name == "output_dir":
            self.line_edit_output.setText(value)
        elif name == "channels":
            self.list_widget_channel.clear()
            for channel in exchange.channels:
                self.list_widget_channel.addItem(channel)
        elif name == "messages":
            self.tree_widget_message.clear()  # 清空所有现有节点
            # 填充内容
            for key, message in exchange.messages.items():
                self._add_tree_item(None, key, message)
            # 重置展开状态
            self.tree_widget_message.expandAll()

    def _add_tree_item(self, parent, key, value):
        """递归添加树节点: parent 为父节点(None 表示顶层),key 为键,value 为值"""
        if parent is None:
            item = QTreeWidgetItem(self.tree_widget_message)  # 顶层节点
        else:
            item = QTreeWidgetItem(parent)  # 子节点
        item.setText(0, str(key))

        # 子节点开启复选框
        if not isinstance(value, dict):
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Unchecked)  # 初始状态为未选中

        if isinstance(value, dict):
            # 如果值是字典，继续递归添加子节点
            for child_key, child_value in value.items():
                self._add_tree_item(item, child_key, child_value)
        else:
            # 如果值不是字典，显示“键: 值”
            if isinstance(value, str):
                item.setText(0, f"{key}: {value[:100]}")  # 防止字符显示过长
            else:
                item.setText(0, f"{key}: {value}")

    def _get_selected_messages(self):
        """遍历树，返回被勾选的叶子节点的路径列表(如 ['field1.subfield', 'field2'])"""
        selected = []

        def traverse(item, path):
            # 如果是叶子节点（没有子节点）且被勾选
            if item.childCount() == 0:  # 判断是否为叶子节点
                if item.checkState(0) == Qt.Checked:  # 判断是否被勾选
                    # 叶子的文本是 "key: value"，只取 key
                    key = item.text(0).split(":")[0].strip()
                    full_path = f"{path}.{key}" if path else key
                    selected.append(full_path)
            else:
                # 非叶子节点，递归处理子项
                for i in range(item.childCount()):
                    child = item.child(i)
                    # 当前节点的文本是键名（可能包含 : 但这里我们取键）
                    key = item.text(0).split(":")[0].strip() if item.text(0) else ""
                    new_path = f"{path}.{key}" if path else key
                    traverse(child, new_path)

        root = self.tree_widget_message.invisibleRootItem()
        for i in range(root.childCount()):
            traverse(root.child(i), "")
        return selected
