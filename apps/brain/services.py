import random
import requests
import time
from typing import List, Dict, Optional
from .models import Domain
from core.logger import Logger


class DomainNameGenerator:
    """Generates unique domain names using three word arrays"""
    
    WORD_ARRAY_1 = [
        "prime", "smart", "fast", "clear", "bright", "sharp", "pure", "fresh",
        "solid", "quick", "strong", "light", "clean", "modern", "sleek", "bold"
    ]
    
    WORD_ARRAY_2 = [
        "matrix", "point", "stream", "sync", "flow", "pulse", "wave", "path",
        "grid", "core", "link", "node", "bridge", "gate", "hub", "zone"
    ]
    
    WORD_ARRAY_3 = [
        "node", "box", "hub", "core", "lab", "space", "base", "port",
        "tech", "digital", "cloud", "web", "net", "pro", "plus", "max"
    ]
    
    @classmethod
    def generate_domain_name(cls, zone: str) -> str:
        """Generate a unique domain name with format word1-word2-word3.zone"""
        word1 = random.choice(cls.WORD_ARRAY_1)
        word2 = random.choice(cls.WORD_ARRAY_2)
        word3 = random.choice(cls.WORD_ARRAY_3)
        
        domain_name = f"{word1}-{word2}-{word3}{zone}"
        return domain_name
    
    @classmethod
    def generate_unique_domains(cls, zone: str, count: int) -> List[str]:
        """Generate specified number of unique domain names"""
        domains = []
        attempts = 0
        max_attempts = count * 50
        
        while len(domains) < count and attempts < max_attempts:
            domain = cls.generate_domain_name(zone)
            
            if domain not in domains and not Domain.objects.filter(name=domain).exists():
                domains.append(domain)
                Logger(f"Generated unique domain: {domain}", "info")
            
            attempts += 1
        
        if len(domains) < count:
            Logger(f"Could only generate {len(domains)} unique domains out of {count} requested", "error")
        
        return domains


class AdmToolsService:
    """Service for purchasing domains through adm.tools API"""
    
    def __init__(self):
        self.api_key = "dv69806dfwam2s6jbu06184fcn0iw16h99y1wxfg5ex1plfb9gt8q3wsake4b0e2"
        self.email = "mar.miroiu@gmail.com"
        self.base_url = "https://adm.tools"
    
    def purchase_domain(self, domain_name: str) -> Optional[str]:
        """Register domain and return invoice ID"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "domain": domain_name,
                "period": 1
            }
            
            response = requests.post(
                f"{self.base_url}/action/domain/register/",
                headers=headers,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                Logger(f"Domain registration response for {domain_name}: {result}", "info")
                
                # Try to get domain_id from registration response
                domain_info = result.get('response', {}).get('domain', {})
                invoice_id = result.get('response', {}).get('invoice', {}).get('id')
                
                if invoice_id:
                    Logger(f"Domain {domain_name} registered with invoice ID {invoice_id}", "info")
                    # Return both invoice_id and any domain info for later use
                    return {"invoice_id": str(invoice_id), "domain_info": domain_info}
                else:
                    Logger(f"Domain registration failed for {domain_name}: {result}", "error")
                    return None
            else:
                Logger(f"Failed to purchase domain {domain_name}: {response.text}", "error")
                return None
                
        except Exception as e:
            Logger(f"Error purchasing domain {domain_name}: {str(e)}", "error")
            return None
    
    
    def complete_order(self, order_id: str) -> bool:
        """Complete the order/purchase from cart"""
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "email": self.email,
                "token": self.api_key,
                "order_id": order_id
            }
            
            # Try different possible endpoints for order completion
            endpoints_to_try = [
                "/action/billing/order/complete",
                "/action/hosting/cart/order", 
                "/action/billing/cart/complete",
                "/action/order/complete"
            ]
            
            for endpoint in endpoints_to_try:
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                Logger(f"Trying endpoint {endpoint} for order {order_id}: {response.status_code}", "info")
                
                if response.status_code == 200:
                    result = response.json()
                    Logger(f"Response from {endpoint}: {result}", "info")
                    
                    if result.get('success') == True or result.get('result') == True:
                        Logger(f"Successfully completed order {order_id} via {endpoint}", "info")
                        return True
                    elif 'найден обработчик' not in str(result.get('messages', {})):
                        # API responded but order failed for other reason
                        break
            
            # If we get here, all endpoints failed
            response = requests.post(
                f"{self.base_url}/action/billing/cart/order",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                Logger(f"Order completion response for {order_id}: {result}", "info")
                
                if result.get('success') == True or result.get('result') == True:
                    Logger(f"Successfully completed order {order_id}", "info")
                    return True
                else:
                    Logger(f"Failed to complete order {order_id}: {result}", "error")
                    return False
            else:
                Logger(f"Failed to complete order {order_id}: {response.text}", "error")
                return False
                
        except Exception as e:
            Logger(f"Error completing order {order_id}: {str(e)}", "error")
            return False
    
    def pay_invoice(self, invoice_id: str) -> bool:
        """Pay invoice from balance"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "invoice_id": invoice_id
            }
            
            response = requests.post(
                f"{self.base_url}/action/billing/invoice_pay_from_balance/",
                headers=headers,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                Logger(f"Invoice payment response for {invoice_id}: {result}", "info")
                return True
            else:
                Logger(f"Failed to pay invoice {invoice_id}: {response.text}", "error")
                return False
                
        except Exception as e:
            Logger(f"Error paying invoice {invoice_id}: {str(e)}", "error")
            return False
    
    def get_domain_id(self, domain_name: str) -> Optional[str]:
        """Get domain ID for NS management using correct API endpoint"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "by": "desc",
                "domains_search_request": domain_name,
                "p": 1,
                "page": "",
                "sort": "valid_untill",
                "tag_free": "",
                "tag_id": "",
            }
            
            # Use correct endpoint from documentation
            response = requests.post(
                f"{self.base_url}/action/dns/list/",
                headers=headers,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                Logger(f"Domain list response: {result}", "info")
                
                if result.get('result') == True:
                    response_data = result.get('response', {})
                    
                    # API returns structure: response -> list -> domain_name -> domain_data
                    if 'list' in response_data and isinstance(response_data['list'], dict):
                        domain_list = response_data['list']
                        
                        # Check if our domain is in the list
                        if domain_name in domain_list:
                            domain_data = domain_list[domain_name]
                            domain_id = domain_data.get('domain_id')
                            if domain_id:
                                Logger(f"Found domain ID {domain_id} for {domain_name}", "info")
                                return str(domain_id)
                            else:
                                Logger(f"domain_id not found in domain data for {domain_name}", "error")
                                return None
                        else:
                            Logger(f"Domain {domain_name} not found in domain list keys: {list(domain_list.keys())}", "error")
                            return None
                    else:
                        Logger(f"Expected 'list' key in response, got: {list(response_data.keys())}", "error")
                        return None
                else:
                    Logger(f"Domain search API failed: {result}", "error")
                    return None
            else:
                Logger(f"Failed to get domain list: {response.text}", "error")
                return None
                
        except Exception as e:
            Logger(f"Error getting domain ID for {domain_name}: {str(e)}", "error")
            return None
    
    def update_nameservers(self, domain_name: str, nameservers: List[str]) -> bool:
        """Update domain nameservers using domain_id (matching PHP implementation)"""
        try:
            # First, get domain_id
            domain_id = self.get_domain_id(domain_name)
            if not domain_id:
                Logger(f"Could not get domain_id for {domain_name}, cannot update NS", "error")
                return False
            
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Match PHP implementation exactly
            data = {
                "domain_id": domain_id,
                "stack": nameservers,
                "skip": 0
            }
            
            Logger(f"NS update request - domain_id: {domain_id}, nameservers: {nameservers}, full data: {data}", "info")
            
            # For array parameters, PHP sends them as indexed arrays
            # Convert to form data that matches PHP http_build_query behavior
            import urllib.parse
            
            form_data = {
                'domain_id': int(domain_id),  # Ensure it's an integer like in PHP
                'skip': 0
            }
            
            # Add nameservers as indexed array like PHP
            for i, ns in enumerate(nameservers):
                form_data[f'stack[{i}]'] = ns
            
            Logger(f"Final form data: {form_data}", "info")
            
            response = requests.post(
                f"{self.base_url}/action/dns/change_nameservers/",
                headers=headers,
                data=form_data,
                timeout=30
            )
            
            result = response.json()
            Logger(f"NS update response for {domain_name} (domain_id: {domain_id}): {result}", "info")
            
            if response.status_code == 200 and result.get('result') == True:
                Logger(f"Successfully updated nameservers for {domain_name} using domain_id {domain_id}", "info")
                return True
            else:
                Logger(f"Failed to update nameservers for {domain_name}: {result}", "error")
                return False
                
        except Exception as e:
            Logger(f"Error updating nameservers for {domain_name}: {str(e)}", "error")
            return False
    
    def get_balance(self) -> Optional[float]:
        """Get account balance from adm.tools"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.get(
                f"{self.base_url}/action/billing/balance_get/",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result') == True:
                    balance_str = result.get('response', {}).get('balance', '0')
                    balance = float(balance_str)
                    Logger(f"Retrieved balance: {balance} UAH", "info")
                    return balance
                else:
                    Logger(f"Balance API failed: {result}", "error")
                    return None
            else:
                Logger(f"Failed to get balance: {response.text}", "error")
                return None
                
        except Exception as e:
            Logger(f"Error getting balance: {str(e)}", "error")
            return None


class CloudFlareService:
    """Service for managing CloudFlare DNS and zones"""
    
    ACCOUNTS = [
        {
            "email": "nexuspointmail@proton.me",
            "api_key": "8ff7fe1530a71ff600140dc1b60826358090b"
        },
        {
            "email": "cloudmessenger@proton.me", 
            "api_key": "406de8bda1d52ab87a723ea78246887515b35"
        },
        {
            "email": "datastreambox@proton.me",
            "api_key": "b456e8d065919e6fc43682ad6c5b103461df2"
        },
        {
            "email": "syncpointmail@proton.me",
            "api_key": "da3e82748f101e0c41c35c6c97343d65bfe5a"
        },
        {
            "email": "clearpathmail@proton.me",
            "api_key": "e7c72a47bddd9a910323d4b643ce111562642"
        }
    ]
    
    def __init__(self):
        self.account = random.choice(self.ACCOUNTS)
        self.base_url = "https://api.cloudflare.com/client/v4"
        Logger(f"Selected CloudFlare account: {self.account['email']}", "info")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for CloudFlare API requests"""
        return {
            "X-Auth-Email": self.account["email"],
            "X-Auth-Key": self.account["api_key"],
            "Content-Type": "application/json"
        }
    
    def create_zone(self, domain_name: str) -> Optional[str]:
        """Create a new zone in CloudFlare and return zone ID"""
        try:
            headers = self._get_headers()
            data = {"name": domain_name}
            
            response = requests.post(
                f"{self.base_url}/zones",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    zone_id = result["result"]["id"]
                    Logger(f"Successfully created CloudFlare zone for {domain_name} with ID {zone_id}", "info")
                    return zone_id
                else:
                    Logger(f"CloudFlare API error creating zone for {domain_name}: {result.get('errors')}", "error")
                    return None
            else:
                Logger(f"Failed to create CloudFlare zone for {domain_name}: {response.text}", "error")
                return None
                
        except Exception as e:
            Logger(f"Error creating CloudFlare zone for {domain_name}: {str(e)}", "error")
            return None
    
    def delete_all_dns_records(self, zone_id: str) -> bool:
        """Delete all DNS records in a zone"""
        try:
            headers = self._get_headers()
            
            response = requests.get(
                f"{self.base_url}/zones/{zone_id}/dns_records",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    records = result["result"]
                    
                    for record in records:
                        if record["type"] not in ["NS", "SOA"]:
                            delete_response = requests.delete(
                                f"{self.base_url}/zones/{zone_id}/dns_records/{record['id']}",
                                headers=headers,
                                timeout=30
                            )
                            
                            if delete_response.status_code == 200:
                                Logger(f"Deleted DNS record {record['name']} ({record['type']})", "info")
                            else:
                                Logger(f"Failed to delete DNS record {record['id']}", "error")
                    
                    return True
                else:
                    Logger(f"CloudFlare API error getting DNS records: {result.get('errors')}", "error")
                    return False
            else:
                Logger(f"Failed to get DNS records for zone {zone_id}: {response.text}", "error")
                return False
                
        except Exception as e:
            Logger(f"Error deleting DNS records for zone {zone_id}: {str(e)}", "error")
            return False
    
    def create_dns_record(self, zone_id: str, domain_name: str) -> bool:
        """Create A record with specified parameters"""
        try:
            headers = self._get_headers()
            
            data = {
                "type": "A",
                "name": domain_name,
                "content": "209.38.103.156",
                "proxied": True,
                "ttl": 1
            }
            
            response = requests.post(
                f"{self.base_url}/zones/{zone_id}/dns_records",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    Logger(f"Successfully created A record for {domain_name}", "info")
                    return True
                else:
                    Logger(f"CloudFlare API error creating DNS record: {result.get('errors')}", "error")
                    return False
            else:
                Logger(f"Failed to create DNS record for {domain_name}: {response.text}", "error")
                return False
                
        except Exception as e:
            Logger(f"Error creating DNS record for {domain_name}: {str(e)}", "error")
            return False
    
    def get_nameservers(self, zone_id: str) -> Optional[List[str]]:
        """Get nameservers for a zone"""
        try:
            headers = self._get_headers()
            
            response = requests.get(
                f"{self.base_url}/zones/{zone_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    nameservers = result["result"]["name_servers"]
                    Logger(f"Retrieved nameservers for zone {zone_id}: {nameservers}", "info")
                    return nameservers
                else:
                    Logger(f"CloudFlare API error getting nameservers: {result.get('errors')}", "error")
                    return None
            else:
                Logger(f"Failed to get nameservers for zone {zone_id}: {response.text}", "error")
                return None
                
        except Exception as e:
            Logger(f"Error getting nameservers for zone {zone_id}: {str(e)}", "error")
            return None


class KeitaroService:
    """Service for managing domains in Keitaro"""
    
    def __init__(self):
        self.api_key = "b0035ee109b826691adfb13f677b4457"
        self.base_url = "https://keitaro.make-admin.com/admin_api/v1"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Keitaro API requests"""
        return {
            "Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def add_domain(self, domain_name: str, cloudflare_email: str) -> bool:
        """Add domain to Keitaro with specified settings"""
        try:
            headers = self._get_headers()
            
            notes = f"UkrHost|{cloudflare_email}|APP"
            
            # Use parameters that work with API
            data = {
                "name": domain_name,
                "notes": notes,
                "group_id": 100,  # "⬛️ APP | ALL" group
                "ssl_redirect": True  # Enable HTTPS-only
            }
            
            response = requests.post(
                f"{self.base_url}/domains",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                Logger(f"Successfully added domain {domain_name} to Keitaro with notes: {notes}", "info")
                return True
            else:
                Logger(f"Failed to add domain {domain_name} to Keitaro: {response.text}", "error")
                return False
                
        except Exception as e:
            Logger(f"Error adding domain {domain_name} to Keitaro: {str(e)}", "error")
            return False


class TelegramService:
    """Service for sending notifications to Telegram channel"""
    
    def __init__(self):
        self.bot_token = "6824654226:AAHOmIA46ViCEJ2cfkGHnDVcmRgVcKz4wLM"
        self.chat_id = "-4108642937"
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Send message to Telegram channel"""
        try:
            data = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    Logger(f"Successfully sent Telegram message", "info")
                    return True
                else:
                    Logger(f"Telegram API error: {result.get('description')}", "error")
                    return False
            else:
                Logger(f"Failed to send Telegram message: {response.text}", "error")
                return False
                
        except Exception as e:
            Logger(f"Error sending Telegram message: {str(e)}", "error")
            return False
    
    def notify_domain_generation(self, domains: List[str], success: bool) -> None:
        """Notify about domain generation step"""
        if success:
            domains_list = "\n".join([f"• {domain}" for domain in domains])
            message = f"🎯 <b>Генерація доменів - успішно</b>\n\n{domains_list}"
        else:
            message = "❌ <b>Генерація доменів - помилка</b>"
        
        self.send_message(message)
    
    def notify_cloudflare_zone(self, domain: str, success: bool, error: str = "") -> None:
        """Notify about CloudFlare zone creation"""
        if success:
            message = f"☁️ <b>Створення зони в CloudFlare - успішно</b>\n<code>{domain}</code>"
        else:
            message = f"❌ <b>Створення зони в CloudFlare - помилка</b>\n<code>{domain}</code>\n{error}"
        
        self.send_message(message)
    
    def notify_dns_setup(self, domain: str, success: bool, error: str = "") -> None:
        """Notify about DNS setup"""
        if success:
            message = f"🔧 <b>Налаштування DNS - успішно</b>\n<code>{domain}</code>"
        else:
            message = f"❌ <b>Налаштування DNS - помилка</b>\n<code>{domain}</code>\n{error}"
        
        self.send_message(message)
    
    def notify_domain_purchase(self, domain: str, success: bool, error: str = "") -> None:
        """Notify about domain purchase"""
        if success:
            message = f"💰 <b>Купівля домену - успішно</b>\n<code>{domain}</code>"
        else:
            message = f"❌ <b>Купівля домену - помилка</b>\n<code>{domain}</code>\n{error}"
        
        self.send_message(message)
    
    def notify_nameserver_update(self, domain: str, success: bool, error: str = "") -> None:
        """Notify about nameserver update"""
        if success:
            message = f"🌐 <b>Оновлення NS - успішно</b>\n<code>{domain}</code>"
        else:
            message = f"❌ <b>Оновлення NS - помилка</b>\n<code>{domain}</code>\n{error}"
        
        self.send_message(message)
    
    def notify_keitaro_addition(self, domain: str, success: bool, error: str = "") -> None:
        """Notify about Keitaro domain addition"""
        if success:
            message = f"📊 <b>Додавання в Keitaro - успішно</b>\n<code>{domain}</code>"
        else:
            message = f"❌ <b>Додавання в Keitaro - помилка</b>\n<code>{domain}</code>\n{error}"
        
        self.send_message(message)
    
    def notify_batch_completion(self, successful_count: int, failed_count: int, successful_domains: List[str]) -> None:
        """Notify about batch completion"""
        if failed_count == 0:
            domains_list = "\n".join([f"• {domain}" for domain in successful_domains])
            message = f"✅ <b>Всі домени успішно створені!</b>\n\nВсього: {successful_count}\n\n{domains_list}"
        else:
            message = f"⚠️ <b>Завершення обробки доменів</b>\n\nУспішно: {successful_count}\nПомилки: {failed_count}"
        
        self.send_message(message)


class DomainPurchaseService:
    """Main service for orchestrating domain purchase process"""
    
    def __init__(self):
        self.adm_tools = AdmToolsService()
        self.telegram = TelegramService()
    
    def purchase_domains(self, count: int, zone: str) -> List[Dict]:
        """Purchase specified number of domains"""
        results = []
        
        domains = DomainNameGenerator.generate_unique_domains(zone, count)
        
        if domains:
            self.telegram.notify_domain_generation(domains, True)
        else:
            self.telegram.notify_domain_generation([], False)
            return results
        
        for domain_name in domains:
            result = self._purchase_single_domain(domain_name, zone)
            results.append(result)
        
        successful_domains = [r["domain"] for r in results if r["success"]]
        failed_count = len([r for r in results if not r["success"]])
        
        self.telegram.notify_batch_completion(len(successful_domains), failed_count, successful_domains)
        
        return results
    
    def purchase_custom_domains(self, domain_names: List[str], zone: str) -> List[Dict]:
        """Purchase domains with custom names"""
        results = []
        
        # Create full domain names by combining names with zone
        full_domains = [f"{name}{zone}" for name in domain_names]
        
        Logger(f"Starting custom domain purchase: {full_domains}", "info")
        self.telegram.notify_domain_generation(full_domains, True)
        
        # Check if domains are already taken in our database
        available_domains = []
        for full_domain in full_domains:
            if Domain.objects.filter(name=full_domain).exists():
                Logger(f"Domain {full_domain} already exists in database", "error")
                results.append({
                    "domain": full_domain,
                    "success": False,
                    "error": "Domain already exists in database"
                })
            else:
                available_domains.append(full_domain)
        
        # Purchase available domains
        for domain_name in available_domains:
            result = self._purchase_single_domain(domain_name, zone)
            results.append(result)
        
        successful_domains = [r["domain"] for r in results if r["success"]]
        failed_count = len([r for r in results if not r["success"]])
        
        self.telegram.notify_batch_completion(len(successful_domains), failed_count, successful_domains)
        
        return results
    
    def purchase_domains_with_retry(self, count: int, zone: str) -> List[Dict]:
        """Purchase domains with NS retry logic (background processing)"""
        domains = DomainNameGenerator.generate_unique_domains(zone, count)
        
        if not domains:
            self.telegram.notify_domain_generation([], False)
            return []
        
        self.telegram.notify_domain_generation(domains, True)
        
        # Phase 1: Quick purchase of all domains
        pending_domains = []
        for domain_name in domains:
            result = self._quick_purchase_domain(domain_name, zone)
            if result.get('success'):
                pending_domains.append(result)
        
        # Phase 2: NS retry logic for all purchased domains
        completed_domains = []
        for domain_data in pending_domains:
            final_result = self._complete_domain_setup(domain_data)
            completed_domains.append(final_result)
        
        successful_domains = [d["domain"] for d in completed_domains if d["success"]]
        failed_count = len([d for d in completed_domains if not d["success"]])
        
        self.telegram.notify_batch_completion(len(successful_domains), failed_count, successful_domains)
        
        return completed_domains
    
    def _purchase_single_domain(self, domain_name: str, zone: str) -> Dict:
        """Purchase and configure a single domain"""
        Logger(f"Starting purchase process for domain: {domain_name}", "info")
        
        cf_service = CloudFlareService()
        
        try:
            zone_id = cf_service.create_zone(domain_name)
            if not zone_id:
                error_msg = "Failed to create CloudFlare zone"
                self.telegram.notify_cloudflare_zone(domain_name, False, error_msg)
                return {"domain": domain_name, "success": False, "error": error_msg}
            
            self.telegram.notify_cloudflare_zone(domain_name, True)
            
            if not cf_service.delete_all_dns_records(zone_id):
                error_msg = "Failed to delete existing DNS records"
                self.telegram.notify_dns_setup(domain_name, False, error_msg)
                return {"domain": domain_name, "success": False, "error": error_msg}
            
            if not cf_service.create_dns_record(zone_id, domain_name):
                error_msg = "Failed to create DNS record"
                self.telegram.notify_dns_setup(domain_name, False, error_msg)
                return {"domain": domain_name, "success": False, "error": error_msg}
            
            self.telegram.notify_dns_setup(domain_name, True)
            
            nameservers = cf_service.get_nameservers(zone_id)
            if not nameservers:
                error_msg = "Failed to get nameservers"
                return {"domain": domain_name, "success": False, "error": error_msg}
            
            domain_result = self.adm_tools.purchase_domain(domain_name)
            if not domain_result:
                error_msg = "Failed to register domain"
                self.telegram.notify_domain_purchase(domain_name, False, error_msg)
                return {"domain": domain_name, "success": False, "error": error_msg}
            
            invoice_id = domain_result["invoice_id"]
            
            # Pay the invoice
            if not self.adm_tools.pay_invoice(invoice_id):
                error_msg = "Failed to pay invoice"
                self.telegram.notify_domain_purchase(domain_name, False, error_msg)
                return {"domain": domain_name, "success": False, "error": error_msg}
            
            self.telegram.notify_domain_purchase(domain_name, True)
            
            # Retry NS update with 5 attempts
            max_attempts = 5
            for attempt in range(1, max_attempts + 1):
                Logger(f"Checking domain status and NS update attempt {attempt}/{max_attempts} for {domain_name}", "info")
                
                if attempt == 1:
                    time.sleep(300)  # Wait 5 minutes after first attempt
                else:
                    time.sleep(120)  # Wait 2 minutes between subsequent attempts
                
                # Try to update nameservers directly
                if self.adm_tools.update_nameservers(domain_name, nameservers):
                    break
                else:
                    Logger(f"NS update failed for {domain_name}, attempt {attempt}/{max_attempts}", "info")
                    
                if attempt == max_attempts:
                    error_msg = f"Domain not accessible or NS update failed after {max_attempts} attempts (15 minutes)"
                    self.telegram.notify_nameserver_update(domain_name, False, error_msg)
                    return {"domain": domain_name, "success": False, "error": error_msg}
            
            self.telegram.notify_nameserver_update(domain_name, True)
            
            keitaro_service = KeitaroService()
            keitaro_success = keitaro_service.add_domain(domain_name, cf_service.account["email"])
            
            if keitaro_success:
                self.telegram.notify_keitaro_addition(domain_name, True)
            else:
                self.telegram.notify_keitaro_addition(domain_name, False, "Failed to add to Keitaro")
            
            domain_obj = Domain.objects.create(
                name=domain_name,
                zone=zone,
                cloudflare_account_email=cf_service.account["email"],
                cloudflare_zone_id=zone_id,
                registrar_domain_id=invoice_id,
                keitaro_added=keitaro_success,
                status='completed'
            )
            
            Logger(f"Successfully completed domain purchase: {domain_name}", "info")
            return {
                "domain": domain_name,
                "success": True,
                "domain_id": domain_obj.id,
                "cloudflare_account": cf_service.account["email"]
            }
            
        except Exception as e:
            error_msg = str(e)
            Logger(f"Unexpected error during domain purchase {domain_name}: {error_msg}", "error")
            self.telegram.send_message(f"❌ <b>Критична помилка</b>\n<code>{domain_name}</code>\n{error_msg}")
            return {"domain": domain_name, "success": False, "error": error_msg}