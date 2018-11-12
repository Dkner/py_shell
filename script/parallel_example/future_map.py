import concurrent.futures
import requests
import time
URLS = ['http://httpbin.org', 'http://example.com/', 'https://api.github.com/']

def load_url(url, timeout=5):
	time.sleep(2)
	ret = requests.get(url)
	return ret.text

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
	future_to_url = {executor.submit(load_url, url, 60): url for url in URLS}
	for future in concurrent.futures.as_completed(future_to_url):
		url = future_to_url[future]
		try:
			data = future.result()
		except Exception as exc:
			print('%r generated an exception: %s' % (url, exc))
		else:
			print('%r page is %d bytes' % (url, len(data)))

print('------------------------------')

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
	for url, data in zip(URLS, executor.map(load_url, URLS)):
		print('%r page is %d bytes' % (url, len(data)))

