def get_clean_app_name(window_title):
    """Cleans the window title to get a more consistent application name."""
    if not window_title or not isinstance(window_title, str) or window_title.strip() == "":
        return "Idle/No Window"
        
    lower_title = window_title.lower()
    
    known_apps = {
        "google chrome": "Google Chrome", "mozilla firefox": "Mozilla Firefox", 
        "microsoft edge": "Microsoft Edge", "file explorer": "File Explorer", 
        "visual studio code": "VS Code", "vscode": "VS Code", "pycharm": "PyCharm",
        "slack": "Slack", "zoom": "Zoom", "terminal": "Terminal/CMD", 
        "cmd.exe": "Terminal/CMD", "powershell": "Terminal/CMD"
    }

    for key, value in known_apps.items():
        if key in lower_title:
            return value

    # Fallback to splitting by common separators
    if " - " in window_title:
        app_name = window_title.split(" - ")[-1].strip()
        if app_name: return app_name
    
    if " | " in window_title:
        app_name = window_title.split(" | ")[-1].strip()
        if app_name: return app_name
            
    return window_title.strip()