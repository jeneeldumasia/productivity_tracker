def get_stylesheet(is_dark):
    """Returns the appropriate QSS stylesheet for the selected theme."""
    
    # Base styles are shared across both themes
    base_style = """
        #backgroundWidget {
            background-color: #1D2B64; /* Fallback color */
        }
        #navPane {
            background-color: rgba(0, 0, 0, 0.3);
            border-right: 1px solid rgba(255, 255, 255, 0.2);
        }
        #navButton, #menuButton, #headerTitle { color: white; }
        #navButton { background-color: transparent; border: none; padding: 12px; text-align: left; font-size: 14px; font-weight: bold; }
        #navButton:hover { background-color: rgba(255, 255, 255, 0.1); }
        #menuButton { font-size: 22px; font-weight: bold; border: none; background-color: transparent; }
        #headerTitle { font-size: 26px; font-weight: bold; }
        #pageScrollArea { border: none; background: transparent; }
        #headerButton { font-size: 20px; font-weight: bold; color: white; background-color: transparent; border: none; }
    """

    combo_box_style = """
        QComboBox { padding: 5px; border-radius: 5px; }
        QComboBox::drop-down { border: none; }
        QComboBox QAbstractItemView { border-radius: 5px; padding: 5px; }
    """

    if is_dark:
        theme_style = """
            #glassCard { background-color: rgba(0, 0, 0, 0.25); border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.15); }
            QDialog { background-color: #2c2c2c; }
            QGroupBox { color: #E0E0E0; border-color: rgba(255, 255, 255, 0.2); }
            QGroupBox::title { color: #E0E0E0; }
            QLabel, h1, QDialog QLabel { color: #F0F0F0; background-color: transparent; }
            QLineEdit, QSpinBox, QDateEdit, QTextEdit, QTableWidget, QComboBox {
                background-color: rgba(0, 0, 0, 0.2); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 5px; padding: 5px; color: #F0F0F0;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(30, 30, 30, 0.95); border: 1px solid rgba(255, 255, 255, 0.2); color: #F0F0F0;
            }
            QComboBox QAbstractItemView::item:hover { background-color: rgba(255, 255, 255, 0.1); }
            QTableWidget { alternate-background-color: rgba(255, 255, 255, 0.03); gridline-color: rgba(255, 255, 255, 0.1); }
            QPushButton, QDialogButtonBox QPushButton { background-color: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); color: white; padding: 8px; border-radius: 5px; min-width: 80px; }
            QPushButton:hover, QDialogButtonBox QPushButton:hover { background-color: rgba(255, 255, 255, 0.2); }
            QHeaderView::section { background-color: rgba(0, 0, 0, 0.3); color: white; border: none; padding: 5px; }
        """
    else: # Light Mode
        theme_style = """
            #glassCard { background-color: rgba(255, 255, 255, 0.25); border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.4); }
            QDialog { background-color: #F5F7FA; }
            QGroupBox { color: #333; border-color: rgba(0, 0, 0, 0.1); }
            QGroupBox::title { color: #333; }
            QLabel, h1, QDialog QLabel { color: #222; background-color: transparent; }
            QLineEdit, QSpinBox, QDateEdit, QTextEdit, QTableWidget, QComboBox {
                background-color: rgba(255, 255, 255, 0.5); border: 1px solid rgba(0, 0, 0, 0.1); border-radius: 5px; padding: 5px; color: #333;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(240, 240, 240, 0.95); border: 1px solid rgba(0, 0, 0, 0.1); color: #333;
            }
            QComboBox QAbstractItemView::item:hover { background-color: rgba(0, 0, 0, 0.1); }
            QTableWidget { alternate-background-color: rgba(0, 0, 0, 0.03); gridline-color: rgba(0, 0, 0, 0.1); }
            QPushButton, QDialogButtonBox QPushButton { background-color: rgba(0, 0, 0, 0.05); border: 1px solid rgba(0, 0, 0, 0.1); color: #333; padding: 8px; border-radius: 5px; min-width: 80px;}
            QPushButton:hover, QDialogButtonBox QPushButton:hover { background-color: rgba(0, 0, 0, 0.1); }
            QHeaderView::section { background-color: rgba(255, 255, 255, 0.3); color: #333; border: none; padding: 5px; }
        """

    return base_style + combo_box_style + theme_style