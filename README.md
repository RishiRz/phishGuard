# 🛡️ PhishGuard – AI-Powered Phishing Email Detection System

**PhishGuard** is an intelligent phishing email detection system designed to identify suspicious and malicious emails using Machine Learning, URL analysis, and email security checks.

The system analyzes email content, sender information, URLs, and authentication-related headers to detect potential phishing attempts and classify emails based on their security risk.

---

## 🚀 Features

- **AI-Based Email Detection:** Uses a Machine Learning model to classify emails as phishing or legitimate.
- **Email Content Analysis:** Examines email subject, sender, and message body for suspicious patterns.
- **URL Analysis:** Identifies potentially malicious or suspicious links embedded in emails.
- **Email Header Analysis:** Supports SPF, DKIM, and DMARC-related security checks.
- **Risk Assessment:** Generates a risk score and risk level for analyzed emails.
- **Email File Upload:** Supports uploading `.eml` email files for analysis.
- **Detailed Analysis Report:** Provides classification results, risk scores, and reasons behind the detection.
- **Interactive Web Interface:** Provides a user-friendly interface for analyzing emails.

---

## 🧰 Technology Stack

| Component | Technology |
|---|---|
| Frontend | React.js, TypeScript |
| Build Tool | Vite |
| Backend | Python, FastAPI |
| Machine Learning | Scikit-learn |
| NLP / Text Processing | TF-IDF Vectorization |
| Model | Machine Learning Classification Model |
| API Communication | REST API |
| Development Environment | VS Code |

---

## 🏗️ System Architecture

PhishGuard follows a frontend-backend architecture where the frontend collects email data and communicates with the backend through REST APIs.

1. **Input:** User enters email details or uploads an `.eml` file.
2. **Preprocessing:** Email content is extracted and cleaned.
3. **Feature Extraction:** TF-IDF converts email text into numerical features.
4. **Machine Learning Analysis:** The trained model predicts whether the email is phishing or legitimate.
5. **Security Analysis:** URLs and available email authentication information are examined.
6. **Risk Calculation:** Different analysis components contribute to the final risk score.
7. **Output:** The system displays the classification, risk level, score, and detection reasons.

---

## 🧠 Machine Learning Model

PhishGuard uses TF-IDF (Term Frequency–Inverse Document Frequency) to transform email text into numerical representations for machine learning classification.

The model is trained using a labeled email dataset containing phishing/spam and legitimate email samples.

### Dataset Distribution

| Category | Number of Samples |
|---|---:|
| Phishing / Spam | 21,842 |
| Legitimate | 17,312 |
| **Total** | **39,154** |

### Model Evaluation Results

The reported model evaluation metrics are:

| Metric | Score |
|---|---:|
| Accuracy | 99.40% |
| Precision | — |
| Recall | — |
| F1-Score | 99.46% |
| ROC-AUC | 99.95% |

*Precision and recall values are not listed here because their exact reported values have not been provided.*

### Risk Scoring

The system uses a weighted risk assessment approach:

| Analysis Component | Weight |
|---|---:|
| Email Content / Rules | 40% |
| URL Analysis | 20% |
| Email Header Analysis | 10% |
| Machine Learning | 30% |
| **Total** | **100%** |

---

## 📂 Project Structure

```text
PhishGuard/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── App.tsx
│   │   └── ...
│   ├── package.json
│   └── vite.config.ts
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── ...
│   └── requirements.txt
│
├── ml/
│   ├── models/
│   │   ├── spam_model.pkl
│   │   └── ...
│   └── ...
│
├── README.md
└── .gitignore
```

*The structure above is a representative layout. Adjust it to match your actual repository.*

---

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.10+
- Node.js and npm
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/USERNAME/PhishGuard.git
cd PhishGuard
```

### 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend API:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### 3. Frontend Setup

Open another terminal and navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open the local URL displayed by Vite in your browser.

---

## 📊 Sample Analysis Output

The system generates an analysis result containing:

- Email classification (Phishing / Legitimate)
- Risk score
- Risk level
- Suspicious URLs
- Email authentication analysis
- Reasons for the classification

---

## 🔐 Security Considerations

- Never open suspicious links directly.
- Avoid uploading emails containing sensitive personal information to untrusted deployments.
- Validate and sanitize uploaded email files.
- Keep API credentials and environment variables outside version control.
- Use authorized and trusted datasets for model training.

---

## 🔮 Future Enhancements

- Real-time email monitoring.
- Browser extension integration.
- Advanced phishing URL detection.
- Improved detection using deep learning and transformer-based models.
- Integration with threat intelligence feeds.
- Email security dashboard and historical analysis.
- Enhanced SPF, DKIM, and DMARC validation.

---

## 🎯 Project Objective

The primary objective of PhishGuard is to improve email security by leveraging machine learning and automated security analysis to identify phishing attempts, reduce the risk of email-based attacks, and help users make safer decisions.

---

## 👨‍💻 Author

**Rishiraj Deka**

Cybersecurity Enthusiast | Python Developer | Security Researcher

---

## ⚠️ Disclaimer

PhishGuard is developed for educational, research, and defensive cybersecurity purposes. Its results should be treated as security indicators rather than a guarantee that an email is safe or malicious.

---

⭐ If you find this project useful, consider giving the repository a star!