import os
import json
import boto3
import streamlit as st
from typing import Optional, Dict, Any
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComplianceAssistantBot:
    """
    LLM-Powered Compliance Assistant Bot using AWS Bedrock
    """
    
    def __init__(self):
        """Initialize the compliance bot with AWS services"""
        self.setup_aws_clients()
        self.setup_compliance_knowledge()
        
    def setup_aws_clients(self):
        """Setup AWS clients for Bedrock and Kendra"""
        try:
            # Debug: Print environment variables to verify they're loaded
            print("=== Environment Variables Debug ===")
            print(f"AWS_ACCESS_KEY_ID: {os.getenv('AWS_ACCESS_KEY_ID', 'NOT_FOUND')}")
            print(f"AWS_SECRET_ACCESS_KEY: {'***' + os.getenv('AWS_SECRET_ACCESS_KEY', 'NOT_FOUND')[-4:] if os.getenv('AWS_SECRET_ACCESS_KEY') else 'NOT_FOUND'}")
            print(f"AWS_REGION: {os.getenv('AWS_REGION', 'NOT_FOUND')}")
            print(f"BEDROCK_MODEL_ID: {os.getenv('BEDROCK_MODEL_ID', 'NOT_FOUND')}")
            print(f"KENDRA_INDEX_ID: {os.getenv('KENDRA_INDEX_ID', 'NOT_FOUND')}")
            print("=" * 35)
            
            # AWS Configuration
            self.aws_config = {
                'region_name': os.getenv('AWS_REGION', 'us-east-1'),
                'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
                'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY')
            }
            
            # Validate required credentials
            if not self.aws_config['aws_access_key_id'] or not self.aws_config['aws_secret_access_key']:
                raise ValueError("AWS credentials not found. Please check your .env file.")
            
            # Initialize Bedrock client for LLM
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                **self.aws_config
            )
            
            # Initialize Kendra client for RAG (optional)
            self.kendra_client = boto3.client(
                'kendra',
                **self.aws_config
            )
            
            # Model configuration
            self.model_config = {
                'model_id': os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0'),
                'max_tokens': int(os.getenv('BEDROCK_MAX_TOKENS', '2000')),
                'temperature': float(os.getenv('BEDROCK_TEMPERATURE', '0.7')),
                'kendra_index_id': os.getenv('KENDRA_INDEX_ID', 'salespitch'),
                'min_confidence_score': float(os.getenv('KENDRA_MIN_CONFIDENCE_SCORE', '0.3'))
            }
            
            logger.info("AWS clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing AWS clients: {str(e)}")
            raise
    
    def setup_compliance_knowledge(self):
        """Define compliance knowledge scope and common scenarios"""
        self.compliance_topics = {
            'aml': [
                'What are STR reporting requirements?',
                'When should an account be flagged for AML?',
                'What are the key AML red flags?',
                'How long should AML records be retained?'
            ],
            'trading': [
                'What is considered circular trading?',
                'What are insider trading regulations?',
                'What constitutes market manipulation?',
                'What are pre-trade compliance checks?'
            ],
            'kyc': [
                'What documents are required for KYC?',
                'How often should KYC be updated?',
                'What is enhanced due diligence?',
                'When is simplified due diligence applicable?'
            ],
            'reporting': [
                'What are regulatory reporting timelines?',
                'Which transactions require immediate reporting?',
                'What are the penalties for late reporting?',
                'How should suspicious activities be documented?'
            ]
        }
    
    def create_compliance_prompt(self, question: str, context: Optional[str] = None) -> str:
        """
        Create a comprehensive prompt for compliance questions
        """
        base_prompt = f"""You are an expert compliance officer assistant with deep knowledge of financial regulations, AML (Anti-Money Laundering), KYC (Know Your Customer), trading compliance, and regulatory reporting requirements.

Your role is to provide accurate, actionable guidance on compliance matters while being clear about when additional legal consultation may be needed.

Guidelines for your responses:
1. Provide clear, structured answers
2. Include relevant regulatory references when applicable
3. Highlight key action items or requirements
4. Mention potential consequences of non-compliance
5. Suggest when to consult legal counsel for complex matters
6. Use bullet points for clarity when listing requirements

Question: {question}

{f"Additional Context: {context}" if context else ""}

Please provide a comprehensive answer that addresses all aspects of this compliance question."""

        return base_prompt
    
    def query_bedrock_llm(self, prompt: str) -> str:
        """
        Query AWS Bedrock LLM for compliance answers
        """
        try:
            # Prepare the request body for Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.model_config['max_tokens'],
                "temperature": self.model_config['temperature'],
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Make the API call to Bedrock
            response = self.bedrock_client.invoke_model(
                modelId=self.model_config['model_id'],
                body=json.dumps(request_body),
                contentType='application/json'
            )
            
            # Parse the response
            response_body = json.loads(response['body'].read())
            answer = response_body['content'][0]['text']
            
            logger.info("Successfully received response from Bedrock")
            return answer
            
        except Exception as e:
            logger.error(f"Error querying Bedrock: {str(e)}")
            return f"I apologize, but I encountered an error while processing your question: {str(e)}"
    
    def query_kendra_rag(self, question: str) -> Optional[Dict[str, Any]]:
        """
        Query AWS Kendra for additional context (RAG implementation)
        """
        try:
            response = self.kendra_client.query(
                IndexId=self.model_config['kendra_index_id'],
                QueryText=question,
                PageSize=5
            )
            
            # Filter results by confidence score
            relevant_results = []
            for result in response.get('ResultItems', []):
                if result.get('ScoreAttributes', {}).get('ScoreConfidence') == 'HIGH':
                    relevant_results.append({
                        'text': result.get('DocumentExcerpt', {}).get('Text', ''),
                        'title': result.get('DocumentTitle', {}).get('Text', ''),
                        'confidence': result.get('ScoreAttributes', {}).get('ScoreConfidence', '')
                    })
            
            return relevant_results if relevant_results else None
            
        except Exception as e:
            logger.error(f"Error querying Kendra: {str(e)}")
            return None
    
    def get_compliance_answer(self, question: str, use_rag: bool = True) -> Dict[str, Any]:
        """
        Main method to get compliance answers with optional RAG
        """
        try:
            # Step 1: Try to get additional context from Kendra (RAG)
            context = None
            rag_used = False
            
            if use_rag:
                kendra_results = self.query_kendra_rag(question)
                if kendra_results:
                    context = "\n".join([f"- {result['text']}" for result in kendra_results[:3]])
                    rag_used = True
            
            # Step 2: Create the prompt with or without RAG context
            prompt = self.create_compliance_prompt(question, context)
            
            # Step 3: Get answer from Bedrock LLM
            answer = self.query_bedrock_llm(prompt)
            
            # Step 4: Return structured response
            return {
                'question': question,
                'answer': answer,
                'rag_used': rag_used,
                'context_sources': kendra_results if rag_used else None,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting compliance answer: {str(e)}")
            return {
                'question': question,
                'answer': f"I apologize, but I encountered an error: {str(e)}",
                'rag_used': False,
                'context_sources': None,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_sample_questions(self) -> Dict[str, list]:
        """Return sample questions by category"""
        return self.compliance_topics

def create_streamlit_app():
    """
    Create Streamlit frontend for the Compliance Assistant Bot
    """
    st.set_page_config(
        page_title="Compliance Assistant Bot",
        page_icon="⚖️",
        layout="wide"
    )
    
    st.title("⚖️ Compliance Assistant Bot")
    st.markdown("**Your AI-powered compliance expert for regulatory questions**")
    
    # Initialize the bot
    if 'bot' not in st.session_state:
        try:
            st.session_state.bot = ComplianceAssistantBot()
            st.success("✅ Compliance Assistant Bot initialized successfully!")
        except Exception as e:
            st.error(f"❌ Error initializing bot: {str(e)}")
            st.stop()
    
    # Sidebar with sample questions
    with st.sidebar:
        st.header("📋 Sample Questions")
        sample_questions = st.session_state.bot.get_sample_questions()
        
        for category, questions in sample_questions.items():
            st.subheader(f"{category.upper()}")
            for question in questions:
                if st.button(question, key=f"sample_{category}_{question[:20]}"):
                    st.session_state.current_question = question
        
        st.markdown("---")
        st.subheader("⚙️ Settings")
        use_rag = st.checkbox("Use RAG (Kendra Search)", value=True, 
                             help="Enable to search through uploaded compliance documents")
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Ask Your Compliance Question")
        
        # Use session state question if available
        default_question = st.session_state.get('current_question', '')
        question = st.text_area(
            "Enter your compliance-related question:",
            value=default_question,
            height=100,
            placeholder="e.g., What are the STR reporting requirements for suspicious transactions?"
        )
        
        if st.button("🔍 Get Answer", type="primary"):
            if question.strip():
                with st.spinner("🤔 Analyzing your compliance question..."):
                    result = st.session_state.bot.get_compliance_answer(question, use_rag)
                    
                    # Display the answer
                    st.markdown("### 📝 Answer")
                    st.markdown(result['answer'])
                    
                    # Display additional information
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.info(f"**RAG Used:** {'✅ Yes' if result['rag_used'] else '❌ No'}")
                    with col_info2:
                        st.info(f"**Timestamp:** {result['timestamp']}")
                    
                    # Display sources if RAG was used
                    if result['rag_used'] and result['context_sources']:
                        with st.expander("📚 Additional Context Sources"):
                            for i, source in enumerate(result['context_sources'], 1):
                                st.markdown(f"**Source {i}:** {source['title']}")
                                st.markdown(f"*Confidence: {source['confidence']}*")
                                st.markdown(f"```{source['text'][:200]}...```")
                                st.markdown("---")
            else:
                st.warning("⚠️ Please enter a question first!")
    
    with col2:
        st.subheader("ℹ️ About")
        st.markdown("""
        This Compliance Assistant Bot helps you with:
        
        **🎯 Core Areas:**
        - Anti-Money Laundering (AML)
        - Know Your Customer (KYC)
        - Trading Compliance
        - Regulatory Reporting
        
        **🔧 Features:**
        - AI-powered responses via AWS Bedrock
        - Optional document search via AWS Kendra
        - Real-time compliance guidance
        
        **⚠️ Important Note:**
        This bot provides general guidance. Always consult with legal counsel for specific compliance matters.
        """)

# AWS Lambda handler for API deployment
def lambda_handler(event, context):
    """
    AWS Lambda handler for API-based deployment
    """
    try:
        # Initialize the bot
        bot = ComplianceAssistantBot()
        
        # Extract question from event
        if event.get('httpMethod') == 'POST':
            body = json.loads(event.get('body', '{}'))
            question = body.get('question', '')
            use_rag = body.get('use_rag', True)
        else:
            # GET request - extract from query parameters
            question = event.get('queryStringParameters', {}).get('question', '')
            use_rag = event.get('queryStringParameters', {}).get('use_rag', 'true').lower() == 'true'
        
        if not question:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Question parameter is required'})
            }
        
        # Get the answer
        result = bot.get_compliance_answer(question, use_rag)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }

# CLI interface
def cli_interface():
    """
    Command-line interface for the Compliance Assistant Bot
    """
    print("⚖️ Compliance Assistant Bot - CLI Mode")
    print("="*50)
    
    try:
        bot = ComplianceAssistantBot()
        print("✅ Bot initialized successfully!")
        
        while True:
            print("\n💬 Ask your compliance question (or type 'quit' to exit):")
            question = input("> ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not question:
                continue
            
            print("\n🤔 Processing your question...")
            result = bot.get_compliance_answer(question)
            
            print(f"\n📝 Answer:")
            print("="*50)
            print(result['answer'])
            print("="*50)
            print(f"RAG Used: {'✅ Yes' if result['rag_used'] else '❌ No'}")
            print(f"Timestamp: {result['timestamp']}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    # Check if running in Streamlit
    try:
        import streamlit as st
        create_streamlit_app()
    except ImportError:
        # Fall back to CLI if Streamlit is not available
        cli_interface()