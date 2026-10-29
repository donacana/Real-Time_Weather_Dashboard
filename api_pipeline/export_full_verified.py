"""Verified ICN API raw export + conservative normalized preview.
Run: python export_full_verified.py --date YYYY-MM-DD --sources flights facilities
Requires .env API keys; never prints or exports API keys.
Does NOT alter production database. Paginates flights and facilities using totalCount.
"""
import argparse, copy, json, math, time
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from pipeline.sources import load_sources
from pipeline.collector import fetch

KST = ZoneInfo('Asia/Seoul')

def parse_response(body):
    doc=json.loads(body)
    if not isinstance(doc,dict): raise ValueError('Non-JSON-object response')
    resp=doc.get('response') or {}
    header=resp.get('header') or {}
    if str(header.get('resultCode')) not in ('00','0'): raise ValueError('API error: '+repr(header))
    data=resp.get('body') or {}
    items=data.get('items',[])
    if isinstance(items,dict):items=items.get('item',[])
    if items is None:items=[]
    if isinstance(items,dict):items=[items]
    if not isinstance(items,list):raise ValueError('Unexpected items structure')
    return doc,items,int(data.get('totalCount',len(items)))

def clean_int(v):
    if v is None or str(v).strip()=='':return None
    return int(float(v))

def utc_time(v):
    if v is None or str(v).strip()=='':return None
    return datetime.strptime(str(v),'%Y%m%d%H%M').replace(tzinfo=timezone.utc).isoformat()

def local_time(v):
    if v is None or str(v).strip()=='':return None
    return datetime.strptime(str(v),'%Y%m%d%H%M').replace(tzinfo=KST).isoformat()

def safe_float(v):
    if v is None or str(v).strip() in ('','-'):return None
    return float(v)

def normalized(source_id,record):
    if source_id=='flights':
        code=record.get('terminalId')
        return {'source_fid':record.get('fid'),'flight_no':record.get('flightId'),
            'master_flight_no':record.get('masterFlightId'),'codeshare':record.get('codeshare'),
            'terminal_raw':code,'terminal_area':{'P01':'T1','P02':'CONCOURSE_T1','P03':'T2'}.get(code),
            'scheduled_at_kst':local_time(record.get('scheduleDatetime')),
            'estimated_at_kst':local_time(record.get('estimatedDatetime')),
            'status_raw':record.get('remark'),'gate_number':record.get('gateNumber'),
            'checkin_range':record.get('chkinRange'),'destination_code':record.get('airportCode'),
            'raw':record}
    if source_id=='facilities':
        return {'source_facility_id':None,'name_raw':record.get('entrpskoreannm'),
            'service_raw':record.get('trtmntprdlstkoreannm'),
            'location_raw':record.get('lckoreannm'),
            'arrival_departure_raw':record.get('arrordep'),
            'service_time_raw':record.get('servicetime'),
            'phone_raw':record.get('tel'), 'terminal_code':None,'category':None,'raw':record}
    if source_id in ('congestion_t1','congestion_t2'):
        gate=record.get('gateId'); when=record.get('occurtime'); wait=record.get('waitTime')
        return {'terminal_id_raw':record.get('terminalId'),'gate_id_raw':gate,
            'hall_number':(int(gate.split('_')[0][2:]) if isinstance(gate,str) and gate.startswith('DG') and gate.split('_')[0][2:].isdigit() else None),
            'observed_at_kst':datetime.strptime(str(when),'%Y%m%d%H%M%S').replace(tzinfo=KST).isoformat() if when else None,
            'wait_length_persons':clean_int(record.get('waitLength')),
            'wait_time_minutes':(None if wait is None or str(wait).strip() in ('','-') else 60 if str(wait).strip()=='60+' else safe_float(wait)),
            'wait_time_is_over_60':str(wait).strip()=='60+',
            'operating_time_raw':record.get('operatingTime'),'raw':record}
    if source_id=='takeoff_forecast':
        ws=safe_float(record.get('ws')); qnh=safe_float(record.get('qnh'))
        return {'airport':record.get('icaoCode'),'valid_at_utc':utc_time(record.get('tmFc')),
            'wind_direction_degrees':safe_float(record.get('wd')),
            'wind_speed_ms':round(ws*0.514444,4) if ws is not None else None,
            'temperature_c':safe_float(record.get('ta')),
            'pressure_hpa':round(qnh/100*33.8638866667,3) if qnh is not None else None,
            'issued_at_utc':None, 'raw':record}
    return {'raw':record}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--date',default=datetime.now(KST).date().isoformat(),help='YYYY-MM-DD (flights)')
    p.add_argument('--sources',nargs='+',default=['flights','facilities'],
                   choices=['flights','facilities','congestion_t1','congestion_t2','passenger_forecast','metar','takeoff_forecast'])
    p.add_argument('--max-requests',type=int,default=30,help='Hard cap for this script')
    p.add_argument('--delay',type=float,default=0.35)
    p.add_argument('--output',default='full_api_export')
    args=p.parse_args()
    if args.max_requests<1: p.error('--max-requests must be positive')
    cfgs=load_sources();out=Path(args.output);out.mkdir(exist_ok=True)
    calls=0; summary=[]
    for source_id in args.sources:
        src=copy.deepcopy(cfgs[source_id]);rows=[];page=1;tot=None; expected_pages=None
        per_page=int(src.get('params',{}).get('numOfRows',100))
        if per_page<1:raise ValueError('numOfRows must be positive')
        if source_id not in ('flights','facilities'):expected_pages=1
        while expected_pages is None or page<=expected_pages:
            if calls>=args.max_requests:raise RuntimeError(f'Call cap {args.max_requests} reached. Stopping before next request.')
            src['params']['pageNo']=page
            body,http_status,_=fetch(src,'live',args.date)
            calls+=1
            doc,items,total=parse_response(body)
            if tot is None:
                tot=total
                expected_pages=max(1,math.ceil(total/per_page)) if source_id in ('flights','facilities') else 1
                if expected_pages>args.max_requests-calls+1:
                    print(f'[NOTICE] {source_id}: {expected_pages} pages; remaining call budget may be insufficient')
            if page==1 and total>0 and not items:raise RuntimeError(f'{source_id}: totalCount={total} but first page has zero items')
            (out / f'{source_id}_page_{page:02d}.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
            rows.extend(items)
            print(f'{source_id} page {page}/{expected_pages} HTTP {http_status} got {len(items)} rows; totalCount {total}',flush=True)
            if page<expected_pages and len(items)==0:raise RuntimeError(f'{source_id}: early empty page; no silent completion')
            page+=1
            if page<=expected_pages:time.sleep(max(0,args.delay))
        if source_id in ('flights','facilities') and len(rows)!=tot:
            raise RuntimeError(f'{source_id}: incomplete: got {len(rows)} vs totalCount {tot}. Raw pages preserved.')
        (out/f'{source_id}_all.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
        with (out/f'{source_id}_normalized_preview.jsonl').open('w',encoding='utf-8') as f:
            for r in rows:f.write(json.dumps(normalized(source_id,r),ensure_ascii=False)+'\n')
        summary.append({'source':source_id,'page_count':expected_pages,'total_count':tot,'exported_items':len(rows)})
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Finished; calls:',calls,'files:',out.resolve())
if __name__=='__main__':main()
