# JU-IIC Lab Inventory System

A full-stack smart inventory management system designed for the Electrical and Computer Engineering labs at Jimma University, under the JU-IIC Innovation Program.

## Features
- **Role-Based Access:** Admin, Storekeeper, Technician, Viewer
- **AI Item Recognition:** Scan items with a camera to identify them.
- **QR Code System:** Generate and scan QR labels.
- **Stock Management:** Track component stock-in and stock-out.
- **Borrowing System:** Issue and return equipment.
- **Reporting:** Export PDF and Excel reports.
- **Password Reset:** Secure email-based password reset.

## Tech Stack
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Backend:** Python (Flask), SQLAlchemy
- **Database:** SQLite
- **Libraries:** OpenPyXL, ReportLab, qrcode, Pillow

## How to Run Locally

### 1. Backend Setup
\`\`\`bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
\`\`\`

Rename `.env.example` to `.env` and fill in your details.

Initialize the database and seed it:
\`\`\`bash
python run.py       # Runs once to create tables
python seed_data.py # Loads sample users, equipment, and components
python run.py       # Starts the server
\`\`\`

### 2. Frontend Setup
Open a new terminal:
\`\`\`bash
cd frontend
python -m http.server 5500
\`\`\`

### 3. Access the App
Open your browser and go to: `http://localhost:5500`

**Default Admin Login:**
- Email: `abebe@lab.edu`
- Password: `password123`