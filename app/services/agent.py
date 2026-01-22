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
    # locations = conf.get("locations", [])
    # products = conf.get("products", []) # generic key
    # offerings = locations if locations else products
    
    # Check if there is a 'locations' key which implies Travel, or just generic 'products'
    # We dump whatever list analysis we have.
    data_context = ""
    # if offerings:
    #      data_context = f"Here are the products/services we offer:\n{json.dumps(offerings, indent=2)}\n"

    # Check for uploaded brochure/knowledge base
    kb_path = os.path.join("data", "knowledge_base.txt")
    if os.path.exists(kb_path):
        with open(kb_path, "r", encoding="utf-8") as f:
            kb_content = f.read()
            data_context += f"\nKNOWLEDGE BASE FROM UPLOADED DOCUMENTS:\n{kb_content}\n"
    
    # Create a dynamic persona
    prompt = f"""
    You represent {company_name}, a respected organization.
    Your name is {agent_name}.
    
    YOUR ROLE:
    You are a helpful assistant for {company_name}. You specialize in our specific offerings and helping users find the best solutions based strictly on our KNOWLEDGE BASE.
    
    IMPORTANT:
    1. **STRICTLY LIMITED SCOPE**: You rely ONLY on the provided Knowledge Base (from uploaded documents). Do NOT use any external or pre-configured JSON lists.
    2. **NO WEB SEARCH FOR PRODUCTS**: Do NOT search the internet for products or services we do not list. If a user asks for a specific product/destination we don't have in the Knowledge Base, politely apologize and state that we do not offer that service.
    3. **OFFICIAL INFO ONLY**: Only generate flyers or quotes for items that explicitly exist in your Knowledge Base.
    
    YOUR KNOWLEDGE BASE:
    {data_context}
    
    INTERACTION GUIDELINES:
    1. Be polite, professional, and helpful.
    2. Collect User Information (Name, Email, Mobile) early in the conversation naturally.
    3. If the user asks for something not in our list, say: "I apologize, but we currently do not offer that service/destination." You may then suggest a close alternative from our list if applicable.
    4. If the user is interested in a listed item, you can provide details.
    5. **Brochures/Flyers**: If the user asks for a brochure/flyer for a LISTED item, use `generate_flyer_pdf`. If the item is NOT listed, refuse to generate the flyer.
    6. Only use email_flyer if the user EXPLICITLY requests to have the flyer sent to their email.
    
    TOOLS:
    To use a tool, output valid JSON:
    {{ "tool": "tool_name", "params": {{ ... }} }}
    
    - update_lead_info(name, email, mobile, topic)
    - generate_flyer_pdf(title, content, filename) -- Use strictly for listed items.
    - email_flyer(to_email, title, content, filename) -- Only use if user specifically asks to EMAIL the flyer.
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

            # Attempt to find JSON-like structure
            start = bot_content.find("{")
            end = bot_content.rfind("}") + 1
            if start != -1 and end != -1 and '"tool":' in bot_content:
                json_str = bot_content[start:end]
                
                # Cleanup: remove markdown code fences if present inside the block (unlikely but possible) or around it
                # Logic: If proper start/end found, usually fences are outside, but let's be safe.
                
                # Robust parsing strategy
                import re
                
                # 1. Try standard load
                try:
                    tool_data = json.loads(json_str, strict=False)
                except json.JSONDecodeError:
                    # 2. Try fixing newlines inside strings. 
                    # This is a naive regex approach: It assumes quotes are balanced and doesn't handle escaped quotes perfectly, 
                    # but works for most LLM text outputs.
                    # Let's try replacing unescaped newlines
                    fixed_str = json_str.replace('\n', '\\n')
                    try:
                         tool_data = json.loads(fixed_str, strict=False)
                    except:
                        # 3. Last ditch: simply ignore control characters
                        tool_data = json.loads(json_str, strict=False)

                tool_name = tool_data.get("tool")
                params = tool_data.get("params", {})
                
                if tool_name == "update_lead_info":
                    result = tools.update_lead_info(**params)
                    tool_response = f"(System: {result})"
                elif tool_name == "search_web":
                    result = tools.search_web(**params)
                    tool_response = f"(System Search Results: {result})"
                elif tool_name == "generate_flyer_pdf":
                    # Clean up content for PDF generation if needed
                    if "content" in params:
                        params["content"] = params["content"].replace("\\n", "\n")
                        
                    filepath = tools.generate_flyer_pdf(**params)
                    tool_response = json.dumps({"action": "download", "url": filepath})
                    bot_content = f"I've generated the flyer '{params.get('title', 'requested')}' for you. [Download PDF]({filepath})"
                elif tool_name == "email_flyer":
                    result = tools.create_and_email_flyer(**params)
                    if isinstance(result, dict) and "url" in result:
                        tool_response = json.dumps({"action": "download", "url": result["url"]})
                        bot_content = f"{result.get('message', 'Flyer emailed.')} [Download PDF]({result['url']})"
                    else:
                        bot_content = str(result.get("error", result)) if isinstance(result, dict) else str(result)
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
            # If we found a tool-like block but failed to parse/execute, 
            # we should probably strip it from the user view so they don't see raw JSON.
            if '"tool":' in bot_content:
                # Fallback: Strip the JSON part to hide the error trace from user
                clean_msg = bot_content[:bot_content.find("{")].strip()
                if not clean_msg:
                    clean_msg = "I attempted to perform an action but encountered a technical issue."
                bot_content = clean_msg
            pass
            
        return bot_content, tool_response

    except Exception as e:
        return f"Error contacting AI: {str(e)}", None
