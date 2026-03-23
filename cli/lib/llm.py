import os
import json
from dotenv import load_dotenv
from google import genai
from numpy import promote_types
from .search_utils import PROMPTS_DIR

load_dotenv()
MODEL = "gemini-2.5-flash"

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY environment variable not set")
client = genai.Client(api_key=api_key)


def generate_content(prompt, query):
    """
    Generate content using the Gemini LLM based on a provided prompt and query.

    The function formats the `prompt` template with the supplied `query`, sends the combined 
    prompt to the Gemini model specified by `MODEL`, and returns the generated textual response.

    Args:
        prompt (str): A prompt template string, expected to contain a `{query}` placeholder 
                      that will be filled in with the actual search/query terms.
        query (str): The search or question string to insert into the prompt.

    Returns:
        str: Generated text content returned by the Gemini model in response to the prompt.
    """
    prompt = prompt.format(query=query)
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text


def correct_spelling(query):
    """
    Use an LLM (Gemini) to correct spelling and grammar for a provided query string.

    This function reads a spelling correction prompt template from 'prompts/spelling.md',
    feeds the original query and template to the LLM, and returns the LLM's suggested correction.

    Args:
        query (str): The input query string potentially containing spelling or grammatical errors.

    Returns:
        str: The LLM's suggested spelling/grammar corrected version of the input query.
    """
    with open(PROMPTS_DIR / "spelling.md", "r") as f:
        prompt = f.read()
    return generate_content(prompt, query)


def rewrite_query(query):
    """
    Use an LLM (Gemini) to rewrite a provided query string.

    This function reads a rewrite prompt template from 'prompts/rewrite.md',
    feeds the original query and template to the LLM, and returns the LLM's suggested rewrite.
    """
    with open(PROMPTS_DIR / "rewrite.md", "r") as f:
        prompt = f.read()
    return generate_content(prompt, query)


def expand_query(query):
    """
    Use an LLM (Gemini) to expand a provided query string.

    This function reads a expand prompt template from 'prompts/expand.md',
    feeds the original query and template to the LLM, and returns the LLM's suggested expand.
    """
    with open(PROMPTS_DIR / "expand.md", "r") as f:
        prompt = f.read()
    return generate_content(prompt, query)


def llm_judge(query, formatted_results):
    """
    Use an LLM (Gemini) to judge the relevance of a list of results to a query.

    Args:
        query (str): The original search query.
        formatted_results (str): Pre-formatted string of results to evaluate.

    Returns:
        list[int]: A list of relevance scores (0-3) in the same order as the results.
    """
    with open(PROMPTS_DIR / "llm_judge.md", "r") as f:
        prompt_template = f.read()
    prompt = prompt_template.format(
        query=query, formatted_results=formatted_results)
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return json.loads(response.text)


def answer_question(query, docs):
    with open(PROMPTS_DIR / "augment_answer.md", "r") as f:
        prompt_template = f.read()
    prompt = prompt_template.format(query=query, docs=docs)
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text
