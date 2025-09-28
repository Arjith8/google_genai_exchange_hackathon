from bs4 import BeautifulSoup, Comment

class HTMLParser:
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
