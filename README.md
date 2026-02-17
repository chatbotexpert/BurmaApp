# Burma News Aggregator

A Django-based news aggregator that collects, translates, and displays news from various sources (RSS, Facebook, Twitter/X, Telegram) in a modern, Pinterest-style masonry layout.

## 🚀 Features

- **Multi-Source Aggregation**: Fetches content from RSS feeds, Facebook pages, Twitter/X profiles, and Telegram channels.
- **Automated Scraping**: Background scheduler runs periodically to fetch new content.
- **Auto-Translation**: Automatically translates Burmese content using `googletrans`.
- **Modern UI**: Responsive masonry grid layout with infinite scroll-like pagination.
- **Source Filtering**: Filter posts by platform (Facebook, X, Telegram, RSS) or specific source.
- **Admin Control**: Manage sources and scraping intervals dynamically via Django Admin.

## 🛠️ Prerequisites

- **Python 3.10+**
- **pip** (Python package manager)
- **Git**

## 📥 Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/chatbotexpert/BurmaApp.git
    cd BurmaApp
    ```

2.  **Create a Virtual Environment** (Recommended)
    ```bash
    python -m venv venv
    
    # Windows
    venv\Scripts\activate
    
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Playwright Browsers**
    Required for scraping Facebook and Twitter/X.
    ```bash
    playwright install
    ```

5.  **Apply Database Migrations**
    ```bash
    python manage.py migrate
    ```

6.  **Create Superuser** (For Admin Panel)
    ```bash
    python manage.py createsuperuser
    ```

7.  **Setup Telegram Scraper** (One-time)
    Required for scraping Telegram channels.
    ```bash
    python telegram_setup.py
    ```
    Follow the prompts to log in with your phone number.

## 🏃‍♂️ How to Run

### 1. One-Click Start (Windows)
Double-click `run_services.bat` to start both the Web Server and the Scraper in separate windows.

### 2. Manual Start
#### Start the Web Server
This runs the main website where users can view the news.
```bash
python manage.py runserver
```
access the site at `http://127.0.0.1:8000/`.

### 2. Start the Scraper (Background Process)
This command runs in an infinite loop, fetching news every X minutes (configurable in Admin). **Run this in a separate terminal window.**
```bash
python manage.py run_scheduler
```
*   **Headless Mode**: By default, scraping runs in "headless" mode (no browser window visible).
*   **Configuration**: The scraping interval defaults to 60 minutes.

## 🧠 System Architecture & Logic

### 1. Data Models (`aggregator/models.py`)
-   **Source**: Represents a news feed/page. Stores the URL, name, and `source_type` (RSS, FACEBOOK, TWITTER, TELEGRAM).
-   **Post**: Represents an individual news item. Stores title, content, images, and the translated text.
-   **ScraperSettings**: A singleton model storing the global `scraping_interval`.

### 2. Scraping Engine (`aggregator/scrapers.py`)
-   **Router**: The `run_scraping()` function iterates through all active `Source` objects.
-   **Strategies**: Depending on the `source_type`, it dispatches the task to specific helper functions:
    -   **RSS**: Uses `feedparser` to standard XML feeds.
    -   **Facebook/Twitter**: Uses `playwright` to simulate a real browser, scroll pages, and extract content dynamically.
    -   **Telegram**: Uses `requests` and `BeautifulSoup` to parse public web views of channels.
-   **Translation**: Content is passed through `googletrans` to ensure Burmese text is available.
-   **Deduplication**: Checks URLs against the database to avoid saving duplicate posts.

### 3. Frontend (`aggregator/templates/`)
-   **Masonry Layout**: Uses CSS Columns (`column-count`) to create a Pinterest-like grid that handles cards of varying heights purely with CSS.
-   **Filtering**: 
    -   **URL Parameters**: `?source=ID` and `?type=TYPE` parameters control the filtering in `views.py`.
    -   **UI**: Buttons and Dropdowns in the template link to these filtered URLs.

## ⚙️ Configuration (Admin Panel)

Access `http://127.0.0.1:8000/admin/` to:
1.  **Add/Remove Sources**: Add new Facebook pages or RSS feeds.
2.  **Adjust Interval**: Go to "Scraper Settings" to change how often the scraper runs (e.g., set to 30 minutes).

## 📂 Key Files

-   `manage.py`: Django's command-line utility.
-   `aggregator/management/commands/run_scheduler.py`: The entry point for the background scraper.
-   `aggregator/scrapers.py`: Core logic for fetching and parsing data.
-   `aggregator/views.py`: Controls what data is sent to the web page.
-   `aggregator/static/aggregator/styles.css`: All visual styling for the feed.
