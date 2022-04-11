import requests

class Algorand:

    def __init__(self):
        self.url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        self.params = {
            "convert": "USD",
            "symbol": "TRUMP"
        }
        self.headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": "18f9d2bf-6a6b-4c8c-8059-3021fa293b97"
        }

        self.id = Algorand.params = {'convert': 'USD', 'symbol': 'ALGO'}

    def cmc(self):
        data = requests.get(url=self.url, headers=self.headers, params=self.id).json()
        return data

Algo_report = Algorand()



def algoValue():
    crypto = Algo_report.cmc()
    # print(crypto["data"])
    Algo = crypto["data"]["ALGO"]["quote"]["USD"]["price"]
    return round(Algo, 6)

def algo_perc24h():
    crypto = Algo_report.cmc()
    # print(crypto["data"])
    Algo_percent_24h = crypto["data"]["ALGO"]["quote"]["USD"]["percent_change_24h"]
    return round(Algo_percent_24h, 10)


def algo_vol24h():
    crypto = Algo_report.cmc()
    # print(crypto["data"])
    Algo_24h= crypto["data"]["ALGO"]["quote"]["USD"]["volume_24h"]
    return round(Algo_24h, 10)

def algo_marketCap():
    crypto = Algo_report.cmc()
    # print(crypto["data"])
    Algo_marketcap = crypto["data"]["ALGO"]["quote"]["USD"]["market_cap"]
    return round(Algo_marketcap, 10)


