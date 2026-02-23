import sys
import json
import os
import shutil
from datetime import datetime
import zhconv  
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QAction, QTextCursor, QTextCharFormat, QColor, QCloseEvent, QIntValidator, QFont
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget,
                               QHBoxLayout, QVBoxLayout, QListWidget, QTextEdit, 
                               QLineEdit, QFormLayout, QFileDialog, QListWidgetItem,
                               QCheckBox, QSpinBox, QMessageBox, QTabWidget, QComboBox,
                               QPushButton, QAbstractItemView, QDialog, QInputDialog, QFrame, QLabel)

# ================= 现代蓝白主题 QSS 样式表 =================
MODERN_BLUE_THEME = """
/* 全局字体和基础设定 */
* {
    font-family: "Segoe UI Variable", "Microsoft YaHei", "PingFang SC", sans-serif;
    font-size: 13px;
    color: #2C3E50;
    outline: none;
}

/* 主窗口背景色 - 淡雅的浅蓝白 */
QMainWindow, QDialog {
    background-color: #F2F7FB; 
}

/* 所有的面板容器白底、圆角 */
#SidePanel, #MainTabs::pane {
    background-color: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #E1E8EE;
}

/* ================= 文本框、数字框和下拉菜单 ================= */
QLineEdit, QTextEdit, QSpinBox, QComboBox {
    background-color: #F8FAFC;
    border: 1px solid #D2DCE6;
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: #75C2F6;
}

QLineEdit:hover, QTextEdit:hover, QSpinBox:hover, QComboBox:hover {
    border: 1px solid #75C2F6;
    background-color: #FFFFFF;
}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 2px solid #59B4FF;
    background-color: #FFFFFF;
}

/* 下拉菜单特调 */
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: none;
}
QComboBox QAbstractItemView {
    border: 1px solid #D2DCE6;
    border-radius: 6px;
    background-color: #FFFFFF;
    selection-background-color: #ECF5FF;
    selection-color: #59B4FF;
    padding: 4px;
}

/* ================= 按钮样式 (优雅动态) ================= */
QPushButton {
    background-color: #59B4FF;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #75C2F6;
}

QPushButton:pressed {
    background-color: #4A9EE0;
    padding-top: 9px; /* 按下时的微小下沉动态效果 */
    padding-bottom: 7px;
}

/* 次要操作按钮 (如查找替换) */
QPushButton#SecondaryBtn {
    background-color: #F0F4F8;
    color: #59B4FF;
    border: 1px solid #D2DCE6;
}
QPushButton#SecondaryBtn:hover {
    background-color: #E1EDF7;
    border: 1px solid #59B4FF;
}

/* ================= 左侧列表样式 ================= */
QListWidget {
    background-color: transparent;
    border: none;
}
QListWidget::item {
    padding: 10px;
    margin: 2px 5px;
    border-radius: 6px;
    color: #34495E;
}
QListWidget::item:hover {
    background-color: #E8F2FA;
}
QListWidget::item:selected {
    background-color: #59B4FF;
    color: #FFFFFF;
    font-weight: bold;
}

/* ================= 标签页样式 ================= */
QTabWidget::pane {
    top: -1px; /* 隐藏原生边框瑕疵 */
}
QTabBar::tab {
    background: transparent;
    color: #7F8C8D;
    padding: 10px 20px;
    border-bottom: 3px solid transparent;
    font-size: 14px;
    font-weight: bold;
}
QTabBar::tab:hover {
    color: #59B4FF;
}
QTabBar::tab:selected {
    color: #59B4FF;
    border-bottom: 3px solid #59B4FF;
}

/* ================= 复选框样式 ================= */
QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #D2DCE6;
    background: #F8FAFC;
}
QCheckBox::indicator:hover {
    border: 1px solid #59B4FF;
}
QCheckBox::indicator:checked {
    background: #59B4FF;
    border: 1px solid #59B4FF;
    image: url(); /* 这里如果想要对勾可以放一张白色的勾选SVG，PySide默认会处理颜色，或者保持纯色块也很现代 */
}

/* ================= 滚动条样式 (隐藏丑陋的Windows原生条) ================= */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #CBD5E1;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #94A3B8;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

# ================= 自定义组件 =================
class DragListWidget(QListWidget):
    itemMoved = Signal(int, int) 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.InternalMove)
    def dropEvent(self, event):
        old_index = self.currentRow()
        super().dropEvent(event)
        new_index = self.currentRow()
        if old_index != new_index and old_index != -1 and new_index != -1:
            self.itemMoved.emit(old_index, new_index)

class ContentEditorWidget(QWidget):
    textChanged = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        tools_layout = QHBoxLayout()
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("🔍 查找内容...")
        
        self.btn_find = QPushButton("查找下一个")
        self.btn_find.setObjectName("SecondaryBtn")
        
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("📝 替换为...")
        
        self.btn_replace = QPushButton("替换")
        self.btn_replace.setObjectName("SecondaryBtn")
        
        self.btn_replace_all = QPushButton("全部替换")
        self.btn_replace_all.setObjectName("SecondaryBtn")

        tools_layout.addWidget(self.find_input)
        tools_layout.addWidget(self.btn_find)
        tools_layout.addWidget(self.replace_input)
        tools_layout.addWidget(self.btn_replace)
        tools_layout.addWidget(self.btn_replace_all)

        self.text_edit = QTextEdit()
        self.text_edit.setMinimumHeight(150)
        
        layout.addLayout(tools_layout)
        layout.addWidget(self.text_edit)

        self.btn_find.clicked.connect(self.find_next)
        self.btn_replace.clicked.connect(self.replace_current)
        self.btn_replace_all.clicked.connect(self.replace_all)
        self.find_input.textChanged.connect(self.highlight_all) 
        self.text_edit.textChanged.connect(self.textChanged.emit)

    def highlight_all(self):
        search_text = self.find_input.text()
        selections = []
        if search_text:
            fmt = QTextCharFormat()
            fmt.setBackground(QColor("#FF7676")) 
            fmt.setForeground(QColor("#FFFFFF")) 
            
            cursor = QTextCursor(self.text_edit.document())
            while not cursor.isNull() and not cursor.atEnd():
                cursor = self.text_edit.document().find(search_text, cursor)
                if not cursor.isNull():
                    sel = QTextEdit.ExtraSelection()
                    sel.format = fmt
                    sel.cursor = cursor
                    selections.append(sel)
        self.text_edit.setExtraSelections(selections)

    def find_next(self):
        search_text = self.find_input.text()
        if not search_text: return
        found = self.text_edit.find(search_text)
        if not found:
            self.text_edit.moveCursor(QTextCursor.Start)
            self.text_edit.find(search_text)

    def replace_current(self):
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == self.find_input.text():
            fmt = QTextCharFormat()
            fmt.setBackground(QColor("#59B4FF")) 
            fmt.setForeground(QColor("#FFFFFF"))
            cursor.insertText(self.replace_input.text(), fmt)
            self.highlight_all() 
            self.find_next()

    def replace_all(self):
        search_text = self.find_input.text()
        replace_text = self.replace_input.text()
        if not search_text: return
        
        cursor = QTextCursor(self.text_edit.document())
        cursor.beginEditBlock()
        count = 0
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#59B4FF"))
        fmt.setForeground(QColor("#FFFFFF"))
        
        while not cursor.isNull() and not cursor.atEnd():
            cursor = self.text_edit.document().find(search_text, cursor)
            if not cursor.isNull():
                cursor.insertText(replace_text, fmt)
                count += 1
        cursor.endEditBlock()
        self.highlight_all()
        QMessageBox.information(self, "替换完毕", f"共替换了 {count} 处内容。")

    def toPlainText(self): return self.text_edit.toPlainText()
    def setText(self, t): self.text_edit.setText(t); self.highlight_all()
    def clear(self): self.text_edit.clear()

class ConvertDialog(QDialog):
    def __init__(self, mode_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"选择要转换为 {mode_name} 的字段")
        self.setMinimumWidth(300)
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.chk_title = QCheckBox("标题/备注 (Comment)")
        self.chk_keys = QCheckBox("触发词与过滤器 (Keys & Filters)")
        self.chk_content = QCheckBox("条目内容 (Content)")
        
        self.chk_title.setChecked(True)
        self.chk_keys.setChecked(True)
        self.chk_content.setChecked(True)
        
        layout.addWidget(self.chk_title)
        layout.addWidget(self.chk_keys)
        layout.addWidget(self.chk_content)
        
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("确定")
        btn_cancel = QPushButton("取消")
        btn_cancel.setObjectName("SecondaryBtn")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def get_selection(self):
        return self.chk_title.isChecked(), self.chk_keys.isChecked(), self.chk_content.isChecked()

# ================= 主窗口 =================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SillyTavern 世界书本地编辑器")
        self.resize(1150, 800)

        # 注入全局 QSS 主题
        self.setStyleSheet(MODERN_BLUE_THEME)

        self.current_file_path = None
        self.world_info_data = {}
        self.current_entry_key = None 
        self.field_map = {} 
        self.is_modified = False 

        self.create_menu()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        # 增加主窗口的外边距和组件间距，让界面呼吸感更强
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # ====== 左侧面板 (封装为独立带有背景的 QFrame) ======
        left_panel = QFrame()
        left_panel.setObjectName("SidePanel") # 用于QSS匹配白底
        left_panel.setFixedWidth(300)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(12)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 全局搜索 (标题/词/内容)...")
        left_layout.addWidget(self.search_bar)

        self.list_widget = DragListWidget()
        left_layout.addWidget(self.list_widget)

        btn_layout1 = QHBoxLayout()
        self.btn_add = QPushButton("➕ 新增")
        self.btn_del = QPushButton("❌ 删除")
        self.btn_del.setObjectName("SecondaryBtn") # 删除按钮样式变淡
        self.btn_move = QPushButton("📍 移至...")
        self.btn_move.setObjectName("SecondaryBtn")
        btn_layout1.addWidget(self.btn_add)
        btn_layout1.addWidget(self.btn_move)
        btn_layout1.addWidget(self.btn_del)
        left_layout.addLayout(btn_layout1)
        
        btn_layout2 = QHBoxLayout()
        self.btn_simp = QPushButton("🇨🇳 简")
        self.btn_trad = QPushButton("🇭🇰 繁")
        self.btn_simp.setObjectName("SecondaryBtn")
        self.btn_trad.setObjectName("SecondaryBtn")
        btn_layout2.addWidget(self.btn_simp)
        btn_layout2.addWidget(self.btn_trad)
        left_layout.addLayout(btn_layout2)

        layout.addWidget(left_panel)

        # ====== 右侧标签页 ======
        self.tabs = QTabWidget()
        self.tabs.setObjectName("MainTabs")
        layout.addWidget(self.tabs)

        self.setup_tabs()
        
        self.field_map['position']['widget'].currentIndexChanged.connect(self.update_position_ui)
        self.field_map['delayUntilRecursion']['widget'].toggled.connect(self.update_recursion_ui)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.search_bar.textChanged.connect(self.filter_list)
        self.btn_add.clicked.connect(self.add_entry)
        self.btn_del.clicked.connect(self.delete_entry)
        
        self.list_widget.itemMoved.connect(self.on_item_dragged)
        self.btn_move.clicked.connect(self.move_to_index)
        self.btn_simp.clicked.connect(lambda: self.convert_chinese('zh-cn'))
        self.btn_trad.clicked.connect(lambda: self.convert_chinese('zh-tw'))

    def set_modified(self):
        if not self.is_modified:
            self.is_modified = True
            title = self.windowTitle()
            if not title.endswith("*"):
                self.setWindowTitle(title + " *")

    def create_menu(self):
        menubar = self.menuBar()
        # 顶部菜单栏背景修饰
        menubar.setStyleSheet("background-color: #FFFFFF; border-bottom: 1px solid #D2DCE6;")
        file_menu = menubar.addMenu("文件 (File)")

        new_action = QAction("新建", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("打开", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)
        
        save_action = QAction("保存", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("另存为", self) 
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_action)

    def add_field(self, layout, label, json_key, widget_type, **kwargs):
        label_widget = None
        if widget_type == 'text':
            w = QLineEdit()
            w.textChanged.connect(lambda _: self.set_modified())
            layout.addRow(label, w)
        elif widget_type == 'content_editor': 
            w = ContentEditorWidget()
            w.textChanged.connect(self.set_modified)
            layout.addRow(label, w)
        elif widget_type == 'bool' or widget_type == 'invert_bool':
            w = QCheckBox(label)
            w.toggled.connect(lambda _: self.set_modified())
            layout.addRow("", w)
        elif widget_type == 'int':
            w = QSpinBox()
            w.setRange(kwargs.get('min', 0), kwargs.get('max', 99999))
            w.valueChanged.connect(lambda _: self.set_modified())
            layout.addRow(label, w)
        elif widget_type == 'nullable_int':
            w = QLineEdit()
            w.setPlaceholderText("为空则使用全局设置")
            w.setValidator(QIntValidator(0, 99999, w)) 
            w.textChanged.connect(lambda _: self.set_modified())
            layout.addRow(label, w)
        elif widget_type == 'combo' or widget_type == 'strategy_combo':
            w = QComboBox()
            w.addItems(kwargs.get('items', []))
            w.currentIndexChanged.connect(lambda _: self.set_modified())
            layout.addRow(label, w)
        elif widget_type == 'tristate_combo':
            w = QComboBox()
            w.addItems(["使用全局 (Global)", "是 (Yes)", "否 (No)"])
            w.currentIndexChanged.connect(lambda _: self.set_modified())
            layout.addRow(label, w)
        elif widget_type == 'multicheck':
            w = QWidget()
            h_layout = QHBoxLayout(w)
            h_layout.setContentsMargins(0, 0, 0, 0)
            h_layout.setSpacing(15) # 复选框之间的间距
            w.checkboxes = {}
            for val, txt in kwargs.get('options', {}).items():
                cb = QCheckBox(txt)
                cb.toggled.connect(lambda _: self.set_modified())
                w.checkboxes[val] = cb
                h_layout.addWidget(cb)
            layout.addRow(label, w)

        if label: 
            label_widget = layout.labelForField(w)
            # ================= 修复空指针报错 =================
            # 因为复选框使用了空标签占位，如果获取不到外部 Label，则单独加粗复选框自身文本
            if label_widget:
                font = label_widget.font()
                font.setBold(True)
                label_widget.setFont(font)
                label_widget.setStyleSheet("color: #34495E;")
            elif isinstance(w, QCheckBox):
                font = w.font()
                font.setBold(True)
                w.setFont(font)
                w.setStyleSheet("color: #34495E;")

        self.field_map[json_key] = {'widget': w, 'type': widget_type, 'label_widget': label_widget}

    def toggle_visibility(self, json_key, visible):
        if json_key in self.field_map:
            config = self.field_map[json_key]
            config['widget'].setVisible(visible)
            if config['label_widget']: config['label_widget'].setVisible(visible)

    def update_position_ui(self):
        idx = self.field_map['position']['widget'].currentIndex()
        self.toggle_visibility('depth', idx == 6)
        self.toggle_visibility('role', idx == 6)
        self.toggle_visibility('outletName', idx == 7)

    def update_recursion_ui(self):
        self.toggle_visibility('recursionLevel', self.field_map['delayUntilRecursion']['widget'].isChecked())

    def _create_tab_widget(self):
        """辅助方法，创建一个内边距舒适的 Tab 面板"""
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(18) # 表单项的垂直间距
        return tab, layout

    def setup_tabs(self):
        tab_basic, layout_basic = self._create_tab_widget()
        self.add_field(layout_basic, "条目标题/备忘录 (Comment):", "comment", "text")
        self.add_field(layout_basic, "主要关键字 (Keys) [逗号分隔]:", "key", "text") 
        self.add_field(layout_basic, "可选过滤器 (Optional Filter):", "keysecondary", "text") 
        self.add_field(layout_basic, "过滤器逻辑:", "selectiveLogic", "combo", items=["AND ANY (包含任一)", "AND ALL (包含所有)", "NOT ANY (不包含任一)", "NOT ALL (不包含所有)"])
        self.add_field(layout_basic, "条目内容 (Content):", "content", "content_editor") 
        self.add_field(layout_basic, "自动化 ID (Automation ID):", "automationId", "text") 
        
        layout_basic.addRow(QLabel("")) # 空行占位
        self.add_field(layout_basic, "✅ 启用此条目 (Enable)", "disable", "invert_bool") 
        self.add_field(layout_basic, "生效策略 (Strategy):", "strategy", "strategy_combo", items=["条件触发 (🟢 默认)", "常驻 (🔵 始终插入)", "向量化匹配 (🔗 相似度)"]) 
        self.tabs.addTab(tab_basic, "基础设定")

        tab_insert, layout_insert = self._create_tab_widget()
        self.add_field(layout_insert, "顺序 (Order):", "order", "int") 
        self.add_field(layout_insert, "触发策略/插入位置:", "position", "combo", items=["角色定义前", "角色定义后", "示例消息前", "示例消息后", "作者注释顶", "作者注释底", "@ D", "锚点 (Outlet)"]) 
        self.add_field(layout_insert, "↳ 深度在 (@ D):", "depth", "int") 
        self.add_field(layout_insert, "↳ 扮演角色 (Role):", "role", "combo", items=["⚙️ [系统]", "👤 [用户]", "🤖 [AI]"]) 
        self.add_field(layout_insert, "↳ 锚点名称 (Outlet Name):", "outletName", "text") 
        
        layout_insert.addRow(QLabel("")) 
        self.add_field(layout_insert, "扫描深度 (Scan Depth):", "scanDepth", "nullable_int") 
        self.add_field(layout_insert, "触发概率 (Trigger %):", "probability", "int", max=100) 
        self.add_field(layout_insert, "区分大小写 (Case Sensitive)", "caseSensitive", "tristate_combo") 
        self.add_field(layout_insert, "完整单词/全字匹配 (Match Whole Words)", "matchWholeWords", "tristate_combo") 
        
        layout_insert.addRow(QLabel("")) 
        self.add_field(layout_insert, "包含组 (Group):", "group", "text") 
        self.add_field(layout_insert, "组权重 (Group Weight):", "groupWeight", "int", max=10000) 
        self.add_field(layout_insert, "确定优先级 (Prioritize Inclusion)", "groupOverride", "bool") 
        self.add_field(layout_insert, "组评分 (Use Group Scoring)", "useGroupScoring", "tristate_combo") 
        
        layout_insert.addRow(QLabel("")) 
        self.add_field(layout_insert, "绑定到角色或标签 (Character Filter):", "characterFilter", "text") 
        self.add_field(layout_insert, "排除 (Exclude Filter)", "characterFilterExclude", "bool") 
        self.tabs.addTab(tab_insert, "插入与匹配")

        tab_adv, layout_adv = self._create_tab_widget()
        self.add_field(layout_adv, "筛选生成触发器 (Triggers):", "triggers", "multicheck", options={"normal": "正常", "continue": "继续", "impersonate": "扮演", "swipe": "滑动", "regenerate": "重新生成", "quiet": "静默"})
        
        layout_adv.addRow(QLabel("")) 
        self.add_field(layout_adv, "黏性 (Sticky):", "sticky", "int") 
        self.add_field(layout_adv, "冷却 (Cooldown):", "cooldown", "int") 
        self.add_field(layout_adv, "延迟 (Delay):", "delay", "int") 
        
        layout_adv.addRow(QLabel("")) 
        self.add_field(layout_adv, "不可递归 (不会被其他条目激活) (Exclude Recursion)", "excludeRecursion", "bool")
        self.add_field(layout_adv, "无视回复限额 (Ignore Budget)", "ignoreBudget", "bool")
        self.add_field(layout_adv, "防止进一步递归 (Prevent Recursion)", "preventRecursion", "bool") 
        self.add_field(layout_adv, "延迟到递归", "delayUntilRecursion", "bool") 
        self.add_field(layout_adv, "↳ 递归等级 (Recursion Level):", "recursionLevel", "int") 
        
        layout_adv.addRow(QLabel("")) 
        self.add_field(layout_adv, "匹配角色描述", "matchCharacterDescription", "bool") 
        self.add_field(layout_adv, "匹配角色备注", "matchCharacterDepthPrompt", "bool") 
        self.add_field(layout_adv, "匹配角色性格", "matchCharacterPersonality", "bool") 
        self.add_field(layout_adv, "匹配情景", "matchScenario", "bool") 
        self.add_field(layout_adv, "匹配用户设定描述", "matchPersonaDescription", "bool") 
        self.add_field(layout_adv, "匹配创作者注释", "matchCreatorNotes", "bool") 
        self.tabs.addTab(tab_adv, "其他")

    def new_file(self):
        if not self.check_unsaved_changes(): return
        self.world_info_data = {}
        self.current_file_path = None
        self.current_entry_key = None
        self.is_modified = False
        self.refresh_list()
        self.clear_form()
        self.setWindowTitle("SillyTavern 世界书编辑器 - [未命名新文件]")

    def open_file_dialog(self):
        if not self.check_unsaved_changes(): return
        file_path, _ = QFileDialog.getOpenFileName(self, "选择世界书文件", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            self.current_file_path = file_path
            self.load_data(file_path)

    def load_data(self, file_path):
        self.current_entry_key = None 
        try:
            backup_path = file_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(file_path, backup_path)
            
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.world_info_data = data.get("entries", {})
            self.refresh_list()
            self.setWindowTitle(f"SillyTavern 世界书编辑器 - {file_path}")
            self.is_modified = False 
        except Exception as e:
            QMessageBox.critical(self, "读取错误", f"无法读取文件:\n{str(e)}")

    def refresh_list(self):
        self.list_widget.clear()
        for key in self.world_info_data.keys():
            item = QListWidgetItem()
            item.setData(Qt.UserRole, key)
            self.list_widget.addItem(item)
        self.update_list_display()

    def update_list_display(self):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            key = item.data(Qt.UserRole)
            entry = self.world_info_data.get(key, {})
            
            display_name = entry.get("comment", "")
            if not display_name:
                keys = entry.get("key", [])
                display_name = ", ".join(keys) if keys else f"未命名条目 {key}"
                
            item.setText(f"[{i + 1}] {display_name}")

    def filter_list(self, text):
        search_text = text.lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            entry_key = item.data(Qt.UserRole)
            entry = self.world_info_data.get(entry_key, {})
            
            title = entry.get("comment", "").lower()
            keys = ", ".join(entry.get("key", [])).lower()
            keys_sec = ", ".join(entry.get("keysecondary", [])).lower()
            content = entry.get("content", "").lower()
            
            if search_text in title or search_text in keys or search_text in keys_sec or search_text in content:
                item.setHidden(False)
            else:
                item.setHidden(True)

    def reorder_dictionary(self, old_row, new_row):
        keys = list(self.world_info_data.keys())
        moved_key = keys.pop(old_row)
        keys.insert(new_row, moved_key)
        
        new_dict = {k: self.world_info_data[k] for k in keys}
        self.world_info_data = new_dict
        self.set_modified()
        self.update_list_display() 

    def on_item_dragged(self, old_row, new_row):
        self.save_current_ui_to_memory()
        self.reorder_dictionary(old_row, new_row)

    def move_to_index(self):
        current_row = self.list_widget.currentRow()
        if current_row < 0: return
        total = self.list_widget.count()
        new_row, ok = QInputDialog.getInt(self, "移动条目", f"输入新位置 (1 到 {total}):", current_row + 1, 1, total, 1)
        if ok and (new_row - 1) != current_row:
            self.save_current_ui_to_memory()
            target_index = new_row - 1
            item = self.list_widget.takeItem(current_row)
            self.list_widget.insertItem(target_index, item)
            self.list_widget.setCurrentRow(target_index)
            self.reorder_dictionary(current_row, target_index)
            self.on_item_clicked(item)

    def convert_chinese(self, target_lang):
        current_row = self.list_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "提示", "请先选择一个要转换的条目！")
            return
        mode_str = "简体" if target_lang == 'zh-cn' else "繁体"
        dialog = ConvertDialog(mode_str, self)
        if dialog.exec() != QDialog.Accepted: return
            
        conv_title, conv_keys, conv_content = dialog.get_selection()
        self.save_current_ui_to_memory()
        
        item = self.list_widget.currentItem()
        original_key = item.data(Qt.UserRole)
        original_data = self.world_info_data[original_key]
        new_data = json.loads(json.dumps(original_data)) 
        
        existing_keys = [int(k) for k in self.world_info_data.keys() if k.isdigit()]
        new_id = str(max(existing_keys) + 1) if existing_keys else "0"
        new_data["uid"] = int(new_id)
        
        suffix = " - 简" if target_lang == 'zh-cn' else " - 繁"
        if conv_title:
            new_data["comment"] = zhconv.convert(new_data.get("comment", ""), target_lang) + suffix
        else:
            new_data["comment"] = new_data.get("comment", "") + suffix
            
        if conv_keys:
            new_data["key"] = [zhconv.convert(k, target_lang) for k in new_data.get("key", [])]
            new_data["keysecondary"] = [zhconv.convert(k, target_lang) for k in new_data.get("keysecondary", [])]
            
        if conv_content:
            new_data["content"] = zhconv.convert(new_data.get("content", ""), target_lang)

        keys_list = list(self.world_info_data.keys())
        insert_idx = keys_list.index(original_key) + 1
        keys_list.insert(insert_idx, new_id)
        
        self.world_info_data[new_id] = new_data
        new_dict = {k: self.world_info_data.get(k) for k in keys_list}
        self.world_info_data = new_dict
        
        self.set_modified()
        self.refresh_list()
        self.list_widget.setCurrentRow(insert_idx)
        self.on_item_clicked(self.list_widget.currentItem())

    def add_entry(self):
        existing_keys = [int(k) for k in self.world_info_data.keys() if k.isdigit()]
        new_id = str(max(existing_keys) + 1) if existing_keys else "0"

        new_entry = {
            "uid": int(new_id), "key": [], "keysecondary": [], "comment": "新条目", "content": "",
            "constant": False, "vectorized": False, "selective": True, "selectiveLogic": 0,
            "addMemo": True, "order": 100, "position": 0, "disable": False, "ignoreBudget": False, 
            "excludeRecursion": False, "preventRecursion": False, "delayUntilRecursion": False, "recursionLevel": 0,
            "matchPersonaDescription": False, "matchCharacterDescription": False, "matchCharacterPersonality": False, 
            "matchCharacterDepthPrompt": False, "matchScenario": False, "matchCreatorNotes": False, 
            "probability": 100, "useProbability": True,
            "depth": 4, "outletName": "", "group": "", "groupOverride": False, "groupWeight": 100, "useGroupScoring": None, 
            "scanDepth": None, "automationId": "", "role": 0, "sticky": 0, "cooldown": 0, "delay": 0,
            "characterFilter": [], "characterFilterExclude": False, "triggers": [],
            "caseSensitive": None, "matchWholeWords": None 
        }

        self.world_info_data[new_id] = new_entry
        self.set_modified()
        self.refresh_list()
        self.list_widget.setCurrentRow(self.list_widget.count() - 1)
        self.on_item_clicked(self.list_widget.currentItem())

    def delete_entry(self):
        current_row = self.list_widget.currentRow()
        if current_row < 0: return
        reply = QMessageBox.question(self, '确认', '确定要删除吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            item = self.list_widget.item(current_row)
            key_to_del = item.data(Qt.UserRole)
            del self.world_info_data[key_to_del]
            self.current_entry_key = None
            self.list_widget.takeItem(current_row)
            self.clear_form()
            self.set_modified()
            self.update_list_display()

    def clear_form(self):
        for json_key, config in self.field_map.items():
            w, w_type = config['widget'], config['type']
            if w_type in ['text', 'content_editor', 'nullable_int']: w.clear() 
            elif w_type in ['bool', 'invert_bool']: w.setChecked(w_type == 'invert_bool') 
            elif w_type == 'int': w.setValue(0)
            elif w_type in ['combo', 'strategy_combo', 'tristate_combo']: w.setCurrentIndex(0) 
            elif w_type == 'multicheck':
                for cb in w.checkboxes.values(): cb.setChecked(False)

    def save_current_ui_to_memory(self):
        if not self.current_entry_key or self.current_entry_key not in self.world_info_data: return
        entry = self.world_info_data[self.current_entry_key]
        
        for json_key, config in self.field_map.items():
            w, w_type = config['widget'], config['type']
            
            if w_type in ['text', 'content_editor']:
                val = w.text() if w_type == 'text' else w.toPlainText()
                if json_key in ['key', 'keysecondary', 'characterFilter']:
                    entry[json_key] = [k.strip() for k in val.split(',')] if val.strip() else []
                else:
                    entry[json_key] = val
            elif w_type == 'bool': entry[json_key] = w.isChecked()
            elif w_type == 'invert_bool': entry[json_key] = not w.isChecked()
            elif w_type == 'int': entry[json_key] = w.value()
            elif w_type == 'nullable_int':
                text_val = w.text().strip()
                entry[json_key] = int(text_val) if text_val.isdigit() else None
            elif w_type == 'combo': entry[json_key] = w.currentIndex()
            elif w_type == 'tristate_combo':
                idx = w.currentIndex()
                if idx == 0: entry[json_key] = None     
                elif idx == 1: entry[json_key] = True   
                elif idx == 2: entry[json_key] = False  
            elif w_type == 'strategy_combo':
                idx = w.currentIndex()
                if idx == 1:   entry['constant'], entry['vectorized'], entry['selective'] = True, False, False
                elif idx == 2: entry['constant'], entry['vectorized'], entry['selective'] = False, True, True
                else:          entry['constant'], entry['vectorized'], entry['selective'] = False, False, True
            elif w_type == 'multicheck':
                entry[json_key] = [val for val, cb in w.checkboxes.items() if cb.isChecked()]

        self.update_list_display()

    def on_item_clicked(self, item):
        self.save_current_ui_to_memory()
        self.current_entry_key = item.data(Qt.UserRole)
        entry_data = self.world_info_data[self.current_entry_key]

        for config in self.field_map.values(): config['widget'].blockSignals(True)

        for json_key, config in self.field_map.items():
            w, w_type = config['widget'], config['type']
            val = entry_data.get(json_key)
            
            if w_type in ['text', 'content_editor']:
                if json_key in ['key', 'keysecondary', 'characterFilter']:
                    val_str = ", ".join(val) if isinstance(val, list) else ""
                else:
                    val_str = str(val) if val is not None else ""
                w.setText(val_str)
            elif w_type == 'bool': w.setChecked(bool(val))
            elif w_type == 'invert_bool': w.setChecked(not bool(val))
            elif w_type == 'int': w.setValue(int(val) if val is not None else 0)
            elif w_type == 'nullable_int': 
                w.setText(str(val) if val is not None else "")
            elif w_type == 'combo': w.setCurrentIndex(int(val) if val is not None else 0)
            elif w_type == 'tristate_combo':
                if val is None: w.setCurrentIndex(0)
                elif val is True: w.setCurrentIndex(1)
                elif val is False: w.setCurrentIndex(2)
            elif w_type == 'strategy_combo':
                if entry_data.get('constant'): w.setCurrentIndex(1)
                elif entry_data.get('vectorized'): w.setCurrentIndex(2)
                else: w.setCurrentIndex(0)
            elif w_type == 'multicheck':
                val_list = val if isinstance(val, list) else []
                for opt_val, cb in w.checkboxes.items():
                    cb.setChecked(opt_val in val_list)
        
        for config in self.field_map.values(): config['widget'].blockSignals(False)
        self.update_position_ui()
        self.update_recursion_ui()

    def save_file(self):
        if not self.current_file_path:
            return self.save_as_file()
            
        self.save_current_ui_to_memory()
        save_data = {"entries": self.world_info_data}
        try:
            with open(self.current_file_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, separators=(',', ':'))
            self.is_modified = False
            self.setWindowTitle(f"SillyTavern 世界书编辑器 - {self.current_file_path}")
            QMessageBox.information(self, "成功", "世界书文件已成功保存！")
            return True
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"错误信息:\n{str(e)}")
            return False

    def save_as_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "另存为", "", "JSON Files (*.json)")
        if file_path:
            self.current_file_path = file_path
            return self.save_file()
        return False

    def check_unsaved_changes(self):
        if not self.is_modified: return True
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("未保存的更改")
        msg_box.setText("您有未保存的更改。请问要如何处理？")
        btn_save = msg_box.addButton("保存并退出", QMessageBox.AcceptRole)
        btn_save_as = msg_box.addButton("另存为...", QMessageBox.AcceptRole)
        btn_discard = msg_box.addButton("直接退出", QMessageBox.DestructiveRole)
        btn_cancel = msg_box.addButton("取消", QMessageBox.RejectRole)
        
        msg_box.exec()
        
        if msg_box.clickedButton() == btn_save: return self.save_file()
        elif msg_box.clickedButton() == btn_save_as: return self.save_as_file()
        elif msg_box.clickedButton() == btn_discard: return True
        else: return False

    def closeEvent(self, event: QCloseEvent):
        if self.check_unsaved_changes(): event.accept()
        else: event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
