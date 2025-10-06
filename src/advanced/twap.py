#!/usr/bin/env python3
"""
TWAP (Time-Weighted Average Price) Strategy for Binance Futures
Splits large orders into smaller chunks over time to minimize market impact
"""

import sys
import argparse
import time
import threading
from datetime import datetime, timedelta
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, FUTURE_ORDER_TYPE_MARKET, FUTURE_ORDER_TYPE_LIMIT
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
logger = logging.getLogger('TWAPStrategy')

class TWAPBot:
    def __init__(self, api_key, api_secret, testnet=True):
        """Initialize TWAP bot with Binance client"""
        try:
            self.client = Client(api_key, api_secret, testnet=testnet)
            if testnet:
                self.client.FUTURES_URL = 'https://testnet.binancefuture.com'
            self.is_running = False
            self.executed_orders = []
            logger.info("TWAP Strategy Bot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise

    def validate_twap_inputs(self, symbol, side, total_quantity, duration_minutes, interval_seconds):
        """Validate TWAP strategy inputs"""
        if not symbol or len(symbol) < 6:
            raise ValueError("Invalid symbol format")
        
        if side not in ['BUY', 'SELL']:
            raise ValueError("Side must be BUY or SELL")
        
        if total_quantity <= 0:
            raise ValueError("Total quantity must be positive")
            
        if duration_minutes <= 0:
            raise ValueError("Duration must be positive")
            
        if interval_seconds <= 0:
            raise ValueError("Interval must be positive")
            
        if interval_seconds >= duration_minutes * 60:
            raise ValueError("Interval must be less than total duration")
        
        # Calculate number of orders
        num_orders = int((duration_minutes * 60) / interval_seconds)
        if num_orders < 2:
            raise ValueError("Duration and interval must allow for at least 2 orders")
        
        logger.info(f"TWAP validation passed: {num_orders} orders over {duration_minutes} minutes")
        return True

    def calculate_twap_chunks(self, total_quantity, duration_minutes, interval_seconds):
        """Calculate order sizes and timing for TWAP execution"""
        num_orders = int((duration_minutes * 60) / interval_seconds)
        base_chunk_size = total_quantity / num_orders
        
        # Add some randomization to avoid predictable patterns
        chunks = []
        remaining_quantity = total_quantity
        
        for i in range(num_orders - 1):
            # Vary chunk size by ±10% for unpredictability
            variation = base_chunk_size * 0.1 * (0.5 - (i % 10) / 10)
            chunk_size = base_chunk_size + variation
            chunk_size = min(chunk_size, remaining_quantity)
            chunk_size = round(chunk_size, 6)  # Round to 6 decimals
            
            chunks.append(chunk_size)
            remaining_quantity -= chunk_size
        
        # Add remaining quantity to last chunk
        if remaining_quantity > 0:
            chunks.append(round(remaining_quantity, 6))
        
        logger.info(f"TWAP chunks calculated: {len(chunks)} orders, sizes: {chunks}")
        return chunks

    def execute_twap_strategy(self, symbol, side, total_quantity, duration_minutes, interval_seconds, order_type='MARKET'):
        """Execute TWAP strategy with time-weighted order placement"""
        try:
            # Validate inputs
            self.validate_twap_inputs(symbol, side, total_quantity, duration_minutes, interval_seconds)
            
            # Calculate chunks
            chunks = self.calculate_twap_chunks(total_quantity, duration_minutes, interval_seconds)
            
            # Initialize execution tracking
            self.is_running = True
            self.executed_orders = []
            start_time = datetime.now()
            
            logger.info(f"Starting TWAP execution: {side} {total_quantity} {symbol} over {duration_minutes} min")
            
            for i, chunk_size in enumerate(chunks):
                if not self.is_running:
                    logger.info("TWAP execution stopped by user")
                    break
                
                try:
                    # Place individual order
                    if order_type == 'MARKET':
                        order = self.client.futures_create_order(
                            symbol=symbol,
                            side=SIDE_BUY if side == 'BUY' else SIDE_SELL,
                            type=FUTURE_ORDER_TYPE_MARKET,
                            quantity=chunk_size
                        )
                    else:  # LIMIT orders at current market price
                        ticker = self.client.futures_symbol_ticker(symbol=symbol)
                        current_price = float(ticker['price'])
                        # Slight price adjustment for limit orders
                        limit_price = current_price * (1.001 if side == 'BUY' else 0.999)
                        
                        order = self.client.futures_create_order(
                            symbol=symbol,
                            side=SIDE_BUY if side == 'BUY' else SIDE_SELL,
                            type=FUTURE_ORDER_TYPE_LIMIT,
                            timeInForce='GTC',
                            quantity=chunk_size,
                            price=limit_price
                        )
                    
                    self.executed_orders.append(order)
                    executed_qty = order.get('executedQty', chunk_size)
                    
                    logger.info(f"TWAP order {i+1}/{len(chunks)} executed: {executed_qty} {symbol}")
                    logger.info(f"Order ID: {order.get('orderId')}, Status: {order.get('status')}")
                    
                    # Wait for next interval (except for last order)
                    if i < len(chunks) - 1:
                        time.sleep(interval_seconds)
                        
                except Exception as e:
                    logger.error(f"TWAP order {i+1} failed: {e}")
                    continue
            
            # Calculate execution summary
            total_executed = sum(float(order.get('executedQty', 0)) for order in self.executed_orders)
            execution_time = datetime.now() - start_time
            
            logger.info(f"TWAP execution completed: {total_executed}/{total_quantity} executed in {execution_time}")
            
            return {
                'strategy': 'TWAP',
                'total_requested': total_quantity,
                'total_executed': total_executed,
                'orders_placed': len(self.executed_orders),
                'execution_time': str(execution_time),
                'orders': self.executed_orders
            }
            
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return None
        except Exception as e:
            logger.error(f"TWAP strategy failed: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            return None

    def stop_twap_execution(self):
        """Stop TWAP execution gracefully"""
        self.is_running = False
        logger.info("TWAP execution stop requested")

    def get_twap_progress(self):
        """Get current TWAP execution progress"""
        return {
            'is_running': self.is_running,
            'orders_executed': len(self.executed_orders),
            'total_executed_qty': sum(float(order.get('executedQty', 0)) for order in self.executed_orders)
        }

def main():
    """CLI interface for TWAP strategy"""
    parser = argparse.ArgumentParser(description='Binance Futures TWAP Strategy Bot')
    parser.add_argument('symbol', help='Trading symbol (e.g., BTCUSDT)')
    parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    parser.add_argument('total_quantity', type=float, help='Total quantity to execute')
    parser.add_argument('duration_minutes', type=int, help='Duration in minutes')
    parser.add_argument('interval_seconds', type=int, help='Interval between orders in seconds')
    parser.add_argument('--api_key', required=True, help='Binance API Key')
    parser.add_argument('--api_secret', required=True, help='Binance API Secret')
    parser.add_argument('--testnet', action='store_true', default=True, help='Use testnet (default: True)')
    parser.add_argument('--order_type', choices=['MARKET', 'LIMIT'], default='MARKET', help='Order type')
    
    args = parser.parse_args()
    
    try:
        # Initialize bot
        bot = TWAPBot(args.api_key, args.api_secret, args.testnet)
        
        # Execute TWAP strategy
        print(f"🕐 Starting TWAP execution...")
        print(f"Symbol: {args.symbol.upper()}")
        print(f"Side: {args.side.upper()}")
        print(f"Total Quantity: {args.total_quantity}")
        print(f"Duration: {args.duration_minutes} minutes")
        print(f"Interval: {args.interval_seconds} seconds")
        print(f"Press Ctrl+C to stop execution\n")
        
        result = bot.execute_twap_strategy(
            args.symbol.upper(),
            args.side.upper(),
            args.total_quantity,
            args.duration_minutes,
            args.interval_seconds,
            args.order_type
        )
        
        if result:
            print(f"\n✅ TWAP execution completed!")
            print(f"Total Executed: {result['total_executed']}/{result['total_requested']}")
            print(f"Orders Placed: {result['orders_placed']}")
            print(f"Execution Time: {result['execution_time']}")
            print(f"Strategy: {result['strategy']}")
        else:
            print("❌ TWAP execution failed. Check logs for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        bot.stop_twap_execution()
        logger.info("TWAP strategy terminated by user")
        print("\n⏹️  TWAP execution stopped by user")
    except Exception as e:
        logger.error(f"Fatal error in TWAP strategy: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()