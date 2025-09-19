# OpenEye - Django + OWASP ZAP Integration

OpenEye is a web application security scanner that integrates Django with OWASP ZAP to provide a beautiful, user-friendly interface for conducting security scans and viewing results.

## Features

- 🔐 **User Authentication**: AWS Cognito integration for secure user management
- 🛡️ **OWASP ZAP Integration**: Full integration with OWASP ZAP for comprehensive security scanning
- 📊 **Real-time Results**: Live scan progress and detailed security findings
- 📈 **Scan History**: Track and review previous scans
- 🎨 **Modern UI**: Beautiful, responsive interface built with Tailwind CSS
- 🔄 **Async Processing**: Background scan processing with real-time updates

## Prerequisites

- Python 3.10+
- Docker (for OWASP ZAP)
- Node.js (for Tailwind CSS compilation)

## Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd OpenEye
```

### 2. Create Virtual Environment

```bash
python -m venv OpenEye-env
source OpenEye-env/bin/activate  # On Windows: OpenEye-env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements_cognito.txt
```

### 4. Database Setup

```bash
python manage.py migrate
python manage.py createsuperuser  # Optional: create admin user
```

### 5. Start OWASP ZAP

```bash
./start_zap.sh
```

This script will:
- Start ZAP in a Docker container
- Enable the API on port 8080
- Make the web UI available on port 8090
- Wait for ZAP to be ready

### 6. Start Django Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the application.

## Usage

### Starting a Scan

1. **Login**: Use the Cognito authentication to sign in
2. **Navigate to Scan**: Click "New Scan" in the sidebar
3. **Configure Scan**:
   - Select OWASP ZAP as the scanning tool
   - Enter the target URL
   - Configure scan options (spider type, scan level, etc.)
4. **Start Scan**: Click "Start Scan" and monitor progress in real-time
5. **View Results**: Once complete, you'll be redirected to the detailed results page

### Viewing Results

The results page provides:
- **Security Summary**: Count of vulnerabilities by risk level
- **Detailed Findings**: Complete list of security issues with:
  - Risk level (High, Medium, Low, Informational)
  - Description and solution
  - Affected URLs and parameters
- **Scan Information**: Target URL, tool used, duration, etc.

### Scan History

Access your scan history to:
- View all previous scans
- Filter by status and tool
- Access detailed results from past scans
- Track your security testing progress

## API Endpoints

The application provides REST API endpoints for programmatic access:

- `POST /scan/api/start-scan/` - Start a new scan
- `GET /scan/api/scan/{id}/status/` - Get scan status
- `GET /scan/api/scan/{id}/results/` - Get scan results
- `GET /scan/api/zap-status/` - Check ZAP availability

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# ZAP Configuration
ZAP_API_URL=http://localhost:8080
ZAP_API_KEY=your_api_key_if_needed

# Database (for production)
DB_NAME=your_db_name
DB_USERNAME=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=your_db_port
```

### ZAP Configuration

The application connects to ZAP via its REST API. Default configuration:
- **API URL**: `http://localhost:8080`
- **API Key**: Not required (disabled for development)
- **Scan Policy**: Default Policy (configurable)

## Architecture

### Backend Components

- **Django Views**: Handle HTTP requests and responses
- **ZAP Integration**: `scanner/zap.py` - Core ZAP API integration
- **Models**: `scanner/models.py` - Database models for scan results
- **Background Processing**: Threading for async scan execution

### Frontend Components

- **Templates**: Django templates with Tailwind CSS
- **JavaScript**: Real-time scan progress and form handling
- **Responsive Design**: Mobile-friendly interface

### Database Schema

- **ScanResult Model**: Stores scan metadata, configuration, and results
- **User Integration**: Links scans to authenticated users
- **JSON Storage**: Flexible storage for scan results and configuration

## Development

### Running Tests

```bash
python manage.py test
```

### Code Style

The project follows Django best practices and PEP 8 for Python code.

### Adding New Scanning Tools

To add support for additional scanning tools:

1. Create a new scanner class in `scanner/zap.py` (or separate file)
2. Add the tool to `SCAN_TOOL_CHOICES` in `models.py`
3. Update the scan logic in `views.py`
4. Add tool-specific options to the scan template

## Troubleshooting

### ZAP Connection Issues

1. **Check ZAP Status**: Visit `http://localhost:8080/JSON/core/view/version/`
2. **Verify Docker**: Ensure ZAP container is running (`docker ps`)
3. **Check Ports**: Ensure ports 8080 and 8090 are available
4. **Restart ZAP**: Use `./start_zap.sh` to restart the container

### Common Issues

- **Import Errors**: Ensure virtual environment is activated
- **Database Errors**: Run `python manage.py migrate`
- **Static Files**: Run `python manage.py collectstatic` (if needed)
- **Permission Errors**: Check file permissions on `start_zap.sh`

## Security Considerations

- **API Security**: ZAP API is disabled by default in development
- **User Authentication**: Implemented via AWS Cognito
- **Data Protection**: Scan results are stored securely in the database
- **Network Security**: Ensure ZAP is only accessible from trusted networks

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the API documentation
- Open an issue on GitHub

---

**Happy Scanning! 🔍🛡️**