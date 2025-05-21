import asyncio
import os
from typing import Union, List
import json
from pathlib import Path
from typing import List
from models.schemas import ResultSchema
from crawl4ai import (
    AsyncWebCrawler, 
    CrawlerRunConfig, 
    CacheMode, 
    BrowserConfig, 
    SemaphoreDispatcher, 
    RateLimiter
)

async def read_urls_from_json(file_path: Union[str, Path]) -> List[str]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    urls = []

    for block in data:
        # 1. URLs trong news_articles
        news_articles = block.get("news_articles")
        if news_articles:
            for article in news_articles:
                url = article.get("url")
                if url:
                    urls.append(url)

        # 2. URLs trong investment_advantages.advantages
        advantages = (block.get("investment_advantages") or {}).get("advantages", [])
        for adv in advantages:
            url = adv.get("url")
            if url:
                urls.append(url)

        # 3. URLs trong investment_attraction_fields.fields
        fields = (block.get("investment_attraction_fields") or {}).get("fields", [])
        for field in fields:
            url = field.get("url")
            if url:
                urls.append(url)

        # 4. URLs trong investment_at_danang.items và các sub_items nếu có
        items = (block.get("investment_at_danang") or {}).get("items", [])
        for item in items:
            url = item.get("url")
            if url:
                urls.append(url)
            sub_items = item.get("sub_items", [])
            if sub_items:
                for sub in sub_items:
                    sub_url = sub.get("url")
                    if sub_url:
                        urls.append(sub_url)

    return urls

import aiohttp
import json
import fitz  # PyMuPDF
from pathlib import Path
from typing import List
from urllib.parse import urlparse

async def download_pdf_and_extract_text(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                pdf_bytes = await resp.read()
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                text = "\n".join(page.get_text() for page in doc)
                return text
            else:
                raise Exception(f"Failed to fetch PDF (status: {resp.status})")

async def crawl_urls(
    urls: List[str], 
    semaphore_count: int = 5,
    check_robots_txt: bool = True,
    cache_mode: CacheMode = CacheMode.ENABLED,
    output_dir: str = None
):
    """Crawl multiple URLs with semaphore-based concurrency and handle .pdf files specially."""
    from pathlib import Path
    import os

    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(
        cache_mode=cache_mode,
        check_robots_txt=check_robots_txt,
        stream=False
    )

    dispatcher = SemaphoreDispatcher(
        semaphore_count=semaphore_count,
        rate_limiter=RateLimiter(base_delay=(1.0, 2.0), max_delay=10.0)
    )

    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)

    print(f"Starting crawl of {len(urls)} URLs with semaphore count: {semaphore_count}")
    print(f"Robots.txt checking: {'Enabled' if check_robots_txt else 'Disabled'}")
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Phân loại URL PDF và URL thường
        pdf_urls = [url for url in urls if url.lower().endswith(".pdf")]
        other_urls = [url for url in urls if not url.lower().endswith(".pdf")]

        # Xử lý PDF trước
        pdf_results = []
        for url in pdf_urls:
            try:
                print(f"Downloading PDF: {url}")
                text = await download_pdf_and_extract_text(url)
                pdf_results.append({
                    "url": url,
                    "success": True,
                    "text": text
                })
                if output_dir:
                    file_name = url.replace("://", "_").replace("/", "_").replace("?", "_")
                    if len(file_name) > 100:
                        file_name = file_name[:100]
                    with open(output_path / f"{file_name}.json", "w", encoding="utf-8") as f:
                        json.dump({"url": url, "text": text}, f, ensure_ascii=False, indent=2)
                    print(f"   PDF content saved to {file_name}.json")
            except Exception as e:
                print(f"{url} - Error reading PDF: {str(e)}")
                pdf_results.append({"url": url, "success": False, "error": str(e)})

        # Xử lý các URL khác bằng crawler
        results = await crawler.arun_many(other_urls, config=run_config, dispatcher=dispatcher)

        for result in results:
            if result.success:
                content_length = len(result.markdown.raw_markdown) if result.markdown else 0
                print(f"{result.url} - {content_length} characters")

                if output_dir:
                    url_filename = result.url.replace("://", "_").replace("/", "_").replace("?", "_")
                    output_file = output_path / f"{url_filename}.md"
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(result.markdown.raw_markdown if result.markdown else "")
                    print(f"   Saved to {output_file}")
            else:
                error_message = result.error_message or "Unknown error"
                if result.status_code == 403 and "robots.txt" in error_message:
                    print(f"{result.url} - Blocked by robots.txt")
                else:
                    print(f"{result.url} - Error: {error_message}")

        return results + pdf_results

async def main():
    # Hardcoded configuration values
    urls_file = "output/https_investdanang.gov.vn_web_guest.json"
    semaphore_count = 5
    check_robots_txt = True
    cache_mode = CacheMode.ENABLED
    output_dir = "Final_Output"
    
    try:
        urls = await read_urls_from_json(urls_file)
        # Remove unnecessary urls
        urls_to_remove = [
                            "https://investdanang.gov.vn/web/guest/thu-tuc-dau-tu",
                            "https://investdanang.gov.vn/web/guest/co-hoi-dau-tu",
                            "https://investdanang.gov.vn/vi/web/guest/thong-tin-ho-tro",
                            "https://investdanang.gov.vn/web/guest/van-ban-phap-luat-2023",
                            "https://investdanang.gov.vn/web/guest/van-ban-dieu-hanh"
                        ]
        urls = [url for url in urls if url not in urls_to_remove]
        sub_urls = [
            # Thủ tục cấp GCN đăng ký đầu tư
            'https://investdanang.gov.vn/web/guest/cap-moi-gcn-dang-ky-dau-tu',
            'https://investdanang.gov.vn/web/guest/dieu-chinh-gcn-dang-ky-dau-tu',
            'https://investdanang.gov.vn/web/guest/tam-ngung-hoat-dong-du-an-dau-tu',
            'https://investdanang.gov.vn/web/guest/cham-dut-hoat-dong-du-an-dau-tu', 
            'https://investdanang.gov.vn/web/guest/thu-tuc-dau-tu-theo-hinh-thuc-hop-von-mua-co-phan-mua-phan-gop-von'
            # Thủ tục cấp GCN đăng ký doanh nghiệp
            'https://dangkykinhdoanh.gov.vn/vn/Pages/Noidunghuongdan.aspx?lhID=1&htID=8',
            'https://dangkykinhdoanh.gov.vn/vn/Pages/Huongdansudungdvc.aspx',
            'https://dangkykinhdoanh.gov.vn/vn/Pages/Nganhnghedautukinhdoanh.aspx'
            ]
        urls.extend(sub_urls)
        if not urls:
            print("No valid URLs found in the file.")
            return
        
        print(f"Found {len(urls)} URLs to crawl")
        
        await crawl_urls(
            urls=urls,
            semaphore_count=semaphore_count,
            check_robots_txt=check_robots_txt,
            cache_mode=cache_mode,
            output_dir=output_dir
        )
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 