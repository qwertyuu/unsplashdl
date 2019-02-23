import json
import urllib.request
import urllib.parse
import sys
import os
from multiprocessing.pool import ThreadPool
from dotenv import load_dotenv
load_dotenv()


# Print iterations progress
def print_progress(iteration, total, prefix='Pages', suffix='', decimals=1, bar_length=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


num = 1


def fetch_image(args):
    name = args['name']
    url = args['url']
    folder = args['folder']
    global num
    if not name:
        name = str(num)
        num += 1
    urllib.request.urlretrieve(url, folder + '/' + name.replace(' ', '_') + '.jpg')


width = 1920
height = 1080
pages_to_download = 1
print(os.getenv('COMMIT_MESSAGE'))

query_params = {
    "query": 'code',
    "orientation": "landscape",
    "per_page": 30,
    "client_id": os.getenv('CLIENT_ID')
}

photo_params = {
    'w': width,
    'h': height,
    'auto': 'true',
    'crop': 'entropy',
    'fit': 'crop',
    'fm': 'jpg',
    'q': 100
}
photo_params = urllib.parse.urlencode(photo_params)

print_progress(0, pages_to_download)
if not os.path.exists('images'):
    os.mkdir('images')
if not os.path.exists('images/' + query_params['query']):
    os.mkdir('images/' + query_params['query'])
for page in range(1, pages_to_download):
    query_params['page'] = page
    html = urllib.request \
        .urlopen("https://api.unsplash.com/search/photos?" + urllib.parse.urlencode(query_params)) \
        .read() \
        .decode('utf-8')

    print_progress(page, pages_to_download)

    images = [{
        'url': result['urls']['raw'] + '&' + photo_params,
        'name': result['description']
    } for result in json.loads(html)['results'] if result['width'] >= width and result['height'] >= height]

    results = ThreadPool(8).imap_unordered(fetch_image, [{'url': image['url'], 'name': image['name'], 'folder': 'images/' + query_params['query']} for image in images])
print_progress(pages_to_download, pages_to_download)
