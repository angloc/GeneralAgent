# Market Information Collection
# Prerequisites: 
# 1. Install BeautifulSoup library: pip install beautifulsoup4
# 2. Install playwright library: pip install playwright
from GeneralAgent import Agent
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import quote
import time

def get_baidu_search_url(keyword):
    """Generate Baidu search URL, only process keyword and timestamp"""
    current_timestamp = int(time.time())
    past_timestamp = current_timestamp - (24 * 3600)  # 24 hours ago
    base_url = "https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd={}&fenlei=256&rqlang=cn&rsv_dl=tb&rsv_enter=1&rsv_btype=i&tfflag=1&gpc=stf%3D{}%2C{}|stftype%3D1"
    return base_url.format(quote(keyword), past_timestamp, current_timestamp)

def extract_news_articles(url):
    """Extract news articles and URLs from webpage"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(url)
            page.wait_for_load_state('networkidle')
            
            content = page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            articles = []
            if 'baidu.com' in url:
                # Process Baidu search results
                search_results = soup.find_all('div', class_=['result-op', 'result'])
                for result in search_results:
                    title_elem = result.find('h3')
                    if title_elem:
                        link = title_elem.find('a')
                        if link:
                            articles.append({
                                'title': title_elem.get_text().strip(),
                                'url': link.get('href', ''),
                                'source': 'Baidu Search'
                            })
            else:
                # Dongchedi processing (keep original logic)
                links = soup.find_all('a', href=True)
                base_url = "https://www.dongchedi.com"
                
                for link in links:
                    href = link.get('href', '')
                    title = link.get_text().strip()
                    if title and href:  # Keep all possible articles, let LLM judge
                        full_url = href if href.startswith('http') else base_url + href
                        articles.append({
                            'title': title,
                            'url': full_url,
                            'source': url
                        })
            
            return articles
            
        except Exception as e:
            return f"Error extracting articles: {str(e)}"
        finally:
            browser.close()

def process_single_url(url: str, keyword: str, search_description: str, agent: Agent):
    """Process articles from a single URL"""
    if 'baidu.com' in url:
        url = get_baidu_search_url(keyword)
    
    articles = extract_news_articles(url)
    if not isinstance(articles, list):
        return f"Error processing URL {url}: {articles}"
    
    if not articles:
        return f"No articles found for URL {url}"
    
    prompt = f"""
    Please strictly filter out only the latest news directly related to "{keyword}" from the following article list.

    Article List:
    {articles}

    Filtering Criteria:
    1. Must directly mention "{keyword}" in the title or be directly related to {keyword}'s products/events
    2. Must be latest news content, not regular product introduction pages
    3. News must be timely and important

    Please organize qualifying articles in the following format:
    Title,URL

    Requirements:
    1. Use comma as field separator
    2. One article per line
    3. First line as header
    4. If title contains commas, enclose in double quotes
    5. Sort by relevance and importance
    6. Only output articles that are 100% directly related to {keyword}
    """
    return agent.run(prompt, display=False)

def process_articles_with_command(urls: list, keyword: str, search_description: str = None):
    """Process articles from all URLs"""
    load_dotenv()
    
    if not search_description:
        search_description = f"Find latest news related to {keyword}"
    
    agent = Agent(f'''You are a professional information analysis assistant.
Your task is to find articles relevant to user requirements.
User search requirement: {search_description}
''')
    
    try:
        print(f"\nSearch keyword: {keyword}")
        print(f"Search requirement: {search_description}\n")
        
        all_results = []
        for url in urls:
            print(f"\nProcessing URL: {url}")
            result = process_single_url(url, keyword, search_description, agent)
            all_results.append(f"\nResults from {url}:\n{result}")
        
        return "\n".join(all_results)
            
    except Exception as e:
        return f"Processing error: {str(e)}"

# Usage example
if __name__ == "__main__":
    keyword = "new energy vehicles"
    description = "Find all possible updates related to new energy vehicles, only looking for the most directly relevant and latest important information (companies, industry policies, etc.)"
    
    urls = [
        "https://www.dongchedi.com/",
        "https://www.baidu.com/s",
        "https://36kr.com/",
    ]
    
    result = process_articles_with_command(urls, keyword, description)
    print(result)
