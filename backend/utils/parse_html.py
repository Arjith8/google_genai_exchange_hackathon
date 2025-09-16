from bs4 import BeautifulSoup, Comment, Tag

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
        head = soup.head.extract()
        return head

    @staticmethod
    def clean_html(html_content) -> BeautifulSoup:
        """
        Cleans the provided HTML 

        Args:
            html_content (str): The HTML content to be cleaned.

        Returns:
            str: The cleaned html content without unnecessary tags and attributes.
        """

        soup = BeautifulSoup(html_content, 'lxml')
        delete_tags = ['script', 'style', 'link', 'iframe', 'noscript']
        entries_to_delete = soup(delete_tags)
        
        _ = [entry.decompose() for entry in entries_to_delete]

        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        return soup

    @staticmethod
    def diff_html(old_html: BeautifulSoup, new_html: BeautifulSoup):
        """
        To be used for generating diffs between two HTML strings, after they have been cleaned.
        """
        pass
