import sys
import requests
import numpy as np
from math import ceil
from scipy.misc import toimage  

IMG_DIM = 128 
NUM_RAND_INTS = IMG_DIM * IMG_DIM * 3  # {r,g,b} for each pixel in 128x128 bitmap 

BASE_URL = 'https://www.random.org/' 

def _compute_rand_ints():
    '''Use this when random.org's quota is hit or for testing.''' 
    v = np.random.random(NUM_RAND_INTS)
    map_to_range = lambda f: ceil(f*256)-1
    vfunc = np.vectorize(map_to_range) 
    mapped_v = vfunc(v)
    return np.reshape(mapped_v, (IMG_DIM,IMG_DIM,3)) 

def _fetch_rand_ints():
    '''Use this to get "true" random integers from www.random.org's API.
    This will quickly exhaust the quota so use with care.'''
    v = np.zeros(NUM_RAND_INTS)
    idx = 0

    num_left = NUM_RAND_INTS
    while num_left > 0:  # max allowed number of integers requestable in one request is 10000
        num_req = num_left if num_left < 10000 else 10000 
        params = {
            'num': num_req,
            'min': 0,
            'max': 255,
            'col': 1,
            'base': 10,
            'format': 'plain',
            'rnd': 'new'
        } 
        try:
            res = requests.get(BASE_URL + 'integers/', params=params)
            res.raise_for_status()
        except Exception as e:
            print(e)
            sys.exit(1)
        for num in res.text.strip().split('\n'):
            v[idx] = int(num)
            idx += 1 
        num_left -= num_req
    return np.reshape(v, (IMG_DIM,IMG_DIM,3)) 

def get_rand_ints(testing=False):
    '''Returns a 128x128x3 3D array of random integers between 0 and 255, inclusive.'''
    return _fetch_rand_ints() if not testing else _compute_rand_ints() 

def get_quota():
    '''Returns the integer quota (in bits) for www.random.org.''' 
    try:
        res = requests.get(BASE_URL + 'quota/', params={'format': 'plain'})
        res.raise_for_status()
    except Exception as e:
        print(e)
        sys.exit(1)
    return int(res.text.strip())

if __name__ == '__main__':
    quota = get_quota()
    while True:
        reply = input('Your quota is at {} bits. Do you still want to use www.random.org? [y/n] '.format(quota))
        if reply in {'y', 'n'}:
            break
        print('Not valid. Try again!')

    rand = get_rand_ints(testing=(reply == 'n')) 
    img = toimage(rand)
    img.save('rand.png', 'PNG')

