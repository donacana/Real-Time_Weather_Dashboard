import argparse,json,os,time
from datetime import date,timedelta
from sqlalchemy import select,func
from .settings import env
from .db import init_db, Session, CollectionRun,RawResponse,CongestionSnapshot,FlightRecord
from .sources import load_sources
from .storage import collect_one

def main():
    p=argparse.ArgumentParser(description='ICN API 수집 테스트 CLI')
    p.add_argument('command',choices=['list','init-db','test','test-all','backfill-flights','run','status'])
    p.add_argument('--source',help='API ID')
    p.add_argument('--date',help='YYYY-MM-DD')
    p.add_argument('--mode',choices=['mock','live'],default=None)
    p.add_argument('--confirm-live-schedule',action='store_true')
    args=p.parse_args();sources=load_sources();mode=args.mode or env('RUN_MODE','mock')
    if args.command=='list':
        for s in sources.values():print(s['id'],s['kind'],'enabled='+str(s['enabled']),'every='+str(s['interval_minutes'])+'m')
        return
    init_db()
    if args.command=='init-db':print('DB 테이블 생성 완료');return
    if args.command in ('test','test-all'):
        if args.command=='test' and args.source not in sources:p.error('--source 에 올바른 API ID를 입력하세요.')
        selected=[sources[args.source]] if args.command=='test' else list(sources.values())
        for s in selected:
            print(json.dumps(collect_one(s,mode,args.date),ensure_ascii=False))
        return
    if args.command=='backfill-flights':
        if mode!='live':print('주의: mock 모드이므로 실제 과거 운항 데이터는 조회하지 않습니다.')
        src=sources['flights'];start=date.fromisoformat(args.date) if args.date else date.today()
        for i in range(3,-1,-1):
            d=(start-timedelta(days=i)).isoformat()
            print(json.dumps(collect_one(src,mode,d),ensure_ascii=False))
        return
    if args.command=='status':
        with Session() as db:
            for model in (CollectionRun,RawResponse,CongestionSnapshot,FlightRecord):
                print(model.__tablename__,db.scalar(select(func.count()).select_from(model)))
            for s in sources:
                row=db.execute(select(CollectionRun).where(CollectionRun.api_id==s).order_by(CollectionRun.id.desc()).limit(1)).scalar_one_or_none()
                print(s,'latest:',(row.finished_at,row.success,row.error_message) if row else 'none')
        return
    if args.command=='run':
        if mode=='live' and not args.confirm_live_schedule:
            p.error('실제 자동수집은 --confirm-live-schedule 지정 후 실행하세요. 호출량/데이터 검증이 먼저 필요합니다.')
        from apscheduler.schedulers.blocking import BlockingScheduler
        from zoneinfo import ZoneInfo
        sched=BlockingScheduler(timezone=ZoneInfo('Asia/Seoul'))
        enabled=[s for s in sources.values() if (mode=='mock' or s.get('enabled')) and s['interval_minutes']>0]
        for s in enabled:
            sched.add_job(collect_one,'interval',minutes=s['interval_minutes'],args=[s,mode],id=s['id'],max_instances=1,coalesce=True,misfire_grace_time=45)
        print('스케줄 시작:',mode,'대상:',[s['id'] for s in enabled],flush=True)
        for s in enabled:print(collect_one(s,mode),flush=True)
        sched.start()
if __name__=='__main__': main()
