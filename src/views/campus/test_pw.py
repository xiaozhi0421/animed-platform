# -*- coding: utf-8 -*-
import urllib.request, json

def req(url, data=None, token=None, method=None):
    h = {'Content-Type': 'application/json'}
    if token: h['Authorization'] = token
    if data is not None: data = json.dumps(data, ensure_ascii=False).encode('utf-8')
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    resp = urllib.request.urlopen(r)
    return resp.status, json.loads(resp.read())

# Login student
data = json.dumps({'username':'20241001001','password':'123456'}).encode('utf-8')
r = urllib.request.Request('http://localhost:8080/auth/campus/login', data=data, headers={'Content-Type':'application/json'})
resp = urllib.request.urlopen(r)
s = json.loads(resp.read())
token = s['data']['token']
print('Student:', s['data']['realName'])

# Create a new password sign-in as teacher first
t_data = json.dumps({'username':'T102015001','password':'123456'}).encode('utf-8')
tr = urllib.request.Request('http://localhost:8080/auth/campus/login', data=t_data, headers={'Content-Type':'application/json'})
tresp = urllib.request.urlopen(tr)
t = json.loads(tresp.read())
t_token = t['data']['token']

# Create password sign-in
si = json.dumps({'classId':8,'title':'pw-test','signType':'密码签到','signPassword':'abcd','duration':30}, ensure_ascii=False).encode('utf-8')
si_r = urllib.request.Request('http://localhost:8080/user/class/sign-in', data=si, headers={'Content-Type':'application/json','Authorization':t_token})
si_resp = urllib.request.urlopen(si_r)
si_data = json.loads(si_resp.read())
si_id = si_data['data']['id']
print(f'Sign-in created: id={si_id}')

# Try to sign in with WRONG password
wrong_data = json.dumps({'signInId':si_id,'inputPassword':'wrong'}).encode('utf-8')
wrong_r = urllib.request.Request('http://localhost:8080/user/class/sign-in/do', data=wrong_data, headers={'Content-Type':'application/json','Authorization':token})
try:
    wrong_resp = urllib.request.urlopen(wrong_r)
    print(f'WRONG PASSWORD: Got HTTP {wrong_resp.status}')
    body = json.loads(wrong_resp.read())
    print(f'Body: {json.dumps(body, ensure_ascii=False)}')
except urllib.error.HTTPError as e:
    print(f'WRONG PASSWORD REJECTED: HTTP {e.code}')
    body = json.loads(e.read())
    print(f'Body: {json.dumps(body, ensure_ascii=False)}')

# Check records
recs_r = urllib.request.Request(f'http://localhost:8080/user/class/sign-in/{si_id}/records', headers={'Authorization':t_token})
recs_resp = urllib.request.urlopen(recs_r)
recs = json.loads(recs_resp.read())
for r in recs['data']:
    print(f'  Record: {r["studentName"]} - {r["result"]} - {r.get("failReason","")}')
