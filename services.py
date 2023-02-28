import asyncio
import datetime
from utils import make_post_request
import aiohttp


async def send_message(myArticle, parent):
    url = 'https://a.wb.ru/e/Item_Offers_From_Other_Seller_Similar_Item?t=%D0%A1%D0%B2%D0%B0%D1%80%D0%BE%D1%87%D0%BD%D1%8B%D0%B9%20%D0%B0%D0%BF%D0%BF%D0%B0%D1%80%D0%B0%D1%82%20%D0%B8%D0%BD%D0%B2%D0%B5%D1%80%D1%82%D0%BE%D1%80%D0%BD%D1%8B%D0%B9%20%D0%A1%D0%90%D0%98160%D0%9A%20(%D0%BA%D0%BE%D0%BC%D0%BF%D0%B0%D0%BA%D1%82)%20%D0%A0%D0%B5%D1%81%D0%B0%D0%BD%D1%82%D0%B0%20%D0%A0%D0%B5%D1%81%D0%B0%D0%BD%D1%82%D0%B0%2049148156%20%D0%BA%D1%83%D0%BF%D0%B8%D1%82%D1%8C%20%D0%B7%D0%B0%205%C2%A0401%C2%A0%E2%82%BD%20%D0%B2%20%D0%B8%D0%BD%D1%82%D0%B5%D1%80%D0%BD%D0%B5%D1%82-%D0%BC%D0%B0%D0%B3%D0%B0%D0%B7%D0%B8%D0%BD%D0%B5%20Wildberries&u=https%3A%2F%2Fwww.wildberries.ru%2Fcatalog%2F49148156%2Fdetail.aspx%3FtargetUrl%3DSP&cid=4&s=1920x1080x24&w=694x714&user_id=7082625921677598339&vbn=324'
    link = f"https://www.wildberries.ru/catalog/{myArticle}/detail.aspx"
    payload = {
        'country': "ru",
        'item_id': '',
        'link': link,
        'parent_id': str(parent),
        'type':"fullsize"
    }
    headers = {

    }
    await make_post_request(url=url, headers=headers, payload=payload, no_json=True)


async def get_products(token_auth):
    data = []
    url = 'https://suppliers-api.wildberries.ru/content/v1/cards/cursor/list'
    payload = {
        "sort": {
            "cursor": {
                "limit": 1000
            },
            "filter": {
                "withPhoto": -1
            }
        }
    }
    total = 1
    while total != 0:
        async with aiohttp.ClientSession(trust_env=True, headers=token_auth) as session:
            async with session.post(url=url, json=payload) as response:
                partial_data = await response.json()
                data += partial_data['data']['cards']
                cursor = partial_data['data']['cursor']
                payload['sort']['cursor'].update(cursor)
                total = cursor['total']
    return data


async def check_by_vendors_and_send_messages(df, link_column, vendorCode_column, products):
    to_be_messaged = []

    for index in df.index:
        for product in products:
            if product.get('vendorCode').split('bland')[-1] in df[vendorCode_column][index]:
                link = str(df[link_column][index])
                another_article = link.split('/')[-2]
                to_be_messaged.append((link, another_article, datetime.datetime.now(), product.get('nmID')))
    tasks = []
    count = 0
    to_excel = []

    for item in to_be_messaged:
        link, another_article, time, myArticle = item
        task = asyncio.create_task(send_message(myArticle=myArticle, parent=another_article))
        tasks.append(task)
        count += 1

        to_excel.append({
            'Артикул ИП Бландова': myArticle,
            'время отправления': time,
            'товар, на котоый отправлено сообщение': link,
        })
        if count % 100 == 0:
            print(count)
            await asyncio.gather(*tasks, return_exceptions=True)
            tasks = []

    await asyncio.gather(*tasks, return_exceptions=True)

    return to_excel
