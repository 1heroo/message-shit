import io

from fastapi import FastAPI, File
import pandas as pd
import uvicorn
from decouple import config
from starlette.responses import StreamingResponse

from services import get_products, check_by_vendors_and_send_messages, send_message
from utils import filter_by_stocks

app = FastAPI()


@app.post("/asd")
async def root(file: bytes = File()):
    auth = {'Authorization': config('WB_TOKEN')}
    brands = ['Ресанта', 'Huter', 'Вихрь']
    products = await get_products(token_auth=auth)
    filtered_products = [product for product in products if product.get('brand') in brands]
    filtered_products = await filter_by_stocks(products=filtered_products, token_auth=auth)

    df = pd.read_excel(file)
    vendorCode_column = df['Вендор код'].name
    link_column = df['Ссылка'].name

    result = await check_by_vendors_and_send_messages(df=df, vendorCode_column=vendorCode_column, link_column=link_column, products=filtered_products)
    df = pd.DataFrame(result)
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    writer.save()

    return StreamingResponse(io.BytesIO(output.getvalue()),
                             media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                             headers={'Content-Disposition': f'attachment; filename="message-report.xlsx"'})


if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        host='0.0.0.0',
        port=8000,
        reload=True
)
