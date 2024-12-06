import streamlit as st
from groq import Groq
import requests
from bs4 import BeautifulSoup
import spacy
import markdown
import os

groq_client = Groq(
    api_key="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",
)

nlp = spacy.load("en_core_web_md")  
llama_70B = "llama-3.1-70b-versatile"

st.set_page_config(page_title="Research Chatbot", layout="wide")

st.title("Conversational Research Chatbot")
st.write("Chat with an AI")

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = [
        {"role": "system", "content": 
        "You are an AI chatbot specializing in various research fields and marketing analysis. Kindly provide a comprehensive and accurate response to the query."}
    ]

def research_company(company_name):
    try:
        url = f"https://en.wikipedia.org/wiki/{company_name.replace(' ', '_')}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraph = soup.find('p')
        return paragraph.text.strip() if paragraph else "Could not find relevant information."
    except Exception as e:
        return f"Error occurred: {str(e)}"

def generate_use_cases(company_name, industry_name):

    return f"""
    As an AI agent, you are equipped to provide in-depth insights and solutions for various industry-specific challenges. 
    Your expertise includes predictive analytics for demand forecasting in the {industry_name} sector,
     enabling businesses to anticipate trends and optimize inventory and resource allocation. 
    You can assist with AI-driven automation strategies to enhance {industry_name} workflows, improving efficiency and reducing operational costs. 
     ensuring seamless and personalized user interactions. Your capabilities extend to leveraging Large Language Models (LLMs) for advanced market research, providing actionable insights to support data-driven decision-making. 
     With your ability to analyze complex data, identify opportunities, and recommend innovative strategies, you are a valuable resource for organizations seeking to stay competitive and drive growth in their industries.
"""

def collect_resources_and_propose_solutions(use_cases):
    try:

        resources = {
            "Kaggle": f"https://www.kaggle.com/search?q={use_cases.replace(' ', '+')}",
            "HuggingFace": f"https://huggingface.co/models?search={use_cases.replace(' ', '+')}",
            "GitHub": f"https://github.com/search?q={use_cases.replace(' ', '+')}",
        }

        file_path = "resources.md"
        with open(file_path, "w") as file:
            for platform, link in resources.items():
                file.write(f"- [{platform}]({link})\n")

        genai_solutions = """
    As an AI agent, you are designed to provide advanced, context-aware solutions for organizational needs. 
    Your expertise includes AI-driven web search, enabling efficient retrieval of internal documents by understanding context and relevance, reducing time spent on manual searches. 
    You also excel in **Automated Report Generation**, creating comprehensive, data-rich reports with minimal manual effort, ensuring accuracy and time efficiency.
    You specialize in developing **AI-Powered Chat Systems** to enhance customer engagement through dynamic, context-sensitive interactions that provide real-time support and personalized solutions. 
    You can integrate with existing systems to analyze workflows, identify inefficiencies, and recommend data-driven improvements, ensuring businesses achieve optimal productivity and enhanced customer satisfaction.
        """
        return genai_solutions, file_path
    except Exception as e:
        return f"Error occurred while collecting resources: {str(e)}", None

def determine_agent(user_input):
    if "research" in user_input.lower():
        return "agent_1"
    elif "generate use cases" in user_input.lower():
        return "agent_2"
    elif "collect resources" in user_input.lower():
        return "agent_3"
    return None

user_input = st.text_input("You:", placeholder="Type your message here...")

if user_input:
    selected_agent = determine_agent(user_input)

    if selected_agent == "agent_1":
        company_name = user_input.split("research")[-1].strip()
        if company_name:
            research_result = research_company(company_name)
            st.session_state.conversation_history.append(
                {"role": "assistant", "content": f"Agent 1 used: {research_result}"}
            )
        else:
            st.session_state.conversation_history.append(
                {"role": "assistant", "content": "Please provide a company name to research."}
            )

    elif selected_agent == "agent_2":
        if "generate use cases for" in user_input.lower():
            input_parts = user_input.lower().split("generate use cases for")
            if len(input_parts) > 1:
                details = input_parts[1].strip()
                if "in" in details:
                    company_name, industry_name = [part.strip() for part in details.split("in", 1)]
                    use_case_result = generate_use_cases(company_name, industry_name)
                    st.session_state.conversation_history.append(
                        {"role": "assistant", "content": f"Agent 2 used: {use_case_result}"}
                    )
                else:
                    st.session_state.conversation_history.append(
                        {"role": "assistant", "content": "Please specify both the company and industry, e.g., 'Generate use cases for ExampleCorp in retail.'" }
                    )
            else:
                st.session_state.conversation_history.append(
                    {"role": "assistant", "content": "Please provide details for use case generation, e.g., 'Generate use cases for ExampleCorp in retail.'"}
                )
        else:
            st.session_state.conversation_history.append(
                {"role": "assistant", "content": "Invalid input. Use the format: 'Generate use cases for [Company] in [Industry].'"}
            )

    elif selected_agent == "agent_3":
        use_cases = user_input.split("collect resources for")[-1].strip()
        if use_cases:
            genai_solutions, file_path = collect_resources_and_propose_solutions(use_cases)
            if file_path:
                st.session_state.conversation_history.append(
                    {"role": "assistant", "content": f"Agent 3 used: Resources saved in {file_path}. {genai_solutions}"}
                )
            else:
                st.session_state.conversation_history.append(
                    {"role": "assistant", "content": "Error collecting resources."}
                )
        else:
            st.session_state.conversation_history.append(
                {"role": "assistant", "content": "Please provide use cases for resource collection."}
            )

    else:
        if st.button("Send"):
            st.session_state.conversation_history.append({"role": "user", "content": user_input})

            chat_completion = groq_client.chat.completions.create(
                messages=st.session_state.conversation_history,
                model=llama_70B,
            )

            assistant_response = chat_completion.choices[0].message.content
            st.session_state.conversation_history.append(
                {"role": "assistant", "content": assistant_response}
            )

for message in st.session_state.conversation_history:
    if message["role"] == "user":
        st.markdown(f"**You:** {message['content']}")
    elif message["role"] == "assistant":
        st.markdown(f"**Assistant:** {message['content']}")
