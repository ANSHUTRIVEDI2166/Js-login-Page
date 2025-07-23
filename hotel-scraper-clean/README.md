# Hotel Scraper - Docker Deployment

This project scrapes hotel data from multiple booking websites and provides a FastAPI backend.

## 🚀 Quick Start

### For Windows (Local Development)
```bash
# Build the Docker image
build.bat

# Run locally
docker-compose up -d
```

### For Linux/Hostinger Server
```bash
# Make scripts executable
chmod +x build.sh deploy.sh

# Build (on your local machine)
./build.sh

# Deploy (on your server)
./deploy.sh
```

## 📦 What's Included

- **FastAPI Backend**: `unified_backend.py` - Main API server
- **Web Scrapers**: Playwright-based scrapers for multiple hotel booking sites
- **Docker Setup**: Complete containerization with all dependencies
- **Deployment Scripts**: Automated build and deploy scripts

## 🌐 Supported Platforms

- **Playwright-based**: Booking.com, Agoda, Airbnb, Expedia, Trip.com, Yatra, TravelGuru, Cleartrip
- **Firecrawl-based**: MakeMyTrip (MMT), Goibibo

## 🔧 API Usage

Once deployed, visit `http://your-domain:8000/docs` for interactive API documentation.

### Example API Call:
```bash
curl 'http://your-domain:8000/run-selected/?checkin=2025-07-25&checkout=2025-07-26&hotels=booking&hotels=agoda&user_email=your-email@example.com'
```

## 📋 Parameters

- `checkin`: Check-in date (YYYY-MM-DD)
- `checkout`: Check-out date (YYYY-MM-DD)  
- `hotels`: List of hotel platforms to scrape (can specify multiple)
- `user_email`: Email to send the results to

## 🏗️ Architecture

1. **FastAPI** receives the request
2. **Playwright** downloads HTML from hotel sites
3. **BeautifulSoup** parses the HTML data
4. **Data processing** merges and formats results
5. **Email service** sends Excel file to user

## 🚀 Hostinger Deployment

1. Upload the project files to your Hostinger server
2. Run `./deploy.sh` - it will install Docker if needed
3. Your API will be available at `http://your-domain:8000`

## 🐳 Docker Commands

```bash
# Build image
docker build -t hotel-scraper .

# Run with compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 🔍 Troubleshooting

- **Port conflicts**: Change port in `docker-compose.yml`
- **Memory issues**: Playwright needs at least 2GB RAM
- **Firewall**: Ensure port 8000 is open on your server

## 📧 Email Configuration

Update `send_email.py` with your SMTP credentials before deployment.
