import asyncio
import random

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


async def fetch_data(client: Client, url: str, limiter: Limiter, proxies: list[Proxy]):
    proxy_ind = random.randrange(0, len(proxies))
    proxy = proxies[proxy_ind]
    task = limiter.wrap(client.get(url))
    return await task


async def main():
    proxy_list: list[str] = create_proxy_list("./proxies/http.txt")
    limiter = Limiter(10 / 5)
    client = create_client(proxy_list)
    url = "https://www.scrapethissite.com/pages/forms/?page_num=1"

    response = await fetch_data(client, url, limiter, proxy_list)
    html = parse_resp(await response.text())

    data = {}
    for node in html.body.css(".table .team"):
        curr_row = node.css("td")
        data[curr_row[0].text().strip()] = {
            "year": curr_row[1].text().strip(),
            "wins": curr_row[2].text().strip(),
            "losses": curr_row[3].text().strip(),
            "ot-losses": curr_row[4].text().strip(),
            "win-pct": curr_row[5].text().strip(),
            "goals-for": curr_row[6].text().strip(),
            "goals-against": curr_row[7].text().strip(),
            "goal-diff": curr_row[8].text().strip(),
        }

    for team, stats in data.items():
        print(f"{team} Stats:")
        print(f"Year: {stats['year']}")
        print(f"Wins: {stats['wins']}")
        print(f"Losses: {stats['losses']}")
        print(f"Overtime Losses: {stats['ot-losses']}")
        print(f"Win Percentage: {stats['win-pct']}")
        print(f"Goals For: {stats['goals-for']}")
        print(f"Goals Against: {stats['goals-against']}")
        print(f"Goals difference: {stats['goal-diff']}")
        print("-----------------------------------------------\n")


if __name__ == "__main__":
    asyncio.run(main())
