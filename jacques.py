#!/usr/bin/env python3
"""
Advanced Google Dorks Scanner - Professional Edition


python3 jacques.py -t https://example.com
"""

import requests
import time
import random
import argparse
import json
from urllib.parse import quote, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import sys

class AdvancedDorkScanner:
    def __init__(self, target, threads=5, delay=3, output_file=None):
        self.target = target
        self.threads = threads
        self.delay = delay
        self.output_file = output_file
        self.results = []
        self.session = requests.Session()
        
        # Advanced User-Agent rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15'
        ]
        
        # Comprehensive payload database
        self.payloads = {
            'SQL_INJECTION': [
                'inurl:id= & site:',
                'inurl:page.php?id=',
                'inurl:product.php?id=',
                'inurl:article.php?id=',
                'inurl:show.php?id=',
                'inurl:news.php?id=',
                'inurl:category.php?id=',
                'inurl:gallery.php?id=',
                'inurl:item.php?id=',
                'inurl:productid=',
                'inurl:catid=',
                'inurl:newsid=',
                'inurl:pid=',
                'inurl:cat=',
                'inurl:userid=',
                'inurl:user=',
                'inurl:keyword=',
                'inurl:search.php?q=',
            ],
            'ADMIN_PANELS': [
                'inurl:admin',
                'inurl:administrator',
                'inurl:admin/login',
                'inurl:admin/login.php',
                'inurl:admin/admin.php',
                'inurl:admin/index.php',
                'inurl:admin/dashboard',
                'inurl:adminpanel',
                'inurl:cpanel',
                'inurl:controlpanel',
                'inurl:webadmin',
                'inurl:wp-admin',
                'inurl:phpmyadmin',
                'inurl:moderator',
                'inurl:siteadmin',
                'intitle:"admin panel"',
                'intitle:"login panel"',
                'intitle:"admin login"',
                'intitle:"administrator login"',
                'inurl:admin.asp',
                'inurl:login.asp',
                'inurl:admin.aspx',
                'inurl:login.aspx',
            ],
            'SENSITIVE_FILES': [
                'ext:log',
                'ext:sql',
                'ext:env',
                'ext:bak',
                'ext:old',
                'ext:backup',
                'ext:swp',
                'ext:conf',
                'ext:config',
                'ext:ini',
                'ext:inc',
                'ext:txt "password"',
                'ext:xls "username"',
                'ext:xlsx "password"',
                'filetype:env "DB_PASSWORD"',
                'filetype:env "API_KEY"',
                'filetype:log "password"',
                'filetype:sql "INSERT INTO"',
                'filetype:bak "password"',
            ],
            'DIRECTORY_LISTING': [
                'intitle:"index of"',
                'intitle:"index of /" "parent directory"',
                'intitle:"index of" "backup"',
                'intitle:"index of" "database"',
                'intitle:"index of" "admin"',
                'intitle:"index of" "config"',
                'intitle:"index of" "uploads"',
                'intitle:"index of" "images"',
                'intitle:"index of" "logs"',
                'intitle:"index of" "sql"',
            ],
            'ERROR_MESSAGES': [
                '"Warning: mysql"',
                '"Warning: mysqli"',
                '"Fatal error:"',
                '"Parse error:"',
                '"unexpected T_STRING"',
                '"syntax error"',
                '"PHP Warning"',
                '"PHP Error"',
                '"MySQL Error"',
                '"Database Error"',
                '"ORA-" "error"',
                '"Microsoft OLE DB"',
                '"ODBC SQL Server"',
                '"PostgreSQL Error"',
            ],
            'LOGIN_PAGES': [
                'inurl:login',
                'inurl:signin',
                'inurl:sign-in',
                'inurl:auth',
                'inurl:authenticate',
                'intitle:"login"',
                'intitle:"sign in"',
                'intitle:"member login"',
                'intitle:"user login"',
                'inurl:user/login',
                'inurl:member/login',
                'inurl:account/login',
            ],
            'CONFIG_FILES': [
                'inurl:config.php',
                'inurl:configuration.php',
                'inurl:settings.php',
                'inurl:db.php',
                'inurl:database.php',
                'inurl:conn.php',
                'inurl:connect.php',
                'filetype:php "mysql_connect"',
                'filetype:inc "mysql_connect"',
            ],
            'UPLOAD_PAGES': [
                'inurl:upload',
                'inurl:file-upload',
                'inurl:fileupload',
                'inurl:uploader',
                'intitle:"file upload"',
                'inurl:uploadfile',
            ],
            'EMAIL_ADDRESSES': [
                'intext:"@" "contact"',
                'intext:"@" "email"',
                'intext:"@" "support"',
                'intext:"@" "admin"',
            ],
            'SUBDOMAINS': [
                'site:*.{domain}',
            ],
            'DOCUMENTS': [
                'filetype:pdf',
                'filetype:doc',
                'filetype:docx',
                'filetype:xls',
                'filetype:xlsx',
                'filetype:ppt',
                'filetype:pptx',
            ],
            'GIT_EXPOSURE': [
                'inurl:.git',
                'intitle:"Index of /.git"',
                'inurl:/.git/config',
                'filetype:git',
            ],
            'API_KEYS': [
                '"api_key"',
                '"apikey"',
                '"access_token"',
                '"secret_key"',
                '"private_key"',
                'filetype:env "API"',
                'filetype:json "apiKey"',
            ],
            'WORDPRESS': [
                'inurl:wp-admin',
                'inurl:wp-login',
                'inurl:wp-content',
                'inurl:wp-includes',
                'inurl:wp-config.php',
                'filetype:sql "wp_users"',
            ],
            'JOOMLA': [
                'inurl:com_',
                'inurl:administrator',
                'inurl:configuration.php',
            ],
            'APACHE_STRUTS': [
                'ext:action',
                'filetype:action',
            ]
        }

    def get_random_headers(self):
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def search_google(self, dork, num_results=10):
        """Search using Google Custom Search API or scraping"""
        results = []
        try:
            # Using DuckDuckGo as alternative (no API key needed)
            url = f"https://html.duckduckgo.com/html/?q={quote(dork)}"
            headers = self.get_random_headers()
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Basic parsing (you can improve this)
                links = response.text.split('href="')[1:]
                for link in links[:num_results]:
                    try:
                        clean_link = link.split('"')[0]
                        if self.target in clean_link and clean_link.startswith('http'):
                            results.append(clean_link)
                    except:
                        continue
            
            time.sleep(random.uniform(self.delay, self.delay + 2))
            
        except Exception as e:
            if 'verbose' in sys.argv:
                print(f"    [!] Error: {str(e)}")
        
        return results

    def test_dork(self, category, payload):
        """Test individual dork payload"""
        dork = f"site:{self.target} {payload}".replace('{domain}', self.target)
        
        print(f"[*] Testing: {category} - {payload[:50]}...")
        
        urls = self.search_google(dork, num_results=10)
        
        if urls:
            result = {
                'category': category,
                'dork': dork,
                'urls': urls,
                'timestamp': datetime.now().isoformat()
            }
            self.results.append(result)
            
            print(f"[+] FOUND {len(urls)} results for {category}")
            for url in urls:
                print(f"    └─> {url}")
            
            return result
        
        return None

    def scan(self):
        """Main scanning function"""
        print(f"""
╔══════════════════════════════════════════════════╗
║  Advanced Google Dorks Scanner v2.0              ║
║  Target: {self.target:38s} ║
╚══════════════════════════════════════════════════╝
        """)
        
        total_payloads = sum(len(p) for p in self.payloads.values())
        current = 0
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = []
            
            for category, payload_list in self.payloads.items():
                print(f"\n[>] Category: {category}")
                print(f"[>] Testing {len(payload_list)} payloads...\n")
                
                for payload in payload_list:
                    future = executor.submit(self.test_dork, category, payload)
                    futures.append(future)
                    current += 1
                
                # Process results as they complete
                for future in as_completed(futures):
                    try:
                        result = future.result()
                    except Exception as e:
                        if 'verbose' in sys.argv:
                            print(f"[!] Thread error: {e}")
                
                futures.clear()
                time.sleep(2)  # Delay between categories
        
        self.save_results()
        self.print_summary()

    def save_results(self):
        """Save results to file"""
        if self.output_file:
            with open(self.output_file, 'w') as f:
                json.dump(self.results, f, indent=4)
            print(f"\n[✓] Results saved to: {self.output_file}")

    def print_summary(self):
        """Print scan summary"""
        print(f"""
╔══════════════════════════════════════════════════╗
║                 SCAN SUMMARY                     ║
╚══════════════════════════════════════════════════╝

[+] Total Categories Scanned: {len(self.payloads)}
[+] Total Payloads Tested: {sum(len(p) for p in self.payloads.values())}
[+] Total Results Found: {len(self.results)}
[+] Unique URLs Found: {sum(len(r['urls']) for r in self.results)}

        """)
        
        if self.results:
            print("[!] FINDINGS BY CATEGORY:")
            for category in self.payloads.keys():
                cat_results = [r for r in self.results if r['category'] == category]
                if cat_results:
                    print(f"    [{category}]: {len(cat_results)} findings")


def main():
    parser = argparse.ArgumentParser(description='Advanced Google Dorks Scanner')
    parser.add_argument('-t', '--target', required=True, help='Target domain (e.g., example.com)')
    parser.add_argument('-o', '--output', help='Output JSON file')
    parser.add_argument('-th', '--threads', type=int, default=3, help='Number of threads (default: 3)')
    parser.add_argument('-d', '--delay', type=int, default=3, help='Delay between requests (default: 3)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    scanner = AdvancedDorkScanner(
        target=args.target,
        threads=args.threads,
        delay=args.delay,
        output_file=args.output
    )
    
    try:
        scanner.scan()
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user")
        scanner.save_results()
        sys.exit(0)


if __name__ == "__main__":
    main()
