import asyncio

from asynciolimiter import Limiter
from rnet import Client, Impersonate, Proxy
from selectolax.lexbor import LexborHTMLParser


def create_proxy_list(filename: str) -> list:
    proxy_list: list[str] = []
    with open(filename, "r") as file:
        for line in file:
            proxy_list.append("https://" + line.strip())

    return proxy_list


def create_client(proxy_list: list[str]) -> Client:
    if len(proxy_list) == 0:
        raise Exception("Proxy list is empty")

    https_proxies = []

    for ip in proxy_list:
        try:
            Proxy.https(ip)
        except Exception as e:
            print(e)

    return Client(impersonate=Impersonate.Firefox136, proxies=https_proxies)


def parse_resp(response: str):
    html = LexborHTMLParser(response)
    return html


async def fetch_data(client: Client, url: str, limiter: Limiter):
    task = limiter.wrap(client.get(url))
    return await task


async def main():
    proxy_list: list[str] = create_proxy_list("./proxies/http.txt")
    limiter = Limiter(10 / 5)
    client = create_client(proxy_list)
    url = "https://www.scrapethissite.com/pages/forms/?page_num=1"

    response = await fetch_data(client, url, limiter)
    html = parse_resp(await response.text())
    for node in html.body.css(".team"):
        print(node.text())


if __name__ == "__main__":
    asyncio.run(main())
