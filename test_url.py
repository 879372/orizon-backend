from urllib.parse import urlparse, unquote

def extract_key(url):
    if not url or not url.startswith('http'):
        return url
    
    parsed = urlparse(url)
    path = unquote(parsed.path)
    if path.startswith('/'):
        path = path[1:]
    
    # We might have bucket name in the path if path-style
    bucket_name = 'categorized-tin-wxoe0puvx'
    if path.startswith(f"{bucket_name}/"):
        path = path[len(bucket_name)+1:]
        
    return path

url1 = "https://categorized-tin-wxoe0puvx.s3.amazonaws.com/material_receipts/MACIEL%20LOJA%203%20-%20NFCe%2041105.pdf?X-Amz-Expires=3600"
url2 = "https://s3.amazonaws.com/categorized-tin-wxoe0puvx/material_receipts/test.pdf?X-Amz-Expires=3600"

print(extract_key(url1))
print(extract_key(url2))
