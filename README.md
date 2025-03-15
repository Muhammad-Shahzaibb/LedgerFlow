# LedgerFlow - Automated Financial Accounting System

LedgerFlow is a **Flask-based financial accounting system** designed to **automate invoice processing and ledger management**. It utilizes **Google's Gemini API** for intelligent invoice extraction and **Retrieval-Augmented Generation (RAG)** for insightful financial analysis. The system is containerized using **Docker**, making it easily deployable.

## 🚀 Features

### 🔹 Automated Invoice Processing
- Uses **Google’s Gemini API** to extract key invoice details:  
  **Sender, Receiver, Invoice Number, Date, Due Date, and Total Amount**.
- Supports **multiple invoice formats** for seamless processing.

### 🔹 Ledger Management
- Stores invoices in **MySQL database** with **CRUD operations**.
- Provides a **detailed financial overview**, tracking revenue, expenses, and payments.

### 🔹 AI-Powered Insights (RAG)
- Implements **Retrieval-Augmented Generation (RAG)** to analyze financial records.
- Generates **summaries on revenue, expenses, and profits**.

### 🔹 User-Friendly Interface
- Web-based UI for **uploading invoices and viewing ledger entries**.
- Simple, clean, and easy-to-navigate dashboard.

### 🔹 Dockerized Deployment
- The entire application is **containerized** using Docker.
- Ensures easy deployment, scalability, and minimal configuration.

---

## 📌 Prerequisites

Before running the project, ensure you have:

- **Docker & Docker Compose** installed  
  *(Install from: [Docker Official Site](https://www.docker.com/))*
- **Python 3.9+** (for local setup without Docker)
- **MySQL 8.0+** (Docker handles this)

---

## 🛠️ Setup & Installation

### 🐳 Run with Docker (Recommended)

1. **Clone the Repository**
   ```sh
   git clone https://github.com/Muhammad-Shahzaibb/LedgerFlow.git
   cd LedgerFlow

2. **Build & Start Containers**
   ```sh
   docker-compose up --build

3. **Open your browser and go to:**
   🔗 http://localhost:5000
