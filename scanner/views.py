from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.paginator import Paginator
import json
import threading
from .models import ScanResult
from .zap import start_scan, ZAPScanner

def index(request):
    """Main scanner view - requires login"""
    if request.user.is_authenticated:
        cognito_user_info = request.session.get('cognito_user_info', {})
        user_email = cognito_user_info.get('email', request.user.email)
        return render(request, 'home.html', {
            'user_email': user_email,
            'cognito_user_info': cognito_user_info
        })
    else:
        return HttpResponse("Please log in to access the scanner. <a href='/login/'>Login with Cognito</a>")

def home(request):
    """Home page view"""
    recent_scans = []
    if request.user.is_authenticated:
        recent_scans = ScanResult.objects.filter(user=request.user)[:6]
        cognito_user_info = request.session.get('cognito_user_info', {})
        user_email = cognito_user_info.get('email', request.user.email)
        return render(request, 'home.html', {
            'user': request.user,
            'user_email': user_email,
            'cognito_user_info': cognito_user_info,
            'recent_scans': recent_scans
        })
    else:
        return render(request, 'home.html', {'recent_scans': recent_scans})

@login_required
def scan(request):
    """Scan page view - requires authentication"""
    recent_scans = ScanResult.objects.filter(user=request.user)[:6]
    cognito_user_info = request.session.get('cognito_user_info', {})
    user_email = cognito_user_info.get('email', request.user.email)
    return render(request, 'scanner/scan.html', {
        'user': request.user,
        'user_email': user_email,
        'cognito_user_info': cognito_user_info,
        'recent_scans': recent_scans
    })

@login_required
def scan_results(request, scan_id):
    """View scan results"""
    scan_result = get_object_or_404(ScanResult, id=scan_id, user=request.user)
    cognito_user_info = request.session.get('cognito_user_info', {})
    user_email = cognito_user_info.get('email', request.user.email)
    
    return render(request, 'scanner/results.html', {
        'scan': scan_result,
        'user': request.user,
        'user_email': user_email,
        'cognito_user_info': cognito_user_info
    })

@login_required
def scan_history(request):
    """View scan history"""
    scans = ScanResult.objects.filter(user=request.user)
    paginator = Paginator(scans, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    cognito_user_info = request.session.get('cognito_user_info', {})
    user_email = cognito_user_info.get('email', request.user.email)
    
    return render(request, 'scanner/history.html', {
        'page_obj': page_obj,
        'user': request.user,
        'user_email': user_email,
        'cognito_user_info': cognito_user_info
    })

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def start_scan_api(request):
    """API endpoint to start a new scan"""
    try:
        data = json.loads(request.body)
        target_url = data.get('target_url')
        tool = data.get('tool', 'zap')
        scan_config = data.get('scan_config', {})
        
        if not target_url:
            return JsonResponse({"error": "target_url is required"}, status=400)
        
        # Create scan record
        scan_result = ScanResult.objects.create(
            user=request.user,
            target_url=target_url,
            tool=tool,
            status='pending',
            scan_config=scan_config
        )
        
        # Start scan in background thread
        def run_scan():
            try:
                scan_result.status = 'running'
                scan_result.save()
                
                if tool == 'zap':
                    results = start_scan(
                        target_url,
                        max_children=scan_config.get('max_children', 10),
                        scan_policy=scan_config.get('scan_policy', 'Default Policy')
                    )
                else:
                    # Placeholder for other tools
                    results = {"error": f"Tool {tool} not implemented yet"}
                
                scan_result.results = results
                scan_result.status = 'completed' if results.get('scan_completed') else 'failed'
                scan_result.completed_at = timezone.now()
                scan_result.save()
                
            except Exception as e:
                scan_result.status = 'failed'
                scan_result.results = {"error": str(e)}
                scan_result.completed_at = timezone.now()
                scan_result.save()
        
        # Start background thread
        thread = threading.Thread(target=run_scan)
        thread.daemon = True
        thread.start()
        
        return JsonResponse({
            "scan_id": scan_result.id,
            "status": "started",
            "message": "Scan started successfully"
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def get_scan_status(request, scan_id):
    """Get scan status and progress"""
    scan_result = get_object_or_404(ScanResult, id=scan_id, user=request.user)
    
    # Calculate progress based on status and time elapsed
    progress = 0
    phase = 'pending'
    
    if scan_result.status == 'pending':
        progress = 5
        phase = 'pending'
    elif scan_result.status == 'running':
        # Estimate progress based on time elapsed
        elapsed = timezone.now() - scan_result.created_at
        elapsed_minutes = elapsed.total_seconds() / 60
        
        if elapsed_minutes < 2:
            progress = 10 + min(20, elapsed_minutes * 10)  # 10-30% in first 2 minutes
            phase = 'spider'
        elif elapsed_minutes < 10:
            progress = 30 + min(50, (elapsed_minutes - 2) * 6.25)  # 30-80% in next 8 minutes
            phase = 'active'
        else:
            progress = 80 + min(15, (elapsed_minutes - 10) * 1.5)  # 80-95% after 10 minutes
            phase = 'report'
    elif scan_result.status == 'completed':
        progress = 100
        phase = 'completed'
    elif scan_result.status == 'failed':
        progress = 0
        phase = 'failed'
    
    return JsonResponse({
        "scan_id": scan_result.id,
        "status": scan_result.status,
        "progress": int(progress),
        "phase": phase,
        "target_url": scan_result.target_url,
        "tool": scan_result.tool,
        "created_at": scan_result.created_at.isoformat(),
        "updated_at": scan_result.updated_at.isoformat(),
        "completed_at": scan_result.completed_at.isoformat() if scan_result.completed_at else None,
        "duration": str(scan_result.duration) if scan_result.duration else None
    })

@login_required
def get_scan_results(request, scan_id):
    """Get scan results"""
    scan_result = get_object_or_404(ScanResult, id=scan_id, user=request.user)
    
    if scan_result.status != 'completed':
        return JsonResponse({"error": "Scan not completed yet"}, status=400)
    
    return JsonResponse({
        "scan_id": scan_result.id,
        "target_url": scan_result.target_url,
        "tool": scan_result.tool,
        "results": scan_result.results,
        "summary": scan_result.results.get('summary', {}) if scan_result.results else {}
    })

@login_required
def check_zap_status(request):
    """Check if ZAP is running and accessible"""
    try:
        scanner = ZAPScanner()
        is_running = scanner.check_zap_status()
        return JsonResponse({"zap_running": is_running})
    except Exception as e:
        return JsonResponse({"zap_running": False, "error": str(e)})

@login_required
def cancel_scan(request, scan_id):
    """Cancel a running scan"""
    scan_result = get_object_or_404(ScanResult, id=scan_id, user=request.user)
    
    if scan_result.status not in ['pending', 'running']:
        return JsonResponse({"error": "Scan cannot be cancelled"}, status=400)
    
    try:
        # Update scan status to cancelled
        scan_result.status = 'cancelled'
        scan_result.save()
        
        # TODO: Add actual ZAP scan cancellation here
        # For now, we just mark it as cancelled in the database
        
        return JsonResponse({
            "success": True,
            "message": "Scan cancelled successfully"
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
