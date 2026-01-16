import json
import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from app.core import config
from app.services import tools

# Initialize Mistral Client
api_key = os.environ.get("MISTRAL_API_KEY")
client = MistralClient(api_key=api_key) if api_key else None

def generate_dynamic_prompt(conf):
    """
    Generates a domain-specific system prompt based on the configuration.
    It attempts to understand the industry/context from the company name and data available.
    """
    company_name = conf.get("company_name", "the company")
    agent_name = conf.get("agent_name", "Assistant")
    
    # Try to infer industry or use available keys
    locations = conf.get("locations", [])
    products = conf.get("products", []) # generic key
    offerings = locations if locations else products
    
    # Check if there is a 'locations' key which implies Travel, or just generic 'products'
    # We dump whatever list analysis we have.
    data_context = ""
    if offerings:
         data_context = f"Here are the products/services we offer:\n{json.dumps(offerings, indent=2)}"
    
    # Create a dynamic persona
    prompt = f"""
    You represent {company_name}, a respected organization.
    Your name is {agent_name}.
    
    YOUR ROLE:
    You are the primary interface for our customers. You handle marketing (explaining our offerings), sales (closing deals/interests), and support (solving problems).
    
    YOUR KNOWLEDGE BASE:
    {data_context}
    
    Refer to these offerings to answer questions. If the user asks for something we don't list, politely explain we don't have it but offer alternatives if possible.
    
    INTERACTION GUIDELINES:
    1. Be polite, professional, and helpful.
    2. Collect User Information (Name, Email, Mobile) early in the conversation naturally.
    3. If the user seems interested in a specific item, offer to send them a detailed Flyer (PDF) or Email about it.
    4. If the user reports an issue, apologize and try to solve it. If you can't, offer to "Escalate to the CEO" (which sends an email to the CEO).
    
    TOOLS:
    To use a tool, output valid JSON:
    {{ "tool": "tool_name", "params": {{ ... }} }}
    
    - update_lead_info(name, email, mobile, topic)
    - generate_flyer_pdf(title, content, filename)
    - email_flyer(to_email, title, content, filename) -- Generates PDF and emails it. Use this if user asks to "email me the flyer".
    - send_email(to_email, subject, content) -- Use "CEO" as to_email for escalations.
    - send_sms(mobile_number, message)
    
    Only output JSON if you are performing an action.
    """
    return prompt

def get_system_prompt():
    """Retrieves the current prompt logic."""
    conf = config.load_config()
    # If a specific prompt is set in config (manual override), use it, otherwise generate one
    # Note: User requested "prompt should be automatically generated acc to the domain". 
    # So we prefer the generator unless strictly overriden by a user manually typing a prompt?
    # For now, let's assume if it matches the default placeholder or is empty, we clean it.
    # Actually, let's always regenerate based on current config values to ensure it matches the selected domain.
    
    return generate_dynamic_prompt(conf)

def process_user_message(user_message: str, history: list):
    """
    Process a user message using Mistral and handle tool calls.
    """
    if not client:
        return "Error: Mistral API Key not configured.", None

    system_prompt = get_system_prompt()
    
    messages = [ChatMessage(role="system", content=system_prompt)]
    for msg in history:
        messages.append(ChatMessage(role=msg["role"], content=msg["content"]))
    
    messages.append(ChatMessage(role="user", content=user_message))
    
    try:
        response = client.chat(
            model="mistral-large-latest", 
            messages=messages,
        )
        bot_content = response.choices[0].message.content
        
        tool_response = None
        try:
            if "{" in bot_content and "}" in bot_content and '"tool":' in bot_content:
                start = bot_content.find("{")
                end = bot_content.rfind("}") + 1
                json_str = bot_content[start:end]
                # Fix for potential unescaped newlines in JSON strings from LLM
                tool_data = json.loads(json_str, strict=False)
                
                tool_name = tool_data.get("tool")
                params = tool_data.get("params", {})
                
                if tool_name == "update_lead_info":
                    result = tools.update_lead_info(**params)
                    tool_response = f"(System: {result})"
                elif tool_name == "generate_flyer_pdf":
                    filepath = tools.generate_flyer_pdf(**params)
                    tool_response = f"I've created that flyer for you: [{params.get('filename')}]({filepath})"
                    bot_content = tool_response
                elif tool_name == "email_flyer":
                    result = tools.create_and_email_flyer(**params)
                    tool_response = result
                    bot_content = tool_response
                elif tool_name == "send_email":
                    result = tools.send_email(**params)
                    tool_response = f"{result}"
                    bot_content = tool_response
                elif tool_name == "send_sms":
                    result = tools.send_sms(**params)
                    tool_response = f"{result}"
                    bot_content = tool_response
                
        except Exception as e:
            print(f"Tool parse warning: {e}")
            pass
            
        return bot_content, tool_response

    except Exception as e:
        return f"Error contacting AI: {str(e)}", None
