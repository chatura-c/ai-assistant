bubble_base_style = """
QTextBrowser {
    border-radius: 15px;
    padding: 10px;
    background-color: %s;
    border: 1.5px solid %s;
    color: %s;
}
"""

assistant_style = bubble_base_style % ("#FFFFAA", "#888888", "black")

user_style = bubble_base_style % ("#E1F5FE", "#03A9F4", "#333")

scrollbar_style = """
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 6px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: rgba(100, 100, 100, 80);
    min-height: 20px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(100, 100, 100, 150);
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
copy_button_style = """
QPushButton {
    background-color: rgba(0, 0, 0, 40);
    border: none;
    border-radius: 10px;
    color: white;
    font-size: 9px;
}
QPushButton:hover {
    background-color: #03A9F4;
}
"""

context_bar_style = """
#ContextBar {
    background-color: rgba(255, 255, 255, 180);
    border-top: 1px solid #ddd;
    border-radius: 10px 10px 0px 0px;
}
#ContextLabel {
    color: #eee;
    font-size: 11px;
    padding: 5px;
}
"""

context_btn_style = """
QPushButton {
    background: rgba(0, 0, 0, 20);
    border: none;
    border-radius: 4px;
    color: #555;
    font-size: 10px;
    padding: 2px 5px;
}
QPushButton:hover {
    background: rgba(0, 0, 0, 40);
}
"""

