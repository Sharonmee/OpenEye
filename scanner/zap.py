import requests
import time
import logging
from typing import Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

# ZAP API configuration
ZAP_API = getattr(settings, 'ZAP_API_URL', "http://localhost:8080")
ZAP_API_KEY = getattr(settings, 'ZAP_API_KEY', None)

class ZAPScanner:
    def __init__(self, api_url: str = ZAP_API, api_key: Optional[str] = ZAP_API_KEY):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        if self.api_key:
            self.session.params = {'apikey': self.api_key}
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to ZAP API with error handling"""
        try:
            url = f"{self.api_url}{endpoint}"
            response = self.session.get(url, params=params or {})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"ZAP API request failed: {e}")
            raise Exception(f"Failed to connect to ZAP API: {e}")
        except ValueError as e:
            logger.error(f"ZAP API returned invalid JSON: {e}")
            raise Exception(f"Invalid response from ZAP API: {e}")
    
    def check_zap_status(self) -> bool:
        """Check if ZAP is running and accessible"""
        try:
            result = self._make_request("/JSON/core/view/version/")
            return 'version' in result
        except:
            return False
    
    def start_spider_scan(self, target_url: str, max_children: int = 10) -> str:
        """Start a spider scan and return scan ID"""
        params = {
            'url': target_url,
            'maxChildren': max_children,
            'recurse': 'true'
        }
        result = self._make_request("/JSON/spider/action/scan/", params)
        scan_id = result.get('scan')
        if not scan_id:
            raise Exception("Failed to start spider scan")
        return str(scan_id)
    
    def get_spider_status(self, scan_id: str) -> int:
        """Get spider scan progress (0-100)"""
        result = self._make_request("/JSON/spider/view/status/", {'scanId': scan_id})
        return int(result.get('status', 0))
    
    def start_active_scan(self, target_url: str, scan_policy: str = "Default Policy") -> str:
        """Start an active scan and return scan ID"""
        params = {
            'url': target_url,
            'scanPolicyName': scan_policy,
            'recurse': 'true'
        }
        result = self._make_request("/JSON/ascan/action/scan/", params)
        scan_id = result.get('scan')
        if not scan_id:
            raise Exception("Failed to start active scan")
        return str(scan_id)
    
    def get_active_scan_status(self, scan_id: str) -> int:
        """Get active scan progress (0-100)"""
        result = self._make_request("/JSON/ascan/view/status/", {'scanId': scan_id})
        return int(result.get('status', 0))
    
    def get_alerts(self, base_url: str = None) -> Dict[str, Any]:
        """Get scan alerts/results"""
        params = {}
        if base_url:
            params['baseurl'] = base_url
        return self._make_request("/JSON/core/view/alerts/", params)
    
    def get_scan_summary(self, base_url: str = None) -> Dict[str, Any]:
        """Get a summary of scan results"""
        alerts = self.get_alerts(base_url)
        summary = {
            'total_alerts': len(alerts.get('alerts', [])),
            'high_risk': 0,
            'medium_risk': 0,
            'low_risk': 0,
            'informational': 0
        }
        
        for alert in alerts.get('alerts', []):
            risk = alert.get('risk', 'Informational')
            if risk == 'High':
                summary['high_risk'] += 1
            elif risk == 'Medium':
                summary['medium_risk'] += 1
            elif risk == 'Low':
                summary['low_risk'] += 1
            else:
                summary['informational'] += 1
        
        return summary

def start_scan(target_url: str, max_children: int = 10, scan_policy: str = "Default Policy") -> Dict[str, Any]:
    """
    Start a complete ZAP scan (spider + active scan) and return results
    
    Args:
        target_url: URL to scan
        max_children: Maximum number of children to crawl
        scan_policy: ZAP scan policy to use
    
    Returns:
        Dictionary containing scan results and summary
    """
    scanner = ZAPScanner()
    
    # Check if ZAP is running
    if not scanner.check_zap_status():
        raise Exception("ZAP is not running or not accessible. Please ensure ZAP is running on the configured port.")
    
    try:
        # 1. Start spider scan
        logger.info(f"Starting spider scan for {target_url}")
        spider_id = scanner.start_spider_scan(target_url, max_children)
        
        # 2. Wait for spider to complete
        logger.info("Waiting for spider scan to complete...")
        while True:
            status = scanner.get_spider_status(spider_id)
            if status >= 100:
                break
            time.sleep(2)
        
        logger.info("Spider scan completed, starting active scan...")
        
        # 3. Start active scan
        active_id = scanner.start_active_scan(target_url, scan_policy)
        
        # 4. Wait for active scan to complete
        logger.info("Waiting for active scan to complete...")
        while True:
            status = scanner.get_active_scan_status(active_id)
            if status >= 100:
                break
            time.sleep(5)
        
        logger.info("Active scan completed, fetching results...")
        
        # 5. Get results
        alerts = scanner.get_alerts(target_url)
        summary = scanner.get_scan_summary(target_url)
        
        return {
            'alerts': alerts.get('alerts', []),
            'summary': summary,
            'target_url': target_url,
            'scan_completed': True
        }
        
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        return {
            'error': str(e),
            'target_url': target_url,
            'scan_completed': False
        }

def get_scan_progress(spider_id: str = None, active_id: str = None) -> Dict[str, int]:
    """Get progress of running scans"""
    scanner = ZAPScanner()
    progress = {}
    
    if spider_id:
        try:
            progress['spider'] = scanner.get_spider_status(spider_id)
        except:
            progress['spider'] = 0
    
    if active_id:
        try:
            progress['active'] = scanner.get_active_scan_status(active_id)
        except:
            progress['active'] = 0
    
    return progress
