# 🔧 Environment Setup Guide

## 📋 Getting Your Plaid Credentials

### 🧪 Sandbox (Already Configured)
- **Client ID**: `697d07196574b5001ea0cf81`
- **Secret**: `8b682cda9642e57cce2151a40a9635`
- **Status**: ✅ Ready for testing

### 🔧 Development Setup (Real Bank Data)

1. **Go to Plaid Dashboard**: https://dashboard.plaid.com
2. **Sign in** to your account
3. **Go to Team Settings** → **Keys**
4. **Select "Development"** environment
5. **Copy your Development credentials**:
   - Client ID (same as sandbox)
   - Development Secret (different from sandbox)

6. **Update your .env file**:
   ```bash
   PLAID_DEVELOPMENT_SECRET=your_real_development_secret_here
   ```

### 🚀 Production Setup (Live Deployment)

1. **In Plaid Dashboard**, go to Team Settings → **Keys**
2. **Select "Production"** environment
3. **Complete production access** requirements:
   - Account verification
   - Security compliance
   - Business verification

4. **Update your .env file**:
   ```bash
   PLAID_PRODUCTION_SECRET=your_real_production_secret_here
   ```

## 🔄 Using the Environment Switcher

### 📱 Web Interface
1. Go to `http://localhost:5000/environment`
2. Click on the desired environment
3. Confirm the switch
4. System automatically uses correct credentials

### ⚠️ Important Notes

- **Sandbox**: Free, fake data, no costs
- **Development**: Real bank data, per-API costs
- **Production**: Live deployment, per-API costs

- **Never commit real secrets** to version control
- **Keep .env file secure** and private
- **Use different secrets** for each environment

## 🛡️ Security Best Practices

1. **Separate credentials** for each environment
2. **Never share secrets** or commit to Git
3. **Rotate secrets** periodically
4. **Monitor usage** in Plaid dashboard
5. **Use IP whitelisting** if available

## 📊 Cost Management

- **Stay in Sandbox** for development and testing
- **Switch to Development** only when needed
- **Monitor API calls** in Plaid dashboard
- **Set usage alerts** in your Plaid account

## 🚀 Quick Start

1. **Get Development credentials** from Plaid dashboard
2. **Update .env file** with your development secret
3. **Use environment switcher** to switch modes
4. **Connect real banks** in Development mode
5. **Switch back to Sandbox** to save costs

---

**Need help?** Check Plaid's documentation: https://plaid.com/docs/
