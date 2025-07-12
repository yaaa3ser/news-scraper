from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import os
import psycopg2
import logging
from urllib.parse import unquote


class DatabaseService:
    """Service class for database operations in the API."""
    
    def __init__(self):
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
    
    def get_all_articles(self):
        """Get all articles from database."""
        conn = self.connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT title_of_article, url_of_article, main_category, main_picture_of_article_url, published_utc FROM articles ORDER BY fetch_datetime_utc DESC")
            articles = [{
                'title_of_article': row[0],
                'url_of_article': row[1],
                'main_category': row[2],
                'main_picture_of_article_url': row[3],
                'published_utc': row[4].isoformat()
            } for row in cursor.fetchall()]
            return articles
        except Exception as e:
            self.logger.error(f"Error fetching articles: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch articles")
        finally:
            cursor.close()
            conn.close()
    
    def get_article_by_url(self, url: str):
        """Get specific article by URL."""
        conn = self.connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM articles WHERE url_of_article = %s", (unquote(url),))
            row = cursor.fetchone()
            if row:
                return {
                    'title_of_article': row[0],
                    'url_of_article': row[1],
                    'full_content_of_article': row[2],
                    'main_picture_of_article_url': row[3],
                    'published_utc': row[4].isoformat(),
                    'fetch_datetime_utc': row[5].isoformat(),
                    'main_category': row[6]
                }
            return {}
        except Exception as e:
            self.logger.error(f"Error fetching article: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch article")
        finally:
            cursor.close()
            conn.close()


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize database service
db_service = DatabaseService()

@app.get("/articles")
async def get_articles():
    return db_service.get_all_articles()

@app.get("/article")
async def get_article(url: str):
    return db_service.get_article_by_url(url)