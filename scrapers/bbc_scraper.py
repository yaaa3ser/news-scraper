import feedparser
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from base_scraper import BaseScraper


class BBCScraper(BaseScraper):
    """BBC RSS scraper implementation."""
    
    def __init__(self):
        super().__init__("BBC")
        self.rss_urls = [
            'http://feeds.bbci.co.uk/news/world/rss.xml',
            'http://feeds.bbci.co.uk/news/technology/rss.xml',
            "http://feeds.bbci.co.uk/news/health/rss.xml",
            "http://feeds.bbci.co.uk/news/education/rss.xml",
            "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
        ]

    def scrape_articles(self):
        """Scrape articles from BBC RSS feeds."""
        articles = []
        for url in self.rss_urls:
            self.logger.info(f"Fetching RSS feed from {url}")
            feed = feedparser.parse(url)
            self.logger.info(f"Found {len(feed.entries)} entries in {url}")
            for entry in feed.entries:
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                if (datetime.now(timezone.utc) - published).total_seconds() <= 24 * 3600:
                    article_url = entry.link
                    try:
                        response = requests.get(article_url)
                        response.raise_for_status()
                        soup = BeautifulSoup(response.text, 'html.parser')
                        content = soup.find('article')
                        if not content:
                            self.logger.warning(f"No content found for {article_url}")
                            continue
                        paragraphs = content.find_all('p', class_='sc-9a00e533-0')
                        content_text = '\n'.join(p.get_text() for p in paragraphs if p.get_text())
                        image = soup.find('meta', property='og:image')
                        image_url = image['content'] if image else ''
                        articles.append({
                            'title': entry.title,
                            'url': article_url,
                            'content': content_text,
                            'image_url': image_url,
                            'published': published,
                            'fetch_time': datetime.now(timezone.utc),
                            'category': feed.feed.title
                        })
                    except Exception as e:
                        self.logger.error(f"Error fetching {article_url}: {e}")
                        continue
        return articles


def main():
    scraper = BBCScraper()
    scraper.run_continuous()


if __name__ == "__main__":
    main()