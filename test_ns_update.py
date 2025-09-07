#!/usr/bin/env python
"""
Test script for NS update functionality without buying new domains
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.brain.services import AdmToolsService

def test_ns_update():
    """Test NS update with existing domain"""
    adm_service = AdmToolsService()
    
    # Use existing domain from logs
    test_domain = "prime-stream-base.space"
    test_nameservers = ['leif.ns.cloudflare.com', 'maria.ns.cloudflare.com']
    
    print(f"🧪 Testing NS update for: {test_domain}")
    print(f"📡 Nameservers: {test_nameservers}")
    print("-" * 50)
    
    # Test domain_id retrieval
    print("1️⃣ Getting domain_id...")
    domain_id = adm_service.get_domain_id(test_domain)
    print(f"   Result: {domain_id}")
    print()
    
    if domain_id:
        # Test NS update
        print("2️⃣ Updating nameservers...")
        success = adm_service.update_nameservers(test_domain, test_nameservers)
        print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    else:
        print("❌ Cannot test NS update without domain_id")

if __name__ == "__main__":
    test_ns_update()