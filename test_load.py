import sys
import aiohttp
import asyncio


async def load1(s_='s1', req_count=100):
    async with aiohttp.ClientSession(requote_redirect_url=False) as session:
        cdn_redirects = 0
        orig_redirects = 0
        for i in range(req_count):
            async with session.get(
                f'http://0.0.0.0:8000/?video=http://{s_}.origin-cluster/video/1488/xcg2djHckad.m3u8',
                allow_redirects=False,
            ) as resp:
                if 'origin-cluster' in resp.headers['location']:
                    orig_redirects += 1
                elif 'cdn-domain' in resp.headers['location']:
                    cdn_redirects += 1
        print(f'orig: {orig_redirects}, cdn: {cdn_redirects}')


async def main(req_count):
    await load1('s1', req_count)
    await load1('s2', req_count)
    await load1('s3', req_count)
    await load1('s1', req_count)
    await load1('s2', req_count)
    await load1('s3', req_count)



if __name__=='__main__':
    try:
        req_count = int(sys.argv[-1])
    except Exception:
        req_count = 100

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(req_count))
