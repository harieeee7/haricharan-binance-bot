#!/usr/bin/env python3
"""
Limit Orders Module for Binance Futures Trading Bot
Handles limit order placement with price validation and logging
"""

import sys
import argparse
from datetime import datetime
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, FUTURE_ORDER_TYPE_LIMIT, TIME_IN_FORCE_GTC
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
logger = logging.getLogger('LimitOrders')

class LimitOrderBot:
    def __init__(self, api_key, api_secret, testnet=True):
        """Initialize limit order bot with Binance client"""
        try:
            self.client = Client(api_key, api_secret, testnet=testnet)
            if testnet:
                self.client.FUTURES_URL = 'https://testnet.binancefuture.com'
            logger.info("Limit Order Bot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise

    def validate_inputs(self, symbol, side, quantity, price):
        """Validate order inputs including price thresholds"""
        if not symbol or len(symbol) < 6:
            raise ValueError("Invalid symbol format")
        
        if side not in ['BUY', 'SELL']:
            raise ValueError("Side must be BUY or SELL")
        
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
            
        if price <= 0:
            raise ValueError("Price must be positive")
        
        # Get current market price for validation
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            current_price = float(ticker['price'])
            price_deviation = abs(price - current_price) / current_price
            
            # Log price analysis
            logger.info(f"Current market price for {symbol}: {current_price}")
            logger.info(f"Limit price: {price}, Deviation: {price_deviation:.2%}")
            
            # Warn if price is significantly different from market
            if price_deviation > 0.1:  # 10% deviation
                logger.warning(f"Limit price deviates {price_deviation:.2%} from market price")
                
        except Exception as e:
            logger.warning(f"Could not fetch current price for validation: {e}")
        
        logger.info(f"Input validation passed: {symbol} {side} {quantity} @ {price}")
        return True

    def place_limit_order(self, symbol, side, quantity, price):
        """Place a limit order with validation and logging"""
        try:
            # Validate inputs
            self.validate_inputs(symbol, side, quantity, price)
            
            # Log order attempt
            logger.info(f"Attempting limit order: {side} {quantity} {symbol} @ {price}")
            
            # Place order
            order = self.client.futures_create_order(
                symbol=symbol,
                side=SIDE_BUY if side == 'BUY' else SIDE_SELL,
                type=FUTURE_ORDER_TYPE_LIMIT,
                timeInForce=TIME_IN_FORCE_GTC,
                quantity=quantity,
                price=price
            )
            
            # Log successful execution
            logger.info(f"Limit order placed successfully: Order ID {order.get('orderId')}")
            logger.info(f"Order details: {order}")
            
            return order
            
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return None
        except Exception as e:
            logger.error(f"Limit order failed: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            return None

    def get_open_orders(self, symbol=None):
        """Get open orders for monitoring"""
        try:
            orders = self.client.futures_get_open_orders(symbol=symbol)
            logger.info(f"Retrieved {len(orders)} open orders")
            return orders
        except Exception as e:
            logger.error(f"Failed to get open orders: {e}")
            return []

    def cancel_order(self, symbol, order_id):
        """Cancel a specific order"""
        try:
            result = self.client.futures_cancel_order(symbol=symbol, orderId=order_id)
            logger.info(f"Order {order_id} cancelled successfully")
            return result
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return None

def main():
    """CLI interface for limit orders"""
    parser = argparse.ArgumentParser(description='Binance Futures Limit Order Bot')
    parser.add_argument('symbol', help='Trading symbol (e.g., BTCUSDT)')
    parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    parser.add_argument('quantity', type=float, help='Order quantity')
    parser.add_argument('price', type=float, help='Limit price')
    parser.add_argument('--api_key', required=True, help='Binance API Key')
    parser.add_argument('--api_secret', required=True, help='Binance API Secret')
    parser.add_argument('--testnet', action='store_true', default=True, help='Use testnet (default: True)')
    parser.add_argument('--check_orders', action='store_true', help='Check open orders after placement')
    
    args = parser.parse_args()
    
    try:
        # Initialize bot
        bot = LimitOrderBot(args.api_key, args.api_secret, args.testnet)
        
        # Place limit order
        order = bot.place_limit_order(args.symbol.upper(), args.side.upper(), args.quantity, args.price)
        
        if order:
            print(f"✅ Limit order placed successfully!")
            print(f"Order ID: {order.get('orderId')}")
            print(f"Status: {order.get('status')}")
            print(f"Symbol: {order.get('symbol')}")
            print(f"Side: {order.get('side')}")
            print(f"Quantity: {order.get('origQty')}")
            print(f"Price: {order.get('price')}")
            
            # Check open orders if requested
            if args.check_orders:
                open_orders = bot.get_open_orders(args.symbol.upper())
                print(f"\n📋 Open orders for {args.symbol.upper()}: {len(open_orders)}")
        else:
            print("❌ Limit order failed. Check logs for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Limit order bot terminated by user")
    except Exception as e:
        logger.error(f"Fatal error in limit order bot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()