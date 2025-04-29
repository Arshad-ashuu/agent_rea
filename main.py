from transformers import pipeline
import streamlit as st
import requests
from newspaper import Article

# ------ Streamlit UI ------
st.set_page_config(page_title="Agent Rea", page_icon="🔍", layout="wide")
st.title("🔎 Agent Rea")
st.markdown("#### Empower your research with SERP API & Hugging Face")

# Sidebar for Configuration
st.sidebar.header("Configuration")
SERPAPI_KEY = st.sidebar.text_input("Enter SERP API Key (Optional):", type="password")

# Input Section
st.markdown("### 🔧 Research Options")
question = st.text_input("Ask a research question:", value="How does Bitcoin work?")
num_results = st.slider("Number of results to retrieve:", min_value=1, max_value=10, value=3)

# Function Definitions
def web_search(query, api_key=None, num_results=3):
    if not api_key:
        st.warning("🔴 SERP API key not provided. Skipping web search.")
        return []
    try:
        params = {"q": query, "api_key": api_key, "num": num_results}
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        results = response.json()
        # Show success message after successful web search
        st.success("✅ Web search successful! Results retrieved.")
        return [result["link"] for result in results.get("organic_results", [])]
    except Exception as e:
        st.error(f"🔴 Search failed: {str(e)}")
        return []

def extract_and_summarize(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        summary = summarizer(article.text, max_length=130, min_length=30, do_sample=False)
        return summary[0]["summary_text"]
    except Exception as e:
        return f"Error summarizing article: {e}"

def summarize_question_directly(question):
    try:
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        summary = summarizer(question, max_length=50, min_length=10, do_sample=False)
        return summary[0]["summary_text"]
    except Exception as e:
        return f"Error summarizing input: {e}"

def research_agent(question, serpapi_key=None):
    urls = web_search(question, serpapi_key) if serpapi_key else []
    results = []
    if urls:
        for url in urls:
            summary = extract_and_summarize(url)
            results.append({"source": url, "summary": summary})
    else:
        # If no URLs are found, summarize the question directly
        summary = summarize_question_directly(question)
        results = [{"source": "Direct Question Summary", "summary": summary}]
    return results

# Execution
if st.button("Run Agent Rea"):
    st.write("🔎 Running Agent Rea...")
    results = research_agent(question, SERPAPI_KEY)
    
    # Display Results
    st.markdown("### 📝 Research Results")
    if results:
        st.write(f"**Question Asked:** {question}")
        st.markdown("#### 🔗 Summarized Results:")
        
        combined_summary = []
        for idx, result in enumerate(results, start=1):
            st.markdown(f"**{idx}. Source:** {result['source']}")
            if result['summary']:
                st.markdown("**Summary:**")
                st.write("- Key Points:")
                for point in result['summary'].split('. '):  # Splits into points
                    if point.strip():
                        st.write(f"  - {point.strip()}")
                combined_summary.append(result['summary'])
            else:
                st.write("- **Summary:** Not available")
        
        # Combined Final Summary
        st.markdown("### 📘 Combined Final Summary:")
        if combined_summary:
            consolidated_text = " ".join(combined_summary)
            key_points = consolidated_text.split('. ')
            for idx, point in enumerate(key_points, start=1):
                if point.strip():
                    st.write(f"{idx}. {point.strip()}")
        else:
            st.write("No meaningful content available for summarization.")
    else:
        st.error("No results to display!")
else:
    st.info("👆 Enter a question and click 'Run Agent Rea' to begin.")

# Footer
st.markdown("---")
st.markdown("🔗 **[Report Issues](https://github.com/Arshad-ashuu/agent_rea)** | 💡 **Suggestions Welcome** | 📧 **Contact Us**")
