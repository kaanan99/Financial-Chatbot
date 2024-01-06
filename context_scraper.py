from bs4 import BeautifulSoup
import requests
from typing import List

def extract_link(header_object:BeautifulSoup) -> str:
    """Extracts the link stored in the header object

    Args:
        header_object (sBeautifulSoup): Header object containing the link

    Returns:
        str: the link
    """
    return header_object.find("a")["href"]


def generate_context_text(query: str) -> List[str]:
    """Searches query on marketwatch.com and returns the text from the 5 most relevant articles

    Args:
        query (str): String containing the query

    Returns:
        List[str]: List of texts from marketwatch.com
    """

    context_article_texts =[]
    
    # Url Generation
    base_link = "https://www.marketwatch.com"
    search_string = "/search?q="

    cleaned_query = query.replace("?", "%3F").split()
    query_for_url = "%20".join(cleaned_query)

    url = f"{base_link}{search_string}{query_for_url}&ts=0&tab=All%20News"

    # Get links for context articles from search
    search_page = requests.get(url)
    content = search_page.text
    search_page_parser = BeautifulSoup(content, "html.parser")

    # Extract Links
    search_results = search_page_parser.find_all(
        "h3", 
        class_="article__headline", 
        limit=5
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
        text = " ".join([p.get_text().strip() for p in paragraphs])

        context_article_texts.append(text)

    return context_article_texts