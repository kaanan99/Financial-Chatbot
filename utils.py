import requests
import re
import string

from bs4 import BeautifulSoup
from typing import List


def clean_query(query:str) -> str:
    """Cleans the query and converts it so it can be used in a URL

    Args:
        query (str): string containing the query

    Returns:
        str: Cleaned query string
    """
    for punct in string.punctuation:
        if punct != "?":
            query = query.replace(punct, "")
    
    query_for_url = "%20".join(
        query.split()
        )
    return query_for_url


def extract_link(header_object:BeautifulSoup) -> str:
    """Extracts the link stored in the header object

    Args:
        header_object (sBeautifulSoup): Header object containing the link

    Returns:
        str: the link
    """
    return header_object.find("a")["href"]


def generate_context_text(query: str, query_limit:int=5) -> List[str]:
    """Searches query on marketwatch.com and returns the text from the 5 most relevant articles

    Args:
        query (str): String containing the query
        query_limit (int, optional):Number of documents to be used for context. Defaults to 5.

    Returns:
        List[str]: List of texts from marketwatch.com
    """

    context_article_texts =[]
    
    # Url Generation
    base_link = "https://www.marketwatch.com"
    search_string = "/search?q="

    # Clean Query
    query_for_url = clean_query(query)

    # URL for Search
    url = f"{base_link}{search_string}{query_for_url}&ts=0&tab=All%20News"

    # Get links for context articles from search
    search_page = requests.get(url)
    content = search_page.text
    search_page_parser = BeautifulSoup(content, "html.parser")

    # Extract Links
    search_results = search_page_parser.find_all(
        "h3", 
        class_="article__headline", 
        limit=query_limit
    )
    links = [
        extract_link(header_object) for header_object in search_results
    ]

    # Get text for context articles
    
    for link in links:
        context_page = requests.get(link)
        context_page_content = context_page.text
        article_parser = BeautifulSoup(context_page_content, "html.parser")

        # Extract Text
        paragraphs = article_parser.find_all("p")
        text = " ".join(
            [
                re.sub("\s\s+", " ", p.get_text().strip())
                for p in paragraphs
            ]
        )

        context_article_texts.append(text)
    
    context_text = " ".join(context_article_texts)

    return context_text


def generate_model_input(
        tokenizer, 
        query: str, 
        context: str,  
        max_length=2048
        )-> List:
    """Generates input for the model. Also filters out tokens in context so the entire model input is under the max token limit

    Args:
        tokenizer (transformers.models.llama.tokenization_llama_fast.LlamaTokenizerFast): Tokenizer used by the model
        query (str): String containing the query
        context (str): string containing the context for the model
        max_length (int, optional): Maximum number of token passed to the model. Defaults to 2048.

    Returns:
        List: Containing dictionaries representing system information, context, and the query respsectively
    """
    # Create system, context, and query information in chat format
    chat_context = {
        "role": "system",
        "content":context,
    }
    system_chat = {
            "role": "system",
            "content": "You are a financial chatbot who is answer the users question as accurately. Try be conversational, concise, and work the question into the response. Use correct grammer to in your response",
        },
    query_chat = {
        "role": "user",
        "content": query
    }

    # Calculate how many tokens were used by the system message and query
    used_tokens = len(
        tokenizer.apply_chat_template(
            [system_chat, query_chat]
            )
        )
    
    remaining_tokens = max_length-used_tokens

    # Keep only max_length number of tokens
    context_tokens_reduced = tokenizer.apply_chat_template([chat_context])[:remaining_tokens]

    # Decode tokens to put into model input
    filtered_context = (
        tokenizer
        .decode(context_tokens_reduced)
        .split(">")[-1]
        .strip()
    )
    chat_context["content"] = filtered_context

    model_input = [system_chat, chat_context, query_chat]

    return model_input


def get_chatbot_response(output:str)-> str:
    """Extracts model response from the output generated

    Args:
        output (str): The model output

    Returns:
        str: Response from the model
    """
    response = (
        output[0]["generated_text"]
        .split(">")[-1]
        .strip()
    )
    return response