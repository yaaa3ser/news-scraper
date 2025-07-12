from datetime import datetime, timezone
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from base_scraper import BaseScraper
from selenium.common.exceptions import TimeoutException


class NewsmaxScraper(BaseScraper):
    """Newsmax web scraper implementation using Selenium."""
    
    def __init__(self):
        super().__init__("Newsmax")
        self.base_url = 'https://www.newsmax.com'

    def create_chrome_driver(self):
        """Create and configure Chrome WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.126 Safari/537.36')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            service = Service('/usr/local/bin/chromedriver')
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.set_page_load_timeout(5)
            driver.implicitly_wait(3)
            return driver
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome driver: {e}")
            raise

    def parse_date(self, date_string):
        """Parse Newsmax date format."""
        try:
            return datetime.strptime(date_string, '%A, %d %B %Y %I:%M %p').replace(tzinfo=timezone.utc)
        except ValueError as e:
            self.logger.warning(f"Failed to parse date '{date_string}': {e}")
            return datetime.now(timezone.utc)

    def scrape_articles(self):
        """Scrape articles from Newsmax homepage."""
        driver = self.create_chrome_driver()
        articles = []
        
        try:
            self.logger.info("Starting Newsmax scraping...")
            
            driver.get(self.base_url)
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            self.logger.info(f"Page title: {soup.title.string if soup.title else 'No title'}")
            
            # Find article links (updated based on Newsmax structure)
            article_links = soup.select('.nmNewsfrontStory .nmNewsfrontHead a')
            self.logger.info(f"Found {len(article_links)} article links")
            
            # Remove duplicates
            seen_urls = set()
            unique_links = []
            for link in article_links:
                url = link['href']
                if url not in seen_urls:
                    seen_urls.add(url)
                    unique_links.append(link)
            
            article_links = unique_links
            self.logger.info(f"Processing {len(article_links)} unique article links")
            
            for i, article in enumerate(article_links):
                article_url = article['href']
                if not article_url.startswith('http'):
                    article_url = self.base_url + article_url
                
                try:
                    self.logger.info(f"Scraping article {i+1}: {article_url}")
                    driver.get(article_url)
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    self.logger.info(f"Loaded article page: {article_url}")
                    
                    article_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    
                    # Extract title
                    title_elem = article_soup.find('h1', class_='article')
                    title = title_elem.get_text().strip() if title_elem else ''
                    
                    # Extract content
                    content_elem = article_soup.find('div', {'id': 'mainArticleDiv'})
                    content_text = content_elem.get_text(separator=' ').strip() if content_elem else ''
                    
                    # Extract image
                    image_elem = article_soup.find('meta', property='og:image')
                    image_url = image_elem.get('content', '') if image_elem else ''
                    self.logger.info(f"Image URL: {image_url if image_url else 'No image found'}")
                    
                    # Extract published date
                    date_elem = article_soup.find('div', itemprop='datePublished')
                    published = self.parse_date(date_elem.get_text().strip()) if date_elem else datetime.now(timezone.utc)
                    
                    # Extract category
                    category_elem = article_soup.find('a', class_='nmMainNavLinkSel')
                    category = 'NewsMax  ' + category_elem.get_text().strip() if category_elem else 'NewsMax General'
                    
                    if title and content_text:
                        articles.append({
                            'title': title,
                            'url': article_url,
                            'content': content_text,
                            'image_url': image_url,
                            'published': published,
                            'fetch_time': datetime.now(timezone.utc),
                            'category': category
                        })
                        self.logger.info(f"Successfully scraped: {title[:50]}...")
                    else:
                        self.logger.warning(f"Skipping article with missing content: {article_url}")
                
                except TimeoutException:
                    self.logger.warning(f"Timeout loading article {i+1}: {article_url} - Skipping")
                    continue  # Skip to next article

                except Exception as e:
                    self.logger.error(f"Error scraping {article_url}: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error in main scraping loop: {e}")
        finally:
            driver.quit()
        
        self.logger.info(f"Scraping completed. Found {len(articles)} articles")
        return articles


def main():
    scraper = NewsmaxScraper()
    scraper.run_continuous()


if __name__ == "__main__":
    main()