import os
import re
import sys
from html.parser import HTMLParser

class SimpleHTMLParser(HTMLParser):
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
        self.tags_stack = []
        self.links = []
        self.ids = set()
        self.current_tag = None
        self.has_errors = False

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        self.tags_stack.append(tag)
        attrs_dict = dict(attrs)
        
        # Track ids for anchor resolution
        if 'id' in attrs_dict:
            self.ids.add(attrs_dict['id'])
            
        # Track links
        if tag == 'a' and 'href' in attrs_dict:
            self.links.append((attrs_dict['href'], self.getpos()))
        if tag == 'form' and 'action' in attrs_dict:
            self.links.append((attrs_dict['action'], self.getpos()))

    def handle_endtag(self, tag):
        if not self.tags_stack:
            print(f"Error in {self.filepath}: Unexpected end tag </{tag}> at line {self.getpos()[0]}")
            self.has_errors = True
            return
        
        last_tag = self.tags_stack.pop()
        if last_tag != tag:
            # Tolerant HTML parsing, but let's log mismatch warning
            pass

    def handle_data(self, data):
        # We can analyze data content here if needed
        pass

def verify_file(filepath):
    print(f"Verifying {filepath}...")
    if not os.path.exists(filepath):
        print(f"Error: File not found {filepath}")
        return None
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check for remaining "loan" references (case-insensitive) except where acceptable (like inside text discussing general history, though we removed it from about)
    # Let's search for "loan" in the content
    loan_matches = []
    for i, line in enumerate(content.splitlines(), 1):
        if re.search(r'\bloans?\b', line, re.IGNORECASE):
            # Exclude standard occurrences that are part of other words, or if it is inside comments.
            # But let's show all matches so we can verify manually.
            loan_matches.append((i, line.strip()))
            
    if loan_matches:
        print(f"  [WARNING] Found 'loan' references:")
        for line_no, text in loan_matches:
            print(f"    Line {line_no}: {text}")
            
    parser = SimpleHTMLParser(filepath)
    parser.feed(content)
    return parser

def main():
    html_files = ['index.html', 'disclosures.html', 'privacy.html', 'terms.html']
    parsers = {}
    
    # 1. Parse all HTML files
    for filename in html_files:
        parser = verify_file(filename)
        if parser:
            parsers[filename] = parser
            
    print("\nVerifying Cross-Page Links and Anchors...")
    all_ok = True
    
    # 2. Verify all links
    for filename, parser in parsers.items():
        for href, pos in parser.links:
            # Skip external links or mailto/tel/whatsapp
            if href.startswith(('http://', 'https://', 'mailto:', 'tel:', 'javascript:', 'wa.me')):
                continue
                
            # Internal link
            parts = href.split('#')
            target_file = parts[0]
            target_anchor = parts[1] if len(parts) > 1 else None
            
            # If href starts with '#', it refers to the current file
            if not target_file:
                target_file = filename
                
            if target_file not in parsers:
                print(f"  [ERROR] {filename}:{pos[0]} - Link to non-existent internal file '{target_file}'")
                all_ok = False
                continue
                
            if target_anchor:
                target_parser = parsers[target_file]
                if target_anchor not in target_parser.ids:
                    print(f"  [ERROR] {filename}:{pos[0]} - Link to non-existent anchor '#{target_anchor}' in '{target_file}'")
                    all_ok = False
                    
    # Check CSS reference
    if not os.path.exists('style.css'):
        print("  [ERROR] style.css file is missing!")
        all_ok = False
        
    if all_ok:
        print("\nAll internal links and anchors verified successfully!")
    else:
        print("\nErrors found in links or anchors. Please check warnings/errors above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
