"""程序统一入口：在项目根目录运行 `python main.py` 即可启动 GUI"""
import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication

# 确保项目根目录在模块搜索路径中（即使从其他目录启动也能导入 data_exchange / parsers）
sys.path.insert(0, str(Path(__file__).resolve().parent))

from gui.main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.window.show()

    sys.exit(app.exec())
