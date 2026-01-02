# AIT Chemistry Classes Website

A modern, responsive website for **AIT Chemistry Classes** in Vadodara, Gujarat, led by **Ashwin Sir**.

## Features

-   **Glassmorphism UI**: Premium iOS-style design with frosted glass panels.
-   **Notes Management System**: Admin can upload PDF notes; students can view/download them.
-   **Enquiry System**: Students can send enquiries; Admin can view them.
-   **Responsive Design**: Mobile-friendly slide-in navigation and optimized layouts.

## Tech Stack

-   **Backend**: Python (Flask)
-   **Database**: SQLite
-   **Frontend**: HTML, CSS (Glassmorphism), JavaScript

## Local Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/polerflyer69/AIT-chemistry-website.git
    cd AIT-chemistry-website
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the database**:
    ```bash
    python init_db.py
    ```

5.  **Run the application**:
    ```bash
    python app.py
    ```
    Visit `http://127.0.0.1:5000` in your browser.

## Deployment (Render)

This project is configured for deployment on [Render](https://render.com).

1.  Push this repository to GitHub.
2.  In Render dashboard, click **New +** -> **Blueprint**.
3.  Connect your repository.
4.  Render will automatically detect `render.yaml` and configure the service.
5.  **Note**: Since SQLite is file-based, data will not persist across re-deployments on the free tier. For persistent storage, upgrade to a disk-enabled service or switch to PostgreSQL.

## Admin Access

-   **URL**: `/login`
-   **Default Credentials**: `admin` / `admin123` (Change strictly for production!)
