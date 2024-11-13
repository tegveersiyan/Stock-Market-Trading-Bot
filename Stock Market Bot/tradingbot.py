from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime
from alpaca_trade_api import REST 
from timedelta import Timedelta

API_KEY = "PKEYH0L5F2DWSBAAU1P6"
API_SECRET = "Ivfb5h6yXo6aZuHK9ium1HSGXwFW5qcuXBSAe33t"
BASE_URL = "https://paper-api.alpaca.markets/v2"

ALPACA_CREDS = {
    "API_KEY":API_KEY,
    "API_SECRET": API_SECRET,
    "PAPER": True
}

class MLTrader(Strategy):
    def initialize(self, symbol:str="SPY", cash_at_risk:float=0.5):
        self.symbol = symbol
        self.sleeptime = "24H"
        self.last_trade = None
        self.cash_at_risk = cash_at_risk
        self.api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quanitity = round(cash * self.cash_at_risk / last_price, 0)
        return cash, last_price, quanitity
    
    def get_dates(self):
        today = self.get_datetime()
        three_days_prior = today - Timedelta(days=3)
        return today.strfttime('%Y-%m-%d'), three_days_prior.strfttime('%Y-%m-%d')

    def get_sentiment(self):
        today, three_days_prior = self.getdates()
        news = self.api.get_news(symbol=self.symbol, start=three_days_prior, end=today)
        news = [ev.__dict__["_raw"]["headline"] for ev in news]
        return news
    
    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()
        
        if cash > last_price:
            if self.last_trade == None:
                news = self.get_news()
                print(news)
                order = self.create_order(self.symbol, 10, "buy", type="bracket", take_profit_price=last_price*1.20)
                stop_loss_price=last_price*0.95
                self.submit_order(order)
                self.last_trade = "buy"

start_date = datetime(2023,12,15)
end_date = datetime(2023,12,31)
broker = Alpaca(ALPACA_CREDS)
strategy = MLTrader(name='mlstrat', broker=broker, parameters={"symbol":"SPY", "cash_at_risk":0.5})
strategy.backtest(YahooDataBacktesting, start_date, end_date, parameters={"symbol":"SPY", "cash_at_risk":0.5})