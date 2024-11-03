from django.core.management import BaseCommand
from dashboard.utils.dbupdater import DBUpdater

class Command(BaseCommand):
    help = 'Ticker 모델 업데이트 하는 명령'
 
    def handle(self, *args, **options):
        
        DBUpdater.update_ticker()
        
        # datas = asyncio.run(GetData.get_code_info_df_async())
        # print('데이터 다운로드 완료!')
        # print('db update 중.')
        # datas = datas.to_dict('records')
        
        # new_codes = [data['code'] for data in datas]
        # existing_tickers = Ticker.objects.filter(code__in=new_codes)
        # existing_codes = set(existing_tickers.values_list('code', flat=True))
        
        # ## 업데이트할것과 새로 생성하는것을 분리
        # to_update = []
        # to_create = []
        
        # for data in datas:
        #     if data['code'] in existing_codes:
        #         # 존재하면
        #         ticker = existing_tickers.get(code=data['code'])
        #         if ticker.name != data['name'] or ticker.구분 != data['gb']:
        #             ticker.name = data['name']
        #             ticker.구분 = data['gb']
        #             to_update.append(ticker)
        #     else:
        #         # 존재하지 않으면 
        #         to_create.append(Ticker(code=data['code'], name=data['name'], 구분=data['gb']))
        
        # if to_update:
        #     Ticker.objects.bulk_update(to_update, ['name','구분'])
        #     print(f"updated 완료 {len(to_update)} ")
        #     print(to_update)
        
        # if to_create:
        #     Ticker.objects.bulk_create(to_create)
        #     print(f"created 완료 {len(to_create)} ")
        #     print(to_create)
            
        
        # print(f'updated : {len(to_update)} created : {len(to_create)}')
        
       
        