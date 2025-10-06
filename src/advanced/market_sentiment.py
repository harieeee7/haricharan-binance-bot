#!/usr/bin/env python3
"""
Market Sentiment Integration Module
Integrates Fear & Greed Index for enhanced trading decisions
"""

import sys
import requests
import json
from datetime import datetime
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
logger = logging.getLogger('MarketSentiment')

class MarketSentimentAnalyzer:
    def __init__(self):
        """Initialize market sentiment analyzer"""
        self.fear_greed_data = None
        logger.info("Market Sentiment Analyzer initialized")

    def load_fear_greed_data(self, file_path=None, url=None):
        """Load Fear & Greed Index data from file or URL"""
        try:
            if file_path:
                # Load from local file
                with open(file_path, 'r') as f:
                    self.fear_greed_data = json.load(f)
                logger.info(f"Fear & Greed data loaded from file: {file_path}")
            elif url:
                # Load from URL (if available)
                response = requests.get(url)
                response.raise_for_status()
                self.fear_greed_data = response.json()
                logger.info(f"Fear & Greed data loaded from URL: {url}")
            else:
                # Sample data for demonstration if no source provided
                self.fear_greed_data = {
                    "current_index": 45,
                    "classification": "Fear",
                    "timestamp": datetime.now().isoformat(),
                    "historical": [
                        {"date": "2025-10-01", "value": 42, "classification": "Fear"},
                        {"date": "2025-10-02", "value": 38, "classification": "Fear"},
                        {"date": "2025-10-03", "value": 45, "classification": "Fear"}
                    ]
                }
                logger.info("Using sample Fear & Greed data for demonstration")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load Fear & Greed data: {e}")
            return False

    def get_current_sentiment(self):
        """Get current market sentiment"""
        if not self.fear_greed_data:
            logger.warning("No Fear & Greed data available")
            return None
        
        current_index = self.fear_greed_data.get("current_index", 50)
        classification = self.classify_sentiment(current_index)
        
        logger.info(f"Current sentiment: {classification} (Index: {current_index})")
        
        return {
            "index": current_index,
            "classification": classification,
            "timestamp": datetime.now().isoformat()
        }

    def classify_sentiment(self, index):
        """Classify sentiment based on Fear & Greed Index"""
        if index >= 75:
            return "Extreme Greed"
        elif index >= 55:
            return "Greed"
        elif index >= 45:
            return "Neutral"
        elif index >= 25:
            return "Fear"
        else:
            return "Extreme Fear"

    def get_trading_recommendation(self, sentiment_data=None):
        """Get trading recommendation based on sentiment"""
        if not sentiment_data:
            sentiment_data = self.get_current_sentiment()
        
        if not sentiment_data:
            return {"action": "HOLD", "reason": "No sentiment data available"}
        
        index = sentiment_data["index"]
        classification = sentiment_data["classification"]
        
        # Contrarian trading strategy based on sentiment
        if index <= 20:  # Extreme Fear
            recommendation = {
                "action": "BUY",
                "reason": "Extreme fear indicates potential buying opportunity",
                "confidence": "HIGH",
                "risk_level": "MEDIUM"
            }
        elif index <= 35:  # Fear
            recommendation = {
                "action": "BUY",
                "reason": "Fear sentiment suggests market may be oversold",
                "confidence": "MEDIUM",
                "risk_level": "MEDIUM"
            }
        elif index >= 80:  # Extreme Greed
            recommendation = {
                "action": "SELL",
                "reason": "Extreme greed indicates potential market top",
                "confidence": "HIGH",
                "risk_level": "MEDIUM"
            }
        elif index >= 65:  # Greed
            recommendation = {
                "action": "SELL",
                "reason": "Greed sentiment suggests market may be overbought",
                "confidence": "MEDIUM",
                "risk_level": "MEDIUM"
            }
        else:  # Neutral
            recommendation = {
                "action": "HOLD",
                "reason": "Neutral sentiment - no clear directional bias",
                "confidence": "LOW",
                "risk_level": "LOW"
            }
        
        logger.info(f"Trading recommendation: {recommendation['action']} - {recommendation['reason']}")
        return recommendation

    def analyze_historical_trend(self, days=7):
        """Analyze historical sentiment trend"""
        if not self.fear_greed_data or "historical" not in self.fear_greed_data:
            logger.warning("No historical data available")
            return None
        
        historical = self.fear_greed_data["historical"][-days:]
        
        if len(historical) < 2:
            return None
        
        # Calculate trend
        start_value = historical[0]["value"]
        end_value = historical[-1]["value"]
        change = end_value - start_value
        change_percent = (change / start_value) * 100
        
        trend_analysis = {
            "period_days": len(historical),
            "start_value": start_value,
            "end_value": end_value,
            "change": change,
            "change_percent": round(change_percent, 2),
            "trend": "IMPROVING" if change > 5 else "DECLINING" if change < -5 else "STABLE"
        }
        
        logger.info(f"Sentiment trend analysis: {trend_analysis['trend']} ({change_percent:.1f}%)")
        return trend_analysis

    def generate_sentiment_report(self):
        """Generate comprehensive sentiment analysis report"""
        current = self.get_current_sentiment()
        recommendation = self.get_trading_recommendation(current)
        trend = self.analyze_historical_trend()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "current_sentiment": current,
            "trading_recommendation": recommendation,
            "trend_analysis": trend,
            "summary": {
                "sentiment_score": current["index"] if current else 50,
                "primary_action": recommendation["action"],
                "confidence_level": recommendation["confidence"],
                "key_insight": recommendation["reason"]
            }
        }
        
        logger.info("Generated comprehensive sentiment report")
        return report

def main():
    """CLI interface for sentiment analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Market Sentiment Analysis with Fear & Greed Index')
    parser.add_argument('--data_file', help='Path to Fear & Greed data file')
    parser.add_argument('--data_url', help='URL to Fear & Greed data')
    parser.add_argument('--report', action='store_true', help='Generate full sentiment report')
    parser.add_argument('--recommendation', action='store_true', help='Get trading recommendation')
    
    args = parser.parse_args()
    
    try:
        # Initialize analyzer
        analyzer = MarketSentimentAnalyzer()
        
        # Load data
        if not analyzer.load_fear_greed_data(args.data_file, args.data_url):
            print("❌ Failed to load sentiment data")
            sys.exit(1)
        
        if args.report:
            # Generate full report
            report = analyzer.generate_sentiment_report()
            print("\n📊 Market Sentiment Analysis Report")
            print("=" * 50)
            
            if report["current_sentiment"]:
                print(f"Current Index: {report['current_sentiment']['index']}")
                print(f"Classification: {report['current_sentiment']['classification']}")
            
            print(f"\n🎯 Trading Recommendation:")
            print(f"Action: {report['trading_recommendation']['action']}")
            print(f"Reason: {report['trading_recommendation']['reason']}")
            print(f"Confidence: {report['trading_recommendation']['confidence']}")
            
            if report["trend_analysis"]:
                print(f"\n📈 Trend Analysis:")
                print(f"Trend: {report['trend_analysis']['trend']}")
                print(f"Change: {report['trend_analysis']['change_percent']:.1f}%")
        
        elif args.recommendation:
            # Get trading recommendation only
            recommendation = analyzer.get_trading_recommendation()
            print(f"\n🎯 Trading Recommendation: {recommendation['action']}")
            print(f"Reason: {recommendation['reason']}")
            print(f"Confidence: {recommendation['confidence']}")
        
        else:
            # Default: show current sentiment
            sentiment = analyzer.get_current_sentiment()
            if sentiment:
                print(f"\n📊 Current Market Sentiment:")
                print(f"Index: {sentiment['index']}")
                print(f"Classification: {sentiment['classification']}")
            else:
                print("❌ No sentiment data available")
        
    except KeyboardInterrupt:
        logger.info("Sentiment analysis terminated by user")
    except Exception as e:
        logger.error(f"Fatal error in sentiment analysis: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()