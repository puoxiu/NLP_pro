from pocketflow import Node, BatchNode

from utils.crawl_webpage import crawl_webpage
from utils.url_validator import filter_valid_urls
from logger import ColoredLogger

class CrawlAndExtract(BatchNode):
    """批量处理多个网址，同时提取干净文本内容，并发现这些页面中的所有链接"""

    def prep(self, shared):
        # 返回： (url_idx, url) 的元组列表
        urls_to_crawl = []
        for url_idx in shared.get("urls_to_process", []):
            if url_idx < len(shared.get("all_discovered_urls", [])):
                urls_to_crawl.append((url_idx, shared["all_discovered_urls"][url_idx]))
        
        return urls_to_crawl

    def exec(self, prep_res):
        """处理一个url，爬取其content 和 页面包含的其它links"""
        url_idx, url = prep_res
        content, links = crawl_webpage(url)
        return url_idx, content, links
    
    def exec_fallback(self, prep_res, exc):
        """爬取失败时的回退机制。链接值为“None”表示爬取失败"""
        url_idx, url = prep_res
        ColoredLogger.error(f"Error crawling {url}: {exc}")
        return url_idx, f"Error crawling page", None

    def post(self, shared, prep_res, exec_res_list):
        """Store results and update URL tracking"""
        new_urls = []
        content_max_chars = shared.get("content_max_chars", 10000)
        max_links_per_page = shared.get("max_links_per_page", 100)
        
        successful_crawls = 0
        for url_idx, content, links in exec_res_list:
            # This part only runs for successful crawls
            successful_crawls += 1
            
            # Truncate content to max chars
            truncated_content = content[:content_max_chars]
            if len(content) > content_max_chars:
                truncated_content += f"\n... [Content truncated - original length: {len(content)} chars]"
            
            shared["url_content"][url_idx] = truncated_content
            shared["visited_urls"].add(url_idx)
            
            valid_links = filter_valid_urls(links, shared["allowed_domains"])
            
            if len(valid_links) > max_links_per_page:
                valid_links = valid_links[:max_links_per_page]
            
            link_indices = []
            for link in valid_links:
                if link not in shared["all_discovered_urls"]:
                    shared["all_discovered_urls"].append(link)
                    new_urls.append(len(shared["all_discovered_urls"]) - 1)
                link_idx = shared["all_discovered_urls"].index(link)
                link_indices.append(link_idx)
            
            shared["url_graph"][url_idx] = link_indices
        
        shared["urls_to_process"] = []
        
        if successful_crawls > 0 and "progress_queue" in shared:
            # Show which pages were actually crawled
            crawled_urls = []
            for url_idx, content, links in exec_res_list:
                if links is not None:  # Only successful crawls
                    crawled_urls.append(shared["all_discovered_urls"][url_idx])
            
            if crawled_urls:
                if len(crawled_urls) == 1:
                    crawl_message = f'Crawled 1 page:<ul><li><a href="{crawled_urls[0]}" target="_blank" style="color: var(--primary); text-decoration: none;">{crawled_urls[0]}</a></li></ul>'
                else:
                    crawl_message = f'Crawled {len(crawled_urls)} pages:<ul>'
                    for url in crawled_urls:
                        crawl_message += f'<li><a href="{url}" target="_blank" style="color: var(--primary); text-decoration: none;">{url}</a></li>'
                    crawl_message += '</ul>'
                shared["progress_queue"].put_nowait(crawl_message)

        ColoredLogger.success(f"Crawled {len(exec_res_list)} pages. Total discovered URLs: {len(shared['all_discovered_urls'])}")

