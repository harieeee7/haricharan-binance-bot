#!/usr/bin/env python3
"""
OCO Orders Module for Binance Futures Trading Bot
One-Cancels-the-Other orders for simultaneous take-profit and stop-loss
"""

import sys
import argparse
from datetime import datetime
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, TIME_IN_FORCE_GTC
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
logger = logging.getLogger('OCOOrders')

class OCOOrderBot:
    def __init__(self, api_key, api_secret, testnet=True):
        """Initialize OCO order bot with Binance client"""
        try:
            self.client = Client(api_key, api_secret, testnet=testnet)
            if testnet:
                self.client.FUTURES_URL = 'https://testnet.binancefuture.com'
            logger.info("OCO Order Bot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise

    def validate_oco_inputs(self, symbol, side, quantity, price, stop_price, stop_limit_price):
        """Validate OCO order inputs with price relationship checks"""
        if not symbol or len(symbol) < 6:
            raise ValueError("Invalid symbol format")
        
        if side not in ['BUY', 'SELL']:
            raise ValueError("Side must be BUY or SELL")
        
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
            
        if price <= 0 or stop_price <= 0 or stop_limit_price <= 0:
            raise ValueError("All prices must be positive")
        
        # Validate price relationships for OCO logic
        if side == 'SELL':
            if price <= stop_price:
                raise ValueError("For SELL OCO: limit price must be higher than stop price")
            if stop_limit_price >= stop_price:
                raise ValueError("For SELL OCO: stop limit price must be lower than stop price")
        else:  # BUY
            if price >= stop_price:
                raise ValueError("For BUY OCO: limit price must be lower than stop price")
            if stop_limit_price <= stop_price:
                raise ValueError("For BUY OCO: stop limit price must be higher than stop price")
        
        # Get current market price for validation
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            current_price = float(ticker['price'])
            logger.info(f"Current market price for {symbol}: {current_price}")
            logger.info(f"OCO prices - Limit: {price}, Stop: {stop_price}, Stop Limit: {stop_limit_price}")
        except Exception as e:
            logger.warning(f"Could not fetch current price for validation: {e}")
        
        logger.info(f"OCO validation passed: {symbol} {side} {quantity}")
        return True

    def place_oco_order(self, symbol, side, quantity, price, stop_price, stop_limit_price):
        """Place an OCO order with validation and logging"""
        try:
            # Validate inputs
            self.validate_oco_inputs(symbol, side, quantity, price, stop_price, stop_limit_price)
            
            # Log order attempt
            logger.info(f"Attempting OCO order: {side} {quantity} {symbol}")
            logger.info(f"Limit: {price}, Stop: {stop_price}, Stop Limit: {stop_limit_price}")
            
            # Note: Binance Futures doesn't support OCO orders directly
            # We'll simulate by placing both orders and managing them
            orders = []
            
            # Place limit order (take profit)
            limit_order = self.client.futures_create_order(
                symbol=symbol,
                side=SIDE_BUY if side == 'BUY' else SIDE_SELL,
                type='LIMIT',
                timeInForce=TIME_IN_FORCE_GTC,
                quantity=quantity,
                price=price
            )
            orders.append(limit_order)
            logger.info(f"Take profit order placed: {limit_order.get('orderId')}")
            
            # Place stop limit order (stop loss)
            stop_order = self.client.futures_create_order(
                symbol=symbol,
                side=SIDE_BUY if side == 'BUY' else SIDE_SELL,
                type='STOP',
                timeInForce=TIME_IN_FORCE_GTC,
                quantity=quantity,
                price=stop_limit_price,
                stopPrice=stop_price
            )
            orders.append(stop_order)
            logger.info(f"Stop loss order placed: {stop_order.get('orderId')}")
            
            # Log successful execution
            logger.info(f"OCO order pair created successfully")
            
            return {
                'orderListId': f"OCO_{limit_order.get('orderId')}_{stop_order.get('orderId')}",
                'orders': orders,
                'limitOrder': limit_order,
                'stopOrder': stop_order
            }
            
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return None
        except Exception as e:
            logger.error(f"OCO order failed: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            return None

    def monitor_oco_orders(self, symbol, order_ids):
        """Monitor OCO orders and cancel opposite when one executes"""
        try:
            open_orders = self.client.futures_get_open_orders(symbol=symbol)
            open_order_ids = [order['orderId'] for order in open_orders]
            
            executed_orders = []
            for order_id in order_ids:
                if order_id not in open_order_ids:
                    executed_orders.append(order_id)
            
            if executed_orders:
                logger.info(f"Order executed: {executed_orders}")
                # Cancel remaining orders
                for order_id in order_ids:
                    if order_id not in executed_orders and order_id in open_order_ids:
                        try:
                            self.client.futures_cancel_order(symbol=symbol, orderId=order_id)
                            logger.info(f"Cancelled order: {order_id}")
                        except Exception as e:
                            logger.warning(f"Could not cancel order {order_id}: {e}")
            
            return executed_orders
            
        except Exception as e:
            logger.error(f"Failed to monitor OCO orders: {e}")
            return []

def main():
    """CLI interface for OCO orders"""
    parser = argparse.ArgumentParser(description='Binance Futures OCO Order Bot')
    parser.add_argument('symbol', help='Trading symbol (e.g., BTCUSDT)')
    parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    parser.add_argument('quantity', type=float, help='Order quantity')
    parser.add_argument('price', type=float, help='Limit price (take profit)')
    parser.add_argument('stop_price', type=float, help='Stop trigger price')
    parser.add_argument('stop_limit_price', type=float, help='Stop limit price')
    parser.add_argument('--api_key', required=True, help='Binance API Key')
    parser.add_argument('--api_secret', required=True, help='Binance API Secret')
    parser.add_argument('--testnet', action='store_true', default=True, help='Use testnet (default: True)')
    
    args = parser.parse_args()
    
    try:
        # Initialize bot
        bot = OCOOrderBot(args.api_key, args.api_secret, args.testnet)
        
        # Place OCO order
        oco_result = bot.place_oco_order(
            args.symbol.upper(), 
            args.side.upper(), 
            args.quantity, 
            args.price,
            args.stop_price,
            args.stop_limit_price
        )
        
        if oco_result:
            print(f"✅ OCO order pair placed successfully!")
            print(f"OCO ID: {oco_result.get('orderListId')}")
            print(f"Take Profit Order: {oco_result['limitOrder'].get('orderId')}")
            print(f"Stop Loss Order: {oco_result['stopOrder'].get('orderId')}")
            print(f"Status: Both orders active")
        else:
            print("❌ OCO order failed. Check logs for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("OCO order bot terminated by user")
    except Exception as e:
        logger.error(f"Fatal error in OCO order bot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()