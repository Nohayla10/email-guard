# EmailGuard: AI-Powered Spam & Phishing Detection Toolkit

![EmailGuard Architecture Diagram](docs/architecture.png)

## Overview

EmailGuard is a comprehensive toolkit designed to classify emails as "legitimate," "spam," or "phishing" using a machine learning model. It offers a flexible solution with both a command-line interface (CLI) for quick, on-demand scanning and a robust Flask-based RESTful API for seamless integration into larger applications or services.

Built with `scikit-learn` and `Flask`, EmailGuard aims to provide a reliable first line of defense against unwanted and malicious emails by leveraging natural language processing and machine learning techniques.

## Features

* **Intelligent Classification:** Uses a trained machine learning model to accurately categorize emails.
* **Dual Interface:** Access functionality via a simple command-line tool or a RESTful API.
* **Robust Text Preprocessing:** Handles noisy email data by cleaning, normalizing, and transforming text for optimal model performance.
* **Comprehensive Documentation:** Detailed guides for setup, usage, and internal architecture.
* **Security Considerations:** Built with an awareness of security best practices, including API key authentication.

## Live Demo

* **Frontend (Web App):** [YOUR_DEPLOYED_FRONTEND_URL_HERE] (e.g., Vercel URL)
* **Backend (API Base URL):** [YOUR_DEPLOYED_BACKEND_URL_HERE] (e.g., Render/Railway URL)

## Getting Started

To get EmailGuard up and running on your local machine, follow these steps.

### 1. Clone the Repository

```bash
git clone https://github.com/Nohayla10/email-guard.git
cd email_guard