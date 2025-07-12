import os
import logging
import psycopg2
import time
from abc import ABC, abstractmethod


class BaseScraper(ABC):
    """Base class for all news scrapers to eliminate code duplication."""
    
    def __init__(self, scraper_name):
        self.scraper_name = scraper_name
        self.db_config = {
            'dbname': 'news_db',
            'user': 'postgres',
            'password': 'password',
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': '5432'
        }
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def connect_db(self):
        """Connect to the database."""
        try:
            return psycopg2.connect(**self.db_config)
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            raise
    
    def save_articles(self, articles):
        """Save articles to database with deduplication."""
        if not articles:
            self.logger.info("No articles to save")
            return
            
        conn = self.connect_db()
        cursor = conn.cursor()
        saved_count = 0
        
        try:
            for article in articles:
                cursor.execute("SELECT 1 FROM articles WHERE url_of_article = %s OR title_of_article = %s",
                            (article['url'], article['title']))
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO articles (title_of_article, url_of_article, full_content_of_article, main_picture_of_article_url, published_utc, fetch_datetime_utc, main_category)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        article['title'], article['url'], article['content'], article['image_url'],
                        article['published'], article['fetch_time'], article['category']
                    ))
                    saved_count += 1
                    self.logger.info(f"Saved article: {article['title'][:50]}...")
                else:
                    self.logger.info(f"Article already exists: {article['title'][:50]}...")
            
            conn.commit()
            self.logger.info(f"Successfully saved {saved_count} new articles")
            
        except Exception as e:
            self.logger.error(f"Error saving articles: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    
    @abstractmethod
    def scrape_articles(self):
        """Abstract method to be implemented by each scraper."""
        pass
    
    def run_continuous(self, interval=60):
        """Run scraper continuously with specified interval."""
        while True:
            try:
                articles = self.scrape_articles()
                self.save_articles(articles)
            except Exception as e:
                self.logger.error(f"Error in {self.scraper_name} main loop: {e}")
            time.sleep(interval)
