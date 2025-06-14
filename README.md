⚖️ Compliance Assistant Bot

An AI-powered Compliance Assistant leveraging **AWS Bedrock** and **Kendra** to answer regulatory questions in areas such as AML, KYC, trading, and reporting. It offers a user-friendly interface via **Streamlit**, a CLI option, and is also deployable as an **AWS Lambda** API.

## 🚀 Features

- 📘 LLM-based responses via AWS Bedrock (Claude 3)
- 🔍 Retrieval Augmented Generation (RAG) using AWS Kendra (optional)
- 🧠 Predefined compliance knowledge base
- 🌐 Streamlit web UI
- 💻 Command-line interface (CLI)
- ☁️ AWS Lambda support

## 📁 Project Structure
├── app.py # Main source code (provided above)

├── .env # AWS and app configuration

├── README.md # Project documentation (this file)


🔧 Setup Instructions

1. Clone the repository
git clone https://github.com/jhayush0502/Compliance_Bot.git
cd Compliance_Bot


2. Create .env file
# .env
# refer example.env
Note: Ensure you have the correct permissions for AWS Bedrock and Kendra APIs.


3. Install dependencies
pip install -r requirements.txt
# Developed using python 3.10.9

🖥️ Run Locally with Streamlit
streamlit run app.py
Visit http://localhost:8501 in your browser.

Enter compliance-related questions interactively.


☁️ AWS Lambda Deployment
Use the lambda_handler function for deploying as an AWS Lambda function behind API Gateway.

Lambda Handler Signature:
def lambda_handler(event, context):

Example Payload (POST)
{
  "question": "What are the STR reporting requirements?",
  "use_rag": true
}

Response Structure
{
  "question": "...",
  "answer": "...",
  "rag_used": true,
  "context_sources": [...],
  "timestamp": "..."
}


🧪 Sample Questions
1) AML: What are STR reporting requirements?

2) KYC: What is enhanced due diligence?

3) Trading: What constitutes market manipulation?

4) Reporting: What are the penalties for late reporting?



⚠️ Disclaimer
This bot provides general compliance guidance using AI. It is not a substitute for legal advice. Please consult your compliance/legal team for regulatory decisions.