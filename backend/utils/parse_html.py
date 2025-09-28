from bs4 import BeautifulSoup, Comment, Tag
from difflib import unified_diff

from requests import request
import requests

class HTMLParser:
    @staticmethod
    def extract_header(soup: BeautifulSoup) -> Tag:
        """
        Extracts the <head> section from the provided HTML content. To be used for metadata extraction.
        Args:
            html_content (str): The HTML content from which to extract the head section.
        Returns:
            str: The extracted head section as a string.
        """
        head = soup.head
        if head:
            return head.extract()
        return soup.new_tag("head")

    @staticmethod
    def clean_html(url) -> BeautifulSoup:
        """
        Cleans the provided HTML 

        Args:
            html_content (str): The HTML content to be cleaned.

        Returns:
            str: The cleaned html content without unnecessary tags and attributes.
        """

        html_content = requests.post("http://playwright:8000/", json={"link": url}).json().get("content", "")
        soup = BeautifulSoup(html_content, 'lxml')

        return soup

    @staticmethod
    def diff_html(old_html: str, new_html: BeautifulSoup):
        """
        To be used for generating diffs between two HTML strings, after they have been cleaned.
        """
        new_str = new_html.prettify()

        diff = unified_diff(
            old_html.splitlines(keepends=True),
            new_str.splitlines(keepends=True),
            fromfile="old_html",
            tofile="new_html",
            lineterm=""
        )
        return "".join(diff)
