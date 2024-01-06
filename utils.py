import requests
import torch
import transformers

from bs4 import BeautifulSoup
from typing import List
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline


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
        text = " ".join([p.get_text().strip() for p in paragraphs])

        context_article_texts.append(text)

    context = " ".join(context_article_texts).strip()

    return context

def create_chatbot_pipeline(model_name:str) -> transformers.pipelines.question_answering.QuestionAnsweringPipeline:
    """Creates pipeline object to generate chatbot responses

    Args:
        model_name (str): Name of the model to use

    Returns:
        transformers.pipelines.question_answering.QuestionAnsweringPipeline: The pipeline object
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForQuestionAnswering.from_pretrained(model_name)
    model = model.to(torch.float32)

    model_pipeline = pipeline('question-answering', model=model, tokenizer=tokenizer)
    return model_pipeline

def generate_chatbot_output(
        query:str,
        model_pipeline:transformers.pipelines.question_answering.QuestionAnsweringPipeline, 
        context_document_num:int=5
        ) ->  str:
    """Generates a response for the chatbot using web-scraped documents for context

    Args:
        query (str): The query from the user
        model_pipeline (transformers.pipelines.question_answering.QuestionAnsweringPipeline): Pipeline object used to generate response
        context_document_num (int, optional): Number of documents to use for context. Defaults to 5.

    Returns:
        str: Response for the chatbot
    """

    context = generate_context_text(query, context_document_num)
    model_input = {
        'question': query,
        'context': f"You are a financial chatbot who is answer the users question as accurately. Try to use details, be conversational, and work the question into the response. Use the following context to help answer questions: {context}"
     }
    result = model_pipeline(model_input)
    return result["answer"]