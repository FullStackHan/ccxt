# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.base.exchange import Exchange
import base64
import hashlib
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import ArgumentsRequired


class gemini (Exchange):

    def describe(self):
        return self.deep_extend(super(gemini, self).describe(), {
            'id': 'gemini',
            'name': 'Gemini',
            'countries': ['US'],
            'rateLimit': 1500,  # 200 for private API
            'version': 'v1',
            'has': {
                'fetchDepositAddress': False,
                'createDepositAddress': True,
                'CORS': False,
                'fetchBidsAsks': False,
                'fetchTickers': False,
                'fetchMyTrades': True,
                'fetchOrder': True,
                'fetchOrders': False,
                'fetchOpenOrders': True,
                'fetchClosedOrders': False,
                'createMarketOrder': False,
                'withdraw': True,
                'fetchTransactions': True,
                'fetchWithdrawals': False,
                'fetchDeposits': False,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27816857-ce7be644-6096-11e7-82d6-3c257263229c.jpg',
                'api': 'https://api.gemini.com',
                'www': 'https://gemini.com',
                'doc': [
                    'https://docs.gemini.com/rest-api',
                    'https://docs.sandbox.gemini.com',
                ],
                'test': 'https://api.sandbox.gemini.com',
                'fees': [
                    'https://gemini.com/fee-schedule/',
                    'https://gemini.com/transfer-fees/',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'symbols',
                        'pubticker/{symbol}',
                        'book/{symbol}',
                        'trades/{symbol}',
                        'auction/{symbol}',
                        'auction/{symbol}/history',
                    ],
                },
                'private': {
                    'post': [
                        'order/new',
                        'order/cancel',
                        'order/cancel/session',
                        'order/cancel/all',
                        'order/status',
                        'orders',
                        'mytrades',
                        'tradevolume',
                        'transfers',
                        'balances',
                        'deposit/{currency}/newAddress',
                        'withdraw/{currency}',
                        'heartbeat',
                        'transfers',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'taker': 0.0035,
                    'maker': 0.001,
                },
            },
        })

    def fetch_markets(self, params={}):
        response = self.publicGetSymbols(params)
        result = []
        for i in range(0, len(response)):
            id = response[i]
            market = id
            baseId = id[0:3]
            quoteId = id[3:6]
            base = baseId.upper()
            quote = quoteId.upper()
            base = self.common_currency_code(base)
            quote = self.common_currency_code(quote)
            symbol = base + '/' + quote
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'baseId': baseId,
                'quoteId': quoteId,
                'info': market,
            })
        return result

    def fetch_order_book(self, symbol, limit=None, params={}):
        self.load_markets()
        request = {
            'symbol': self.market_id(symbol),
        }
        if limit is not None:
            request['limit_bids'] = limit
            request['limit_asks'] = limit
        response = self.publicGetBookSymbol(self.extend(request, params))
        return self.parse_order_book(response, None, 'bids', 'asks', 'price', 'amount')

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'symbol': market['id'],
        }
        ticker = self.publicGetPubtickerSymbol(self.extend(request, params))
        timestamp = self.safe_integer(ticker['volume'], 'timestamp')
        baseVolume = self.safe_float(market, 'base')
        quoteVolume = self.safe_float(market, 'quote')
        last = self.safe_float(ticker, 'last')
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': None,
            'low': None,
            'bid': self.safe_float(ticker, 'bid'),
            'bidVolume': None,
            'ask': self.safe_float(ticker, 'ask'),
            'askVolume': None,
            'vwap': None,
            'open': None,
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': self.safe_float(ticker['volume'], baseVolume),
            'quoteVolume': self.safe_float(ticker['volume'], quoteVolume),
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = self.safe_integer(trade, 'timestampms')
        id = self.safe_string(trade, 'tid')
        orderId = self.safe_string(trade, 'order_id')
        fee = self.safe_float(trade, 'fee_amount')
        if fee is not None:
            currency = self.safe_string(trade, 'fee_currency')
            if currency is not None:
                if currency in self.currencies_by_id:
                    currency = self.currencies_by_id[currency]['code']
                currency = self.common_currency_code(currency)
            fee = {
                'cost': self.safe_float(trade, 'fee_amount'),
                'currency': currency,
            }
        price = self.safe_float(trade, 'price')
        amount = self.safe_float(trade, 'amount')
        return {
            'id': id,
            'order': orderId,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['type'].lower(),
            'price': price,
            'cost': price * amount,
            'amount': amount,
            'fee': fee,
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'symbol': market['id'],
        }
        response = self.publicGetTradesSymbol(self.extend(request, params))
        return self.parse_trades(response, market, since, limit)

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostBalances(params)
        result = {'info': response}
        for i in range(0, len(response)):
            balance = response[i]
            currencyId = self.safe_string(balance, 'currency')
            code = self.common_currency_code(currencyId)
            account = {
                'free': self.safe_float(balance, 'available'),
                'used': 0.0,
                'total': self.safe_float(balance, 'amount'),
            }
            account['used'] = account['total'] - account['free']
            result[code] = account
        return self.parse_balance(result)

    def parse_order(self, order, market=None):
        timestamp = self.safe_integer(order, 'timestampms')
        amount = self.safe_float(order, 'original_amount')
        remaining = self.safe_float(order, 'remaining_amount')
        filled = self.safe_float(order, 'executed_amount')
        status = 'closed'
        if order['is_live']:
            status = 'open'
        if order['is_cancelled']:
            status = 'canceled'
        price = self.safe_float(order, 'price')
        average = self.safe_float(order, 'avg_execution_price')
        cost = None
        if filled is not None:
            if average is not None:
                cost = filled * average
        type = self.safe_string(order, 'type')
        if type == 'exchange limit':
            type = 'limit'
        elif type == 'market buy' or type == 'market sell':
            type = 'market'
        else:
            type = order['type']
        fee = None
        symbol = None
        if market is None:
            marketId = self.safe_string(order, 'symbol')
            if marketId in self.markets_by_id:
                market = self.markets_by_id[marketId]
        if market is not None:
            symbol = market['symbol']
        id = self.safe_string(order, 'order_id')
        return {
            'id': id,
            'info': order,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'lastTradeTimestamp': None,
            'status': status,
            'symbol': symbol,
            'type': type,
            'side': order['side'].lower(),
            'price': price,
            'average': average,
            'cost': cost,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'fee': fee,
        }

    def fetch_order(self, id, symbol=None, params={}):
        self.load_markets()
        request = {
            'order_id': id,
        }
        response = self.privatePostOrderStatus(self.extend(request, params))
        return self.parse_order(response)

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        response = self.privatePostOrders(params)
        orders = self.parse_orders(response, None, since, limit)
        if symbol is not None:
            market = self.market(symbol)  # throws on non-existent symbol
            orders = self.filter_by_symbol(orders, market['symbol'])
        return orders

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        nonce = self.nonce()
        request = {
            'client_order_id': str(nonce),
            'symbol': self.market_id(symbol),
            'amount': str(amount),
            'price': str(price),
            'side': side,
            'type': 'exchange limit',  # gemini allows limit orders only
        }
        response = self.privatePostOrderNew(self.extend(request, params))
        return {
            'info': response,
            'id': response['order_id'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        request = {
            'order_id': id,
        }
        return self.privatePostOrderCancel(self.extend(request, params))

    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        if symbol is None:
            raise ArgumentsRequired(self.id + ' fetchMyTrades requires a symbol argument')
        self.load_markets()
        market = self.market(symbol)
        request = {
            'symbol': market['id'],
        }
        if limit is not None:
            request['limit_trades'] = limit
        if since is not None:
            request['timestamp'] = int(since / 1000)
        response = self.privatePostMytrades(self.extend(request, params))
        return self.parse_trades(response, market, since, limit)

    def withdraw(self, code, amount, address, tag=None, params={}):
        self.check_address(address)
        self.load_markets()
        currency = self.currency(code)
        request = {
            'currency': currency['id'],
            'amount': amount,
            'address': address,
        }
        response = self.privatePostWithdrawCurrency(self.extend(request, params))
        return {
            'info': response,
            'id': self.safe_string(response, 'txHash'),
        }

    def nonce(self):
        return self.milliseconds()

    def fetch_transactions(self, code=None, since=None, limit=None, params={}):
        self.load_markets()
        request = {}
        if limit is not None:
            request['limit_transfers'] = limit
        if since is not None:
            request['timestamp'] = since
        response = self.privatePostTransfers(self.extend(request, params))
        return self.parseTransactions(response)

    def parse_transaction(self, transaction, currency=None):
        timestamp = self.safe_integer(transaction, 'timestampms')
        code = None
        if currency is None:
            currencyId = self.safe_string(transaction, 'currency')
            if currencyId in self.currencies_by_id:
                currency = self.currencies_by_id[currencyId]
        if currency is not None:
            code = currency['code']
        address = self.safe_string(transaction, 'destination')
        type = self.safe_string(transaction, 'type')
        if type is not None:
            type = type.lower()
        status = 'pending'
        # When deposits show as Advanced or Complete they are available for trading.
        if transaction['status']:
            status = 'ok'
        fee = None
        feeAmount = self.safe_float(transaction, 'feeAmount')
        if feeAmount is not None:
            fee = {
                'cost': feeAmount,
                'currency': code,
            }
        return {
            'info': transaction,
            'id': self.safe_string(transaction, 'eid'),
            'txid': self.safe_string(transaction, 'txHash'),
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'address': address,
            'tag': None,  # or is it defined?
            'type': type,  # direction of the transaction,('deposit' | 'withdraw')
            'amount': self.safe_float(transaction, 'amount'),
            'currency': code,
            'status': status,
            'updated': None,
            'fee': fee,
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = '/' + self.version + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            self.check_required_credentials()
            nonce = self.nonce()
            request = self.extend({
                'request': url,
                'nonce': nonce,
            }, query)
            payload = self.json(request)
            payload = base64.b64encode(self.encode(payload))
            signature = self.hmac(payload, self.encode(self.secret), hashlib.sha384)
            headers = {
                'Content-Type': 'text/plain',
                'X-GEMINI-APIKEY': self.apiKey,
                'X-GEMINI-PAYLOAD': self.decode(payload),
                'X-GEMINI-SIGNATURE': signature,
            }
        url = self.urls['api'] + url
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'result' in response:
            if response['result'] == 'error':
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response

    def create_deposit_address(self, code, params={}):
        self.load_markets()
        currency = self.currency(code)
        request = {
            'currency': currency['id'],
        }
        response = self.privatePostDepositCurrencyNewAddress(self.extend(request, params))
        address = self.safe_string(response, 'address')
        self.check_address(address)
        return {
            'currency': code,
            'address': address,
            'tag': None,
            'info': response,
        }
