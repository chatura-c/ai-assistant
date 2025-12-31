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
    background: #2b2b2b;    /* Background of the scrollbar track */
    width: 10px;            /* Narrower for a sleek look */
    margin: 0px 0px 0px 0px;
    border-radius: 5px;
}

/* The actual handle that moves */
QScrollBar::handle:vertical {
    background: #5c5c5c;    /* Subtle grey */
    min-height: 30px;
    border-radius: 5px;
}

/* Handle color on hover */
QScrollBar::handle:vertical:hover {
    background: #888888;
}

/* Hide the top and bottom arrows */
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    height: 0px;
}

/* Removes the background area above and below the handle */
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
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

