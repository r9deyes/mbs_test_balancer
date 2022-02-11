from urllib.parse import urlparse
import pytest


@pytest.fixture
def default_app():
    from app import app as test_app
    
    test_app.config.CDN_HOST = 'cdn-domain'
    test_app.config.BALANCE_DISTRIBUTION = 10

    return test_app


def test_redirection_serv_name(default_app):
    """
    Проверка редиректа с учетом указанного имени 
    сервера в кластере
    """
    test_client = default_app.test_client
    test_url1 = 'http://s1.origin-cluster/video/1488/xcg2djHckad.m3u8'
    req, resp = test_client.get(
        '/', params={'video': test_url1}, 
        allow_redirects=False,
    )
    location = resp.headers['location']
    if 'cdn-domain' in location:
        assert urlparse(location).path.startswith('/s1')
    elif 'origin-cluster' in location:
        assert urlparse(location).netloc.startswith('s1.')
    else:
        pytest.fail(f'Wrong redirection: {location}')

    test_url2 = 'http://s2.origin-cluster/video/1337/832h8r3294c.m3u8'
    req, resp = test_client.get(
        '/', params={'video': test_url2}, 
        allow_redirects=False,
    )
    location = resp.headers['location']
    if 'cdn-domain' in location:
        assert urlparse(location).path.startswith('/s2')
    elif 'origin-cluster' in location:
        assert urlparse(location).netloc.startswith('s2.')
    else:
        pytest.fail(f'Wrong redirection: {location}')


def test_distribution_of_10_sync_client(default_app):
    """
    Синхронный тест для проверки распределения запросов 
    по CDN и серверу оригиналов (1 к 10)
    """
    test_client = default_app.test_client
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
            pytest.fail(f'Wrong redirection: {resp.headers["location"]}')

    assert orig_redirects == 1
    assert cdn_redirects == 9


@pytest.mark.asyncio
async def test_distribuition_asgi_client(default_app):
    """
    Асинхронный тест для проверки распределения запросов
    по CDN и серверу оригиналов (1 к 10)
    """
    test_client = default_app.asgi_client
    test_url = 'http://s1.origin-cluster/video/1488/xcg2djHckad.m3u8'

    cdn_redirects = 0
    orig_redirects = 0
    for _ in range(10):
        req, resp = await test_client.get(
            '/', params={'video': test_url}, 
            # allow_redirects=False,
        )
        if 'cdn-domain' in resp.headers['location']:
            cdn_redirects += 1
        elif 's1.origin-cluster' in resp.headers['location']:
            orig_redirects += 1
        else:
            pytest.fail(f'Wrong redirection: {resp.headers["location"]}')

    assert orig_redirects == 1
    assert cdn_redirects == 9
