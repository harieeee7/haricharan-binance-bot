# How to Get Binance Testnet API Keys

## Step-by-Step Guide to Generate API Credentials

### 1. Register for Binance Testnet Account

1. **Go to Binance Futures Testnet**
   - Visit: https://testnet.binancefuture.com/
   - This is the official testnet environment (not real trading)

2. **Create Account**
   - Click "Register" in the top right corner
   - Enter email address and create password
   - Complete email verification
   - No KYC required for testnet

3. **Login to Your Account**
   - Use your registered credentials
   - You'll see the testnet trading interface

### 2. Get Test USDT Funding

1. **Navigate to Wallet**
   - Click on "Wallet" in the top menu
   - Go to "Futures Wallet"

2. **Get Test Funds**
   - Look for "Get Test Funds" or similar button
   - Click to receive free test USDT (usually 100,000 USDT)
   - These are not real funds - just for testing

### 3. Generate API Keys

1. **Go to API Management**
   - Click on your profile icon (top right)
   - Select "API Management" from dropdown menu
   - Or go directly to account settings

2. **Create New API Key**
   - Click "Create API" or "Create API Key"
   - Enter a label/name for your API (e.g., "Trading Bot")
   - Complete any security verification (email, etc.)

3. **Configure API Permissions**
   - ✅ **Enable Futures Trading** (REQUIRED)
   - ✅ **Enable Reading** (REQUIRED)
   - ❌ Leave "Enable Withdrawals" disabled (not needed)
   - ❌ Leave "Enable Internal Transfer" disabled (not needed)

4. **IP Restriction (Recommended)**
   - Add your computer's IP address for security
   - You can find your IP at: https://whatismyipaddress.com/
   - Or leave unrestricted for testing (less secure)

5. **Save Your Keys**
   - **API Key**: Copy and save this (public key)
   - **Secret Key**: Copy and save this immediately (shown only once!)
   - ⚠️ **IMPORTANT**: Secret key is shown only once - copy it now!

### 4. Test Your API Keys

Once you have your keys, test them with:

```powershell
# Test market order (will fail due to validation but confirms API works)
python src/market_orders.py BTCUSDT BUY 0.01 --api_key "your_api_key_here" --api_secret "your_secret_key_here"
```

### 5. Security Best Practices

1. **Never Share Your Keys**
   - API Key: Can be shared (but avoid it)
   - Secret Key: NEVER share this with anyone

2. **Environment Variables (Recommended)**
   ```powershell
   # Set environment variables (Windows)
   $env:BINANCE_API_KEY="your_api_key_here"
   $env:BINANCE_API_SECRET="your_secret_key_here"
   ```

3. **IP Restrictions**
   - Always set IP restrictions in production
   - For testing, you can leave unrestricted

### 6. Common Issues & Solutions

**Issue**: "Invalid API Key" error
- **Solution**: Double-check you copied the key correctly
- **Solution**: Ensure you're using testnet keys with testnet URL

**Issue**: "Signature failed" error  
- **Solution**: Verify secret key is correct
- **Solution**: Check system time is synchronized

**Issue**: "Permission denied" error
- **Solution**: Enable "Futures Trading" permission in API settings
- **Solution**: Verify IP restriction allows your current IP

### 7. Example API Key Format

```
API Key: 4f8b2c1d9e7a6b5c3d2e1f0a9b8c7d6e5f4g3h2i1j0k9l8m7n6o5p4q3r2s1t0
Secret:  a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

### 8. Ready to Trade!

Once you have your keys, you can run any trading bot command:

```powershell
# Market Order
python src/market_orders.py BTCUSDT BUY 0.01 --api_key YOUR_KEY --api_secret YOUR_SECRET

# Limit Order  
python src/limit_orders.py BTCUSDT SELL 0.01 50000 --api_key YOUR_KEY --api_secret YOUR_SECRET

# Advanced OCO Order
python src/advanced/oco.py BTCUSDT SELL 0.01 55000 45000 44000 --api_key YOUR_KEY --api_secret YOUR_SECRET

# TWAP Strategy
python src/advanced/twap.py BTCUSDT BUY 1.0 60 30 --api_key YOUR_KEY --api_secret YOUR_SECRET
```

---

## Quick Summary:

1. **Register**: https://testnet.binancefuture.com/
2. **Get Test Funds**: Free 100,000 USDT
3. **API Management**: Profile → API Management → Create API
4. **Enable Permissions**: Futures Trading + Reading
5. **Copy Keys**: API Key + Secret Key (save secret immediately!)
6. **Test**: Run any bot command with your keys

**Remember**: This is testnet - no real money involved, safe for testing!

---

## Additional Resources

### Official Documentation
- **Binance Futures API Docs**: https://binance-docs.github.io/apidocs/futures/en/
  - Complete API reference for all endpoints
  - Authentication and signature examples
  - Rate limits and best practices

### Optional Testing Data
- **Historical Data**: https://drive.google.com/file/d/1IAfLZwu6rJzyWKgBToqwSmmVYU6VbjVs/view
  - Historical price data for backtesting strategies
  - Can be used to validate TWAP and other algorithm performance

### Bonus Integration Opportunities  
- **Fear & Greed Index**: https://drive.google.com/file/d/1PgQC0tO8XN-wqkNyghWc_-mnrYv_nhSf/view
  - Market sentiment indicator for advanced trading strategies
  - Could be integrated into decision-making algorithms