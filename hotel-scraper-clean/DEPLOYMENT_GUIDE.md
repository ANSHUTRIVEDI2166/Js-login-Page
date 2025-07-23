# 🚀 Hotel Scraper Deployment Guide

## 📋 What Your Boss Wants
Your boss wants this hotel scraping app hosted on **Hostinger** with Docker. Here's exactly what to do:

## ⚡ Option 1: Quick Docker Setup (Recommended)

### Step 1: Install Docker Desktop (on your Windows machine)
1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/
2. Install and restart your computer
3. Start Docker Desktop

### Step 2: Build and Test Locally
```powershell
# Navigate to your project
cd "c:\Users\Anshu\Desktop\ALL_HOTEL-20250527T062616Z-1-001 - Copy_updated_retries"

# Build the Docker image
docker build -t hotel-scraper .

# Test it locally
docker-compose up -d

# Check if it's working
docker-compose ps
```

### Step 3: Access Your API
- Open: http://localhost:8000/docs
- Test the API with your hotel scraping endpoints

### Step 4: Deploy to Hostinger
```powershell
# Save Docker image for upload
docker save hotel-scraper:latest > hotel-scraper.tar

# Upload this .tar file to your Hostinger server
```

## 🔧 Option 2: Direct Python Deployment (Alternative)

If Docker is giving you trouble, you can deploy directly with Python:

### On Hostinger Server:
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium firefox
playwright install-deps

# Run the application
cd ALL_HOTEL
uvicorn unified_backend:app --host 0.0.0.0 --port 8000
```

## 🌐 What Your Boss Will See

Once deployed, your boss can:

1. **View API Documentation**: `http://your-domain:8000/docs`
2. **Test the API**: 
   ```
   http://your-domain:8000/run-selected/?checkin=2025-07-25&checkout=2025-07-26&hotels=booking&hotels=agoda&user_email=boss@company.com
   ```
3. **Get Results**: Excel file emailed automatically

## 📊 Supported Hotel Sites
- ✅ Booking.com
- ✅ Agoda  
- ✅ Airbnb
- ✅ Expedia
- ✅ Trip.com
- ✅ Yatra
- ✅ TravelGuru
- ✅ Cleartrip
- ✅ MakeMyTrip (MMT)
- ✅ Goibibo

## 🚨 Before You Deploy

1. **Update Email Settings** in `ALL_HOTEL/send_email.py`:
   ```python
   msg["From"] = "your-company-email@gmail.com"
   smtp.login("your-email", "your-app-password")
   ```

2. **Set Environment Variables** (for production):
   - Email credentials
   - Firecrawl API key (if using MMT/Goibibo)

## 💰 Hostinger Requirements

- **VPS or Cloud Hosting** (not shared hosting)
- **Minimum**: 2GB RAM, 2GB storage
- **Docker support** (most VPS plans have this)

## 🆘 If You're Stuck

**Tell your boss**: "The app is containerized with Docker and ready for deployment. Just need VPS access to Hostinger to complete the setup."

**Show this working locally first** - it proves the code works!
