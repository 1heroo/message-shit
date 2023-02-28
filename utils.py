import aiohttp


async def make_post_request(url, payload, headers, no_json=False):
    async with aiohttp.ClientSession(trust_env=True, headers=headers) as session:
        async with session.post(url=url, json=payload) as response:
            if response.status == 200:
                return True if no_json else await response.json()


async def get_wh(toke_auth):
    url = 'https://suppliers-api.wildberries.ru/api/v2/warehouses'
    async with aiohttp.ClientSession(headers=toke_auth) as session:
        async with session.get(url=url) as response:
            return [item.get('id') for item in await response.json()]


async def get_stocks(wh, skus, token_auth):
    url = f'https://suppliers-api.wildberries.ru/api/v3/stocks/{wh}'
    stocks: list = []
    async with aiohttp.ClientSession(headers=token_auth) as session:
        times = len(skus) // 1000
        start = 0
        for i in range(times + 1):
            chunk_skus = skus[start: start + 1000] if i != times else skus[start: len(skus)]
            start += 1000
            async with session.post(url=url, json=dict(skus=chunk_skus)) as response:
                if response.status == 200:
                    data = await response.json()
                    stocks += data.get('stocks')
    return stocks


async def filter_by_stocks(token_auth, products):
    skus = [item['sizes'][0]['skus'][0] for item in products]
    whs = await get_wh(toke_auth=token_auth)
    stocks = []
    for wh in whs:
        stocks += await get_stocks(wh=wh, skus=skus, token_auth=token_auth)
    print(whs)
    output = []
    for product in products:
        for stock in stocks:
            if stock.get('sku') == product['sizes'][0]['skus'][0] and stock.get('amount') > 0:
                output.append(product)

    return output