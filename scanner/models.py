from django.db import models
from django.contrib.auth.models import User
import json

class ScanResult(models.Model):
    SCAN_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    SCAN_TOOL_CHOICES = [
        ('zap', 'OWASP ZAP'),
        ('nmap', 'Nmap'),
        ('nikto', 'Nikto'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    target_url = models.URLField(max_length=500)
    tool = models.CharField(max_length=20, choices=SCAN_TOOL_CHOICES, default='zap')
    status = models.CharField(max_length=20, choices=SCAN_STATUS_CHOICES, default='pending')
    scan_config = models.JSONField(default=dict, blank=True)
    results = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tool} scan of {self.target_url} - {self.status}"
    
    @property
    def duration(self):
        if self.completed_at and self.created_at:
            return self.completed_at - self.created_at
        return None
    
    def get_high_risk_alerts(self):
        """Get high risk alerts from ZAP results"""
        if self.tool == 'zap' and self.results:
            alerts = self.results.get('alerts', [])
            return [alert for alert in alerts if alert.get('risk') == 'High']
        return []
    
    def get_medium_risk_alerts(self):
        """Get medium risk alerts from ZAP results"""
        if self.tool == 'zap' and self.results:
            alerts = self.results.get('alerts', [])
            return [alert for alert in alerts if alert.get('risk') == 'Medium']
        return []
    
    def get_low_risk_alerts(self):
        """Get low risk alerts from ZAP results"""
        if self.tool == 'zap' and self.results:
            alerts = self.results.get('alerts', [])
            return [alert for alert in alerts if alert.get('risk') == 'Low']
        return []
    
    def get_info_alerts(self):
        """Get informational alerts from ZAP results"""
        if self.tool == 'zap' and self.results:
            alerts = self.results.get('alerts', [])
            return [alert for alert in alerts if alert.get('risk') == 'Informational']
        return []
