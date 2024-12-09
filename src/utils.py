import random

class ProxyUserAgentManager:
    def __init__(self):
        # 프록시 리스트
        self.proxies = [
            "http://123.456.78.90:8080",
            "http://98.76.54.32:3128",
            "http://12.34.56.78:80",
            "http://87.65.43.21:8000",
            "https://10.0.0.1:443",
            "https://203.0.113.0:8443",
            "http://192.0.2.0:8080",
            "http://198.51.100.1:1080",
            "https://139.59.123.0:3128",
            "http://165.227.100.10:80",
        ]

        # 유저 에이전트 리스트
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:110.0) Gecko/20100101 Firefox/110.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:105.0) Gecko/20100101 Firefox/105.0",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36",
            "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",
        ]

    def get_next_proxy_user_agent(self):
        # 랜덤으로 프록시와 유저 에이전트를 선택
        proxy = random.choice(self.proxies)
        user_agent = random.choice(self.user_agents)

        # 딕셔너리 형태로 반환
        return {
            "proxy": proxy,
            "user_agent": user_agent
        }