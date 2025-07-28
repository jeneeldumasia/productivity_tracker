# Automated Productivity Tracker v7

This version of the productivity tracker has been refactored into a modular structure for better maintainability and scalability. It includes an enhanced glassmorphism UI, theme management, and stubs for cross-platform support.

## Features

-   **Modular Codebase**: UI, data logic, and tracking are separated into modules.
-   **Enhanced Glassmorphism UI**: A blurred background and translucent cards create a modern "glass" effect.
-   **Light/Dark Theme**: A robust theme manager allows for easy toggling between light and dark modes.
-   **Live Analytics**: A real-time dashboard with a pie chart visualizes application usage.
-   **Activity Log**: A detailed, filterable log of all tracked activities.
-   **Data Export**: Export all activity data to a CSV file.
-   **Cross-Platform Stubs**: Includes placeholders to add support for macOS and Linux window tracking.

## Setup and Installation

1.  **Prerequisites**:
    * Python 3.6+
    * Git (optional, for cloning)

2.  **Clone the repository (optional)**:
    ```bash
    git clone <repository-url>
    cd productivity_tracker
    ```

3.  **Create a Virtual Environment** (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

4.  **Install Dependencies**:
    Create a `requirements.txt` file with the following content:

    ```
    pyqt5
    pandas
    matplotlib
    # --- Windows Only ---
    pywin32
    # --- macOS/Linux (for future support) ---
    # py-get-active-window
    # python-xlib
    ```

    Then, install the packages:
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

Execute the main entry point of the application:

```bash
python main.py