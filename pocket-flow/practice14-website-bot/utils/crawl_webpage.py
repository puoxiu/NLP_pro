import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

def crawl_webpage(url, delay_after_load=3):
    """
    使用crawl4ai爬取网页，提取markdown格式内容和所有链接。
        https://github.com/weidwonder/crawl4ai-mcp-server
    """
    async def _async_crawl():
        config = CrawlerRunConfig(
            wait_until="load",
            delay_before_return_html=delay_after_load,
        )
        
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url, config=config)
            
            if not result or not result.success:
                raise Exception(f"Failed to crawl {url}. Error: {result.error_message if result else 'Unknown error'}")
                
            clean_text = result.markdown

            # 合并内部链接和外部链接
            all_link_objects = result.links.get('internal', []) + result.links.get('external', [])
            links = [link.get('href') for link in all_link_objects if link.get('href')]
            
            return clean_text, links
            
    return asyncio.run(_async_crawl())




if __name__ == "__main__":
    
    test_url = "https://www.stats.gov.cn/sj/zxfb/202507/t20250731_1960553.html"
    
    content, links = crawl_webpage(test_url)
    print("==" * 50)
    print("爬取成功，开始保存内容...")
    
    content_filename = "data/crawled_content.md"
    with open(content_filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Markdown内容已保存至：{content_filename}")
    
    links_filename = "data/crawled_links_.txt"
    with open(links_filename, "w", encoding="utf-8") as f:
        for link in links:
            f.write(link + "\n")  # 每个链接占一行
    print(f"链接列表已保存至：{links_filename}")


    # if content:
    #     print(f"Content length: {len(content)}")
    #     print(f"Content preview: {content[:100000]}{'...' if len(content) > 100000 else ''}")
    
    # print("==" * 50)
    
    # if links:
    #     print(f"\nFound {len(links)} unique links:")
    #     for link in links[:5]:
    #         print(f"  {link}")
        
    #     if len(links) > 5:
    #         print(f"  ... and {len(links) - 5} more") 