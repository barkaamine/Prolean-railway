# context_processors.py
import requests
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from .models import CurrencyRate
import logging

logger = logging.getLogger(__name__)

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_location_from_ip(ip_address):
    """
    Get location from IP address with strict timeouts and error handling.
    Returns default location on ANY failure.
    NOTE: This function makes external network calls. 
    It should NOT be called directly in the request cycle without caching.
    """
    default_location = {'city': 'Casablanca', 'country': 'Maroc', 'countryCode': 'MA'}
    
    # Localhost check
    if ip_address in ['127.0.0.1', 'localhost', '::1']:
        return default_location
    
    # Try primary service
    try:
        response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=2) # Strict 2s timeout
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'city': data.get('city', 'Casablanca'),
                    'country': data.get('country', 'Maroc'),
                    'countryCode': data.get('countryCode', 'MA')
                }
    except Exception as e:
        logger.warning(f"IP-API lookup failed: {e}")
    
    # Try fallback service
    try:
        response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=2, verify=False) # Strict 2s timeout
        if response.status_code == 200:
            data = response.json()
            if not data.get('error'):
                return {
                    'city': data.get('city', 'Casablanca'),
                    'country': data.get('country_name', 'Maroc'),
                    'countryCode': data.get('country_code', 'MA')
                }
    except Exception as e:
        logger.warning(f"IPAPI.co lookup failed: {e}")
    
    return default_location

def currency_rates(request):
    """Add currency rates to context with caching"""
    # Try to get from cache first
    rates = cache.get('currency_rates')
    
    if not rates:
        rates = {}
        try:
            # Fetch from DB
            db_rates = CurrencyRate.objects.all()
            for rate in db_rates:
                rates[rate.currency_code] = float(rate.rate_to_mad)
            
            # If DB empty, use defaults
            if not rates:
                raise Exception("No rates in DB")
                
            # Cache for 1 hour (3600 seconds)
            cache.set('currency_rates', rates, 3600)
            
        except Exception as e:
            logger.error(f"Error fetching currency rates: {e}")
            # Fallback defaults
            rates = {
                'MAD': 1.0, 'EUR': 0.093, 'USD': 0.100,
                'GBP': 0.079, 'CAD': 0.136, 'AED': 0.367
            }
    
    preferred_currency = request.session.get('preferred_currency', 'MAD')
    
    return {
        'currency_rates': rates,
        'preferred_currency': preferred_currency,
    }

def user_location(request):
    """Add user location to context with session caching"""
    # Check session first
    if 'user_location' in request.session:
        return {'user_location': request.session['user_location']}
    
    # If not in session, detect once
    ip_address = get_client_ip(request)
    location = get_location_from_ip(ip_address)
    
    # Save to session to prevent future lookups
    request.session['user_location'] = location
    
    return {
        'user_location': location,
    }

def site_settings(request):
    """Add site settings to context"""
    return {
        'SITE_NAME': 'Prolean Centre',
        'SITE_URL': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
        'CONTACT_PHONE': '+212 779 25 99 42',
        'CONTACT_EMAIL': 'contact@proleancentre.ma',
        'CURRENT_YEAR': timezone.now().year,
    }

# Alias for backward compatibility
site_context = site_settings

def notifications(request):
    """Add user notifications to context"""
    if request.user.is_authenticated:
        try:
            # Optimized query - slicing to avoid fetching all
            unread_notifications = request.user.notifications.filter(is_read=False).order_by('-created_at')[:5]
            unread_count = request.user.notifications.filter(is_read=False).count()
            return {
                'global_notifications': unread_notifications,
                'unread_notifications_count': unread_count,
            }
        except Exception:
            pass
            
    return {
        'global_notifications': [],
        'unread_notifications_count': 0,
    }
