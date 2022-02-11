import os
from unittest import TestCase, main



class _TestDistributionBalance(TestCase):
    """
    """
    def _test_distribution_of_10(self):
        os.environ['SANIC_CDN_HOST'] = 'cdn-domain'
        os.environ['SANIC_BALANCE_DISTRIBUTION'] = '10'
        from app import app as test_app
        
        test_client = test_app.test_client
        test_url = 'http://s1.origin-cluster/video/1488/xcg2djHckad.m3u8'

        cdn_redirects = 0
        orig_redirects = 0
        for _ in range(10):
            req, resp = test_client.get(
                '/', params={'video': test_url}, 
                allow_redirects=False,
            )
            if 'cdn-domain' in resp.headers['location']:
                cdn_redirects += 1
            elif 's1.origin-cluster' in resp.headers['location']:
                orig_redirects += 1
            else:
                self.fail()

        self.assertEqual(orig_redirects, 1)
        self.assertEqual(cdn_redirects, 9)


if __name__ == '__main__':
    main()
