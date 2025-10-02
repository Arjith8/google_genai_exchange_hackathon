from difflib import unified_diff

import requests
from bs4 import BeautifulSoup, Tag


class HTMLParser:
    @staticmethod
    def extract_header(soup: BeautifulSoup) -> Tag:
        """
        Extract the <head> section from the provided HTML content.

        Use it for for metadata extraction.

        Args:
            soup (str): BeautifulSoup instance of the html that was parsed

        Returns:
            Tag: The extracted head section as a string.

        """
        head = soup.head
        if head:
            return head.extract()
        return soup.new_tag("head")

    @staticmethod
    def clean_html(url: str) -> BeautifulSoup:
        """
        Clean the provided HTML.

        Args:
            url (str): Url for the website that needs to be cleaned.

        Returns:
            str: The cleaned html content without unnecessary tags and attributes.

        """
        html_content = (
            requests.post("http://playwright:8000/", json={"link": url}, timeout=10000).json().get("content", "")
        )
        return BeautifulSoup(html_content, "lxml")

    @staticmethod
    def diff_html(old_html: str, new_html: BeautifulSoup) -> str:
        """
        To be used for generating diffs between two HTML strings, after they have been cleaned.
        """
        new_str = new_html.prettify()

        diff = unified_diff(
            old_html.splitlines(keepends=True),
            new_str.splitlines(keepends=True),
            fromfile="old_html",
            tofile="new_html",
            lineterm="",
        )
        return "".join(diff)
