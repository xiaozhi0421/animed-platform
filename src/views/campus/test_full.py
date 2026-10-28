# -*- coding: utf-8 -*-
import urllib.request, json

def req(url, data=None, token=None, method=None):
    h = {'Content-Type': 'application/json'}
    if token: h['Authorization'] = token
    if data is not None: data = json.dumps(data, ensure_ascii=False).encode('utf-8')
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    resp = urllib.request.urlopen(r)
    body = json.loads(resp.read())
    if body.get('code') != 200:
        raise Exception(f'API Error: {body.get("msg")} (code={body.get("code")})')
    return body

def check_req(url, data=None, token=None, method=None):
    """Make request and return status + body without raising on business errors"""
    h = {'Content-Type': 'application/json'}
    if token: h['Authorization'] = token
    if data is not None: data = json.dumps(data, ensure_ascii=False).encode('utf-8')
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    resp = urllib.request.urlopen(r)
    return resp.status, json.loads(resp.read())

print('========== 完整功能测试 ==========')

# 1. Teacher login
t = req('http://localhost:8080/auth/campus/login', {'username':'T102015001','password':'123456'})
t_token = t['data']['token']
print(f'1. 教师登录: {t["data"]["realName"]} (role={t["data"]["role"]})')

# 2. Get teacher classes
cl = req('http://localhost:8080/user/class/teacher', token=t_token)
cid = cl['data'][0]['id']
ccode = cl['data'][0]['classCode']
print(f'2. 班级: {cl["data"][0]["className"]} (ID={cid}, 码={ccode}, 教师={cl["data"][0]["teacherName"]})')

# 3. Get members
m = req(f'http://localhost:8080/user/class/{cid}/members', token=t_token)
names = [mb['userName'] + '(' + mb['role'] + ')' for mb in m['data']]
print(f'3. 成员: {", ".join(names)}')
assert any(mb['role'] == '教师' for mb in m['data']), '教师角色错误!'
assert any(mb['role'] == '学生' for mb in m['data']), '学生角色错误!'

# 4. Teacher create normal sign-in
si1 = req('http://localhost:8080/user/class/sign-in', {'classId':cid,'title':'课堂签到','signType':'普通签到','duration':30}, token=t_token)
si1_id = si1['data']['id']
print(f'4. 发起普通签到: ID={si1_id}, 状态={si1["data"]["status"]}')

# 5. Teacher create password sign-in
si2 = req('http://localhost:8080/user/class/sign-in', {'classId':cid,'title':'密码签到','signType':'密码签到','signPassword':'2024','duration':30}, token=t_token)
si2_id = si2['data']['id']
print(f'5. 发起密码签到: ID={si2_id}')

# 6. Teacher create homework
hw = req('http://localhost:8080/user/class/homework', {'classId':cid,'title':'第一章作业','deadline':'2026-07-01T23:59:59','description':'完成课后习题'}, token=t_token)
hw_id = hw['data']['id']
print(f'6. 发布作业: ID={hw_id}, 标题={hw["data"]["title"]}')

# 7. Student login
s = req('http://localhost:8080/auth/campus/login', {'username':'20241001001','password':'123456'})
s_token = s['data']['token']
print(f'7. 学生登录: {s["data"]["realName"]} (role={s["data"]["role"]})')

# 8. Student get classes
scl = req('http://localhost:8080/user/class/student', token=s_token)
print(f'8. 学生班级: {scl["data"][0]["className"]}')

# 9. Student normal sign-in
dsi1 = req('http://localhost:8080/user/class/sign-in/do', {'signInId':si1_id}, token=s_token)
assert dsi1['data']['result'] == '成功', f'普通签到失败: {dsi1["data"]["result"]}'
print(f'9. 学生普通签到: {dsi1["data"]["result"]}')

# 10. Student password sign-in (wrong password)
s10, b10 = check_req('http://localhost:8080/user/class/sign-in/do', {'signInId':si2_id,'inputPassword':'wrong'}, token=s_token)
assert b10.get('code') != 200 or b10.get('data',{}).get('result') == '失败', '错误密码应该被拒绝!'
print(f'10. 错误密码签到: msg={b10.get("msg","")} (正确拒绝)')

# 11. Student password sign-in (correct password)
dsi2 = req('http://localhost:8080/user/class/sign-in/do', {'signInId':si2_id,'inputPassword':'2024'}, token=s_token)
assert dsi2['data']['result'] == '成功', f'正确密码签到失败: {dsi2["data"]["result"]}'
print(f'11. 正确密码签到: {dsi2["data"]["result"]}')

# 12. Student submit homework
sub = req('http://localhost:8080/user/class/homework/submit', {'homeworkId':hw_id,'content':'已完成第一章习题'}, token=s_token)
print(f'12. 学生提交作业: ID={sub["data"]["id"]}, 内容={sub["data"]["content"]}')

# 13. Teacher view submissions
subs = req(f'http://localhost:8080/user/class/homework/{hw_id}/submissions', token=t_token)
print(f'13. 查看提交: {len(subs["data"])} 条')
assert len(subs['data']) > 0, '没有提交记录!'

# 14. Teacher grade
req('http://localhost:8080/user/class/homework/grade', {'submitId':sub['data']['id'],'score':95,'comment':'优秀'}, token=t_token)
print('14. 教师评分: 完成')

# 15. Teacher view sign-in records
recs = req(f'http://localhost:8080/user/class/sign-in/{si1_id}/records', token=t_token)
print(f'15. 签到记录: {len(recs["data"])} 条')
for r in recs['data']:
    print(f'     {r["studentName"]}: {r["result"]}')

# 16. Teacher end sign-in
req(f'http://localhost:8080/user/class/sign-in/{si1_id}/end', token=t_token, method='POST')
req(f'http://localhost:8080/user/class/sign-in/{si2_id}/end', token=t_token, method='POST')
print('16. 结束签到: 完成')

# 17. Verify ended status
sil = req(f'http://localhost:8080/user/class/{cid}/sign-in', token=t_token)
ended = sum(1 for s in sil['data'] if s['status'] == '已结束')
print(f'17. 已结束签到: {ended} 个')

# 18. Check student homework list
shl = req(f'http://localhost:8080/user/class/{cid}/homework/student', token=s_token)
print(f'18. 学生作业列表: {len(shl["data"])} 条')

print()
print('========== 全部通过! ==========')
print(f'班级: 动物医学2025-1班 (码: {ccode})')
print(f'教师: 刘教授')
print(f'学生: 张三')
