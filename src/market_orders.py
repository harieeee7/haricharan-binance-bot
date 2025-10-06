#!/usr/bin/env python3
"""
Market Orders Module for Binance Futures Trading Bot
Handles market order placement with validation and logging
"""

import sys
import argparse
from datetime import datetime
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, FUTURE_ORDER_TYPE_MARKET
import logging

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(module)s | %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MarketOrders')

class MarketOrderBot:
    def __init__(self, api_key, api_secret, testnet=True):
        """Initialize market order bot with Binance client"""
        try:
            self.client = Client(api_key, api_secret, testnet=testnet)
            if testnet:
                self.client.FUTURES_URL = 'https://testnet.binancefuture.com'
            logger.info("Market Order Bot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise

    def validate_inputs(self, symbol, side, quantity):
        """Validate order inputs"""
        if not symbol or len(symbol) < 6:
            raise ValueError("Invalid symbol format")
        
        if side not in ['BUY', 'SELL']:
            raise ValueError("Side must be BUY or SELL")
        
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        logger.info(f"Input validation passed: {symbol} {side} {quantity}")
        return True

    def place_market_order(self, symbol, side, quantity):
        """Place a market order with validation and logging"""
        try:
            # Validate inputs
            self.validate_inputs(symbol, side, quantity)
            
            # Log order attempt
            logger.info(f"Attempting market order: {side} {quantity} {symbol}")
            
            # Place order
            order = self.client.futures_create_order(
                symbol=symbol,
                side=SIDE_BUY if side == 'BUY' else SIDE_SELL,
                type=FUTURE_ORDER_TYPE_MARKET,
                quantity=quantity
            )
            
            # Log successful execution
            logger.info(f"Market order executed successfully: Order ID {order.get('orderId')}")
            logger.info(f"Order details: {order}")
            
            return order
            
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return None
        except Exception as e:
            logger.error(f"Market order failed: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            return None

    def get_account_balance(self):
        """Get account balance for validation"""
        try:
            account = self.client.futures_account()
            balance = account.get('totalWalletBalance', '0')
            logger.info(f"Account balance retrieved: {balance} USDT")
            return float(balance)
        except Exception as e:
            logger.error(f"Failed to get account balance: {e}")
            return 0.0

def main():
    """CLI interface for market orders"""
    parser = argparse.ArgumentParser(description='Binance Futures Market Order Bot')
    parser.add_argument('symbol', help='Trading symbol (e.g., BTCUSDT)')
    parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    parser.add_argument('quantity', type=float, help='Order quantity')
    parser.add_argument('--api_key', required=True, help='Binance API Key')
    parser.add_argument('--api_secret', required=True, help='Binance API Secret')
    parser.add_argument('--testnet', action='store_true', default=True, help='Use testnet (default: True)')
    
    args = parser.parse_args()
    
    try:
        # Initialize bot
        bot = MarketOrderBot(args.api_key, args.api_secret, args.testnet)
        
        # Check account balance
        balance = bot.get_account_balance()
        if balance <= 0:
            logger.warning("Account balance is zero or unavailable")
        
        # Place market order
        order = bot.place_market_order(args.symbol.upper(), args.side.upper(), args.quantity)
        
        if order:
            print(f"✅ Market order placed successfully!")
            print(f"Order ID: {order.get('orderId')}")
            print(f"Status: {order.get('status')}")
            print(f"Executed Quantity: {order.get('executedQty')}")
        else:
            print("❌ Market order failed. Check logs for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Market order bot terminated by user")
    except Exception as e:
        logger.error(f"Fatal error in market order bot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()