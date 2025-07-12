import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from base_scraper import BaseScraper


class CNNScraper(BaseScraper):
    """CNN web scraper implementation."""
    
    def __init__(self):
        super().__init__("CNN")
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.99 Safari/537.36'}
        self.base_url = 'https://www.cnn.com'

    def parse_date(self, date_string):
        """Parse CNN date format."""
        try:
            return datetime.strptime(date_string, '%b %d, %Y, %I:%M %p').replace(tzinfo=timezone.utc)
        except ValueError as e:
            self.logger.warning(f"Failed to parse date '{date_string}': {e}")
            return datetime.now(timezone.utc)

    def scrape_articles(self):
        """Scrape articles from CNN homepage."""
        url = self.base_url
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            self.logger.info(f"Scraping CNN homepage: {url}")
            for article in soup.select('a[data-link-type="article"]'):
                href = article['href']
                if href.startswith('/') and '/20' in href:
                    article_url = 'https://www.cnn.com' + href
                    self.logger.info(f"Found article link: {article_url}")
                try:
                    article_response = requests.get(article_url, headers=self.headers)
                    article_response.raise_for_status()
                    
                    article_soup = BeautifulSoup(article_response.text, 'html.parser')
                    
                    title = article_soup.find('h1').get_text() if article_soup.find('h1') else ''
                    
                    content = article_soup.find('div', itemprop='articleBody')
                    content_text = content.get_text().strip() if content else ''
                    
                    image = article_soup.find('meta', property='og:image')
                    image_url = image['content'] if image else ''
                    
                    date_elem = article_soup.find('div', class_='timestamp__published')
                    published_text = date_elem.get_text().strip().replace('PUBLISHED ', '').replace(' ET', '') if date_elem else ''
                    published = self.parse_date(published_text) if published_text else datetime.now(timezone.utc)
                    
                    category_elem = article_soup.find('a', class_='header__nav-item-link')
                    category = 'CNN ' + category_elem.get_text().strip() if category_elem else 'CNN General'
                    
                    articles.append({
                        'title': title,
                        'url': article_url,
                        'content': content_text,
                        'image_url': image_url,
                        'published': published,
                        'fetch_time': datetime.now(timezone.utc),
                        'category': category
                    })
                except Exception as e:
                    self.logger.error(f"Error scraping {article_url}: {e}")
                    continue
            self.logger.info(f"Found {len(articles)} articles on CNN homepage")
            return articles
        except Exception as e:
            self.logger.error(f"Error fetching CNN homepage: {e}")
            return []


def main():
    scraper = CNNScraper()
    scraper.run_continuous()


if __name__ == "__main__":
    main()