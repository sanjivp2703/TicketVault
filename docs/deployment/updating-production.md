# Update Production Server - safetransaction.app

## Server Information
- **Domain**: safetransaction.app
- **Server IP**: 35.222.52.124
- **Deployment Path**: /var/www/safetransaction
- **GitHub Token**: <GITHUB_TOKEN>

## Step-by-Step Update Process

### 1. Connect to the GCP Server
```bash
# SSH into your GCP VM (replace with your key path if needed)
ssh vedav@35.222.52.124
# OR if using GCP console, use their SSH button
```

### 2. Navigate to the Project Directory
```bash
cd /var/www/safetransaction
```

### 3. Pull Latest Changes from GitHub
```bash
# Set up Git credentials (if not already done)
git config --global credential.helper store

# Pull the latest changes
sudo git pull origin main
# OR if using the token:
sudo git pull https://<GITHUB_TOKEN>@github.com/YOUR_USERNAME/Safe-Transaction.git main
```

### 4. Update Dependencies (if needed)
```bash
# Activate virtual environment
source /var/www/safetransaction/env/bin/activate

# Update Python dependencies
pip install -r requirements.txt

# If you added any npm packages
npm install
```

### 5. Restart the Services
```bash
# Restart the Flask application
sudo systemctl restart safetransaction

# Check status
sudo systemctl status safetransaction

# Restart nginx if needed
sudo systemctl restart nginx
```

### 6. Check for Errors
```bash
# View application logs
sudo journalctl -u safetransaction -n 50 --no-pager

# View nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### 7. Verify the Update
- Visit https://safetransaction.app in your browser
- Test the new features (school switching, buyer email changes)
- Check that everything loads correctly

## Quick Update Script
You can also create a script to do this automatically:

```bash
#!/bin/bash
cd /var/www/safetransaction
sudo git pull origin main
source env/bin/activate
pip install -r requirements.txt
sudo systemctl restart safetransaction
sudo systemctl status safetransaction
```

Save as `update.sh`, make executable with `chmod +x update.sh`, then run `./update.sh`

## Troubleshooting

### If Git Pull Fails
```bash
# Check Git status
sudo git status

# Stash any local changes
sudo git stash

# Pull again
sudo git pull origin main
```

### If Service Doesn't Start
```bash
# Check detailed error logs
sudo journalctl -u safetransaction -xe

# Check if port is already in use
sudo netstat -tulpn | grep :8000

# Restart everything
sudo systemctl stop safetransaction
sudo systemctl start safetransaction
```

### If Changes Don't Appear
```bash
# Clear browser cache
# Force refresh: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)

# Check if static files need rebuilding
cd /var/www/safetransaction
npm run build
```

## Important Notes
- Always backup the database before major updates: `sudo cp /var/www/safetransaction/var/insta485.sqlite3 /var/www/safetransaction/var/insta485.sqlite3.backup`
- Check .env file has all required environment variables
- Make sure file permissions are correct: `sudo chown -R www-data:www-data /var/www/safetransaction`

