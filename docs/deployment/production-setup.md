# 🚀 Production Setup Guide for TicketVault

This guide covers all the steps needed to deploy TicketVault to production.

## 📋 Prerequisites

Before deploying to production, ensure you have:

1. **Domain Name**: Purchase a domain (e.g., `safetransaction.com`)
2. **SSL Certificate**: For HTTPS (Let's Encrypt recommended)
3. **Email Service**: Mailgun or SendGrid account
4. **Payment Processing**: Stripe live account
5. **Server**: VPS or cloud hosting (AWS, DigitalOcean, etc.)
6. **Database**: PostgreSQL or MySQL for production

## 🔧 Step 1: Domain and DNS Setup

### 1.1 Domain Configuration
```bash
# Set up DNS records for safetransaction.app
A     @              YOUR_SERVER_IP
A     www            YOUR_SERVER_IP
CNAME mail           mailgun.org
MX    @              10 mxa.mailgun.org
MX    @              10 mxb.mailgun.org
```

### 1.2 SSL Certificate
```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d safetransaction.app -d www.safetransaction.app
```

## 📧 Step 2: Email Service Setup

### 2.1 Mailgun Setup (Recommended)

1. **Create Mailgun Account**: Sign up at mailgun.com
2. **Add Your Domain**: Add `safetransaction.com` to Mailgun
3. **Verify Domain**: Add DNS records provided by Mailgun
4. **Get API Keys**: Note down your API key and domain

### 2.2 Email Receiving Setup

For Michigan Athletics restriction, you need:

```python
# Create Michigan Athletics email account
MICHIGAN_EMAIL = "safetransaction@umich.edu"  # Request from Michigan IT
MICHIGAN_PASSWORD = "secure_password"

# Add to config
MICHIGAN_ATHLETICS_EMAILS = {
    'username': 'safetransaction@umich.edu',
    'password': 'secure_password',
    'imap_server': 'imap.umich.edu',
    'smtp_server': 'smtp.umich.edu'
}
```

### 2.3 Update Email Configuration

```python
# insta485/config.py - Production settings
import os

class ProductionConfig:
    # Mailgun Production Settings
    MAILGUN_DOMAIN = 'safetransaction.com'
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
    MAILGUN_BASE_URL = f'https://api.mailgun.net/v3/{MAILGUN_DOMAIN}'
    
    # SMTP Settings
    MAIL_SERVER = 'smtp.mailgun.org'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = f'postmaster@{MAILGUN_DOMAIN}'
    MAIL_PASSWORD = os.environ.get('MAILGUN_API_KEY')
    MAIL_DEFAULT_SENDER = f'TicketVault <noreply@{MAILGUN_DOMAIN}>'
```

## 💳 Step 3: Stripe Production Setup

### 3.1 Stripe Account Setup
1. **Create Stripe Account**: Sign up at stripe.com
2. **Complete Business Verification**: Provide business details
3. **Get Live API Keys**: Switch to live mode and get keys
4. **Setup Webhooks**: Configure webhook endpoints

### 3.2 Webhook Configuration
```python
# Add to your Flask app
@app.route('/webhook/stripe', methods=['POST'])
def handle_stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET')
        )
        
        # Handle payment success
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            transaction_id = session['metadata']['transaction_id']
            # Process successful payment
            
    except ValueError:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400
        
    return 'Success', 200
```

### 3.3 Update Stripe Configuration
```python
# Production Stripe settings
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_LIVE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_LIVE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
```

## 🗄️ Step 4: Database Setup

### 4.1 PostgreSQL Setup (Recommended for Production)
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE safetransaction;
CREATE USER safetransaction_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE safetransaction TO safetransaction_user;
```

### 4.2 Database Migration
```python
# Update database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 
    'postgresql://safetransaction_user:secure_password@localhost/safetransaction')

# Migrate from SQLite to PostgreSQL
# Use tools like pgloader or custom migration scripts
```

## 🖥️ Step 5: Server Setup

### 5.1 Server Requirements
- **OS**: Ubuntu 20.04 LTS or newer
- **RAM**: Minimum 2GB, Recommended 4GB+
- **Storage**: Minimum 20GB SSD
- **CPU**: 2+ cores recommended

### 5.2 Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx supervisor redis-server

# Install Node.js for frontend builds
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs
```

### 5.3 Application Deployment
```bash
# Create application directory
sudo mkdir -p /var/www/safetransaction
sudo chown $USER:$USER /var/www/safetransaction

# Clone repository
cd /var/www/safetransaction
git clone https://github.com/yourusername/TicketVault.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Build frontend assets
npm install
npm run build
```

## 🔧 Step 6: Environment Configuration

### 6.1 Create Production Environment File
```bash
# /var/www/safetransaction/.env
FLASK_ENV=production
SECRET_KEY=your_super_secret_key_here
DATABASE_URL=postgresql://safetransaction_user:password@localhost/safetransaction

# Stripe
STRIPE_LIVE_PUBLISHABLE_KEY=pk_live_...
STRIPE_LIVE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Mailgun
MAILGUN_API_KEY=your_mailgun_api_key
MAILGUN_DOMAIN=safetransaction.com

# Michigan Athletics (if needed)
MICHIGAN_EMAIL=safetransaction@umich.edu
MICHIGAN_PASSWORD=secure_password

# Security
ALLOWED_HOSTS=safetransaction.com,www.safetransaction.com
```

### 6.2 Update Configuration Files
```python
# insta485/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Email settings
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
    MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')
    
    # Stripe settings
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_LIVE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_LIVE_SECRET_KEY')
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
```

## 🌐 Step 7: Web Server Configuration

### 7.1 Nginx Configuration
```nginx
# /etc/nginx/sites-available/safetransaction
server {
    listen 80;
    server_name safetransaction.com www.safetransaction.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name safetransaction.com www.safetransaction.com;
    
    ssl_certificate /etc/letsencrypt/live/safetransaction.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/safetransaction.com/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /var/www/safetransaction/insta485/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 7.2 Enable Nginx Site
```bash
sudo ln -s /etc/nginx/sites-available/safetransaction /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔄 Step 8: Process Management

### 8.1 Gunicorn Configuration
```python
# gunicorn_config.py
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
preload_app = True
```

### 8.2 Supervisor Configuration
```ini
# /etc/supervisor/conf.d/safetransaction.conf
[program:safetransaction]
command=/var/www/safetransaction/venv/bin/gunicorn -c gunicorn_config.py insta485:app
directory=/var/www/safetransaction
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/safetransaction/app.log

[program:safetransaction-background]
command=/var/www/safetransaction/venv/bin/python bin/start_background_jobs.py
directory=/var/www/safetransaction
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/safetransaction/background.log
```

### 8.3 Start Services
```bash
sudo mkdir -p /var/log/safetransaction
sudo chown www-data:www-data /var/log/safetransaction
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start safetransaction
sudo supervisorctl start safetransaction-background
```

## 📊 Step 9: Monitoring and Logging

### 9.1 Log Configuration
```python
# insta485/logger_config.py - Production settings
import logging
import logging.handlers

def setup_production_logging():
    # Main application log
    app_handler = logging.handlers.RotatingFileHandler(
        '/var/log/safetransaction/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    app_handler.setLevel(logging.INFO)
    
    # Error log
    error_handler = logging.handlers.RotatingFileHandler(
        '/var/log/safetransaction/error.log',
        maxBytes=10*1024*1024,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    
    # Payment log
    payment_handler = logging.handlers.RotatingFileHandler(
        '/var/log/safetransaction/payments.log',
        maxBytes=10*1024*1024,
        backupCount=10  # Keep more payment logs
    )
    payment_handler.setLevel(logging.INFO)
```

### 9.2 Health Check Endpoint
```python
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        connection = insta485.model.get_db()
        connection.execute("SELECT 1").fetchone()
        
        # Check background jobs
        job_status = app.scheduler.get_jobs()
        
        return {
            'status': 'healthy',
            'timestamp': datetime.datetime.now().isoformat(),
            'database': 'connected',
            'background_jobs': len(job_status),
            'version': '1.0.0'
        }
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500
```

## 🔒 Step 10: Security Hardening

### 10.1 Firewall Configuration
```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 10.2 Security Headers
```python
# Add security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' js.stripe.com; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src 'self' fonts.gstatic.com"
    return response
```

## 🚀 Step 11: Deployment Checklist

### Pre-Deployment
- [ ] Domain purchased and DNS configured
- [ ] SSL certificate installed
- [ ] Email service configured and tested
- [ ] Stripe live keys configured
- [ ] Database migrated and backed up
- [ ] Environment variables set
- [ ] Security headers implemented
- [ ] Monitoring and logging configured

### Deployment
- [ ] Code deployed to server
- [ ] Dependencies installed
- [ ] Database migrations run
- [ ] Static files collected
- [ ] Services started (Nginx, Gunicorn, Supervisor)
- [ ] Background jobs running
- [ ] Health checks passing

### Post-Deployment
- [ ] Test complete user flow (seller → buyer)
- [ ] Test email notifications
- [ ] Test payment processing
- [ ] Test error scenarios
- [ ] Monitor logs for issues
- [ ] Set up automated backups
- [ ] Configure monitoring alerts

## 🔧 Step 12: Maintenance Scripts

### 12.1 Backup Script
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump safetransaction > /backups/safetransaction_$DATE.sql
find /backups -name "safetransaction_*.sql" -mtime +7 -delete
```

### 12.2 Log Rotation
```bash
# /etc/logrotate.d/safetransaction
/var/log/safetransaction/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        supervisorctl restart safetransaction
    endscript
}
```

## 📞 Support and Monitoring

### Key Metrics to Monitor
- Transaction success rate
- Payment processing time
- Email delivery rate
- Server response time
- Error rates
- Background job status

### Alerts to Set Up
- Payment failures
- Email delivery failures
- High error rates
- Server downtime
- Database connection issues
- Background job failures

## 🎯 Production URLs

After deployment, your system will be available at:
- **Main Site**: https://safetransaction.com
- **Admin Dashboard**: https://safetransaction.com/admin
- **Health Check**: https://safetransaction.com/health
- **API Endpoints**: https://safetransaction.com/api/
- **Webhooks**: https://safetransaction.com/webhook/

## 🆘 Troubleshooting

### Common Issues
1. **Email not sending**: Check Mailgun configuration and DNS records
2. **Payments failing**: Verify Stripe webhook endpoints and API keys
3. **Background jobs not running**: Check Supervisor logs and restart services
4. **Database connection errors**: Verify database credentials and connection string
5. **SSL certificate issues**: Renew Let's Encrypt certificates

### Emergency Contacts
- **Stripe Support**: https://support.stripe.com
- **Mailgun Support**: https://help.mailgun.com
- **Server Provider**: Your hosting provider's support

---

🎉 **Congratulations!** Your TicketVault platform is now ready for production use!
