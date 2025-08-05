from urllib.parse import urlparse

def is_basic_valid_url(url):
    """
    检查 URL 是否符合最基本的格式要求（不限制域名，仅验证结构）
        1.协议（scheme）必须是 http 或 https；2.网络位置（netloc）必须存在
    """
    parsed = urlparse(url)
    return parsed.scheme in ('http', 'https') and bool(parsed.netloc)


def is_valid_url(url, allowed_prefixes_or_domains):
    """
    检查URL是否有效，不仅要求格式基本有效，还需符合允许的前缀或域名规则。
    参数 allowed_prefixes_or_domains 即自定义的域名规则
    
    """
    parsed = urlparse(url)
    
    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
        return False
    
    url_lower = url.lower()
    domain = parsed.netloc.lower()
    
    # # 移除域名中的端口（若存在），例如"example.com:80" → "example.com"
    if ':' in domain:
        domain = domain.split(':')[0]
    
    # 遍历所有允许的规则，判断URL是否符合其中任意一条
    for allowed in allowed_prefixes_or_domains:
        allowed_lower = allowed.lower()
        
        # 判断当前允许的规则是否为「URL前缀形式」
        if allowed_lower.startswith(('http://', 'https://')):
            if url_lower.startswith(allowed_lower):
                return True
        else:
        # 当前允许的规则时域名匹配
            # 不含协议和路径，如规则是"example.com"， url可以是example.com， 也可以是home.example.com）
            if domain == allowed_lower or domain.endswith('.' + allowed_lower):
                return True
    
    return False


def filter_valid_urls(urls, allowed_prefixes_or_domains):
    if not allowed_prefixes_or_domains:
        return [url for url in urls if is_basic_valid_url(url)]
    
    return [url for url in urls if is_valid_url(url, allowed_prefixes_or_domains)]



if __name__ == "__main__":
    test_urls = [
        "https://www.stats.gov.cn/sj/sjjd/202507/t20250727_1960503.html",
        "https://www.stats.gov.cn/sj/sjjd/202507/t20250727_1960503.html", 
        "https://www.stats.gov.cn/sj/xwfbh/fbhwd/202506/t20250616_1960173.html",
        "https://www.stats.gov.cn/sj/",
        "invalid-url"
    ]
    
    print("=== Testing URL prefix matching ===")
    allowed_prefixes = ["https://www.stats.gov.cn/", "stats.gov.cn"]
    
    for url in test_urls:
        valid = is_valid_url(url, allowed_prefixes)
        print(f"{url}: {'✓' if valid else '✗'}")
    
    print("==" * 50)
    print(f"\nFiltered URLs: {filter_valid_urls(test_urls, allowed_prefixes)}")
    