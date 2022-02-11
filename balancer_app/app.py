from itertools import cycle
from urllib.parse import ParseResult, urlparse, urlunparse

from sanic import Sanic
from sanic.response import redirect, html


app = Sanic('balancer_app')


if not hasattr(app.config, 'BALANCE_DISTRIBUTION'):
    app.config.BALANCE_DISTRIBUTION = 10


# Глобальный объект циклического счетчика 
# для подсчета обращений к перенаправлениям
app.ctx._request_cycle = cycle(range(
    1,
    app.config.BALANCE_DISTRIBUTION + 1,
))


def is_redirecting_to_origin():
    """
    Проверка одного из 10 запросов для перенаправления на оригинал
    Если ложно, то запрос будет перенапрален на CDN
    """
    return next(app.ctx._request_cycle) == app.config.BALANCE_DISTRIBUTION


def parse_video_url(video_url: str) -> ParseResult:
    try:
        url_obj = urlparse(video_url)
    except Exception:
        raise ValueError('URL in video args is not valid', video_url)

    return url_obj


def get_balanced_url(url_obj: ParseResult, is_origin: bool=False) -> str:
    """
    Логика для получения URL редиректа. 
    Если is_origin=True - возвращается переданный адрес, 
    иначе, подготовливается URL с хостом CDN и названием 
    сервера оригинала в кластере
    """
    if is_origin:
        result = urlunparse(url_obj)
    else:
        serv_index = ''
        domain_split = url_obj.netloc.split('.', maxsplit=1)
        if len(domain_split) > 1:
            serv_index = f'/{domain_split[0]}'

        result = urlunparse(url_obj._replace(
            netloc=app.config.CDN_HOST,
            path=f'{serv_index}{url_obj.path}',
        ))

    return result


@app.route('/')
async def cycle_balance(request):
    """
    Перенаправляем каждый 10й запрос контента на сервер 
    оригиналов, остальные на CDN
    """
    video_url = request.args.get('video')

    if video_url:
        url_obj = parse_video_url(video_url)

        result = redirect(
            to=get_balanced_url(
                url_obj=url_obj,
                is_origin=is_redirecting_to_origin(),
            ),
            status=301,
        )
    else:
        demo_url = f'/?video=http://s1.origin-cluster/video/1488/xcg2djHckad.m3u8'  # noqa
        result = html(f'<a target="_blank" href="{demo_url}">{demo_url}</a>"')

    return result


if __name__=='__main__':
    app.run(host='0.0.0.0', port=8000, workers=4)
