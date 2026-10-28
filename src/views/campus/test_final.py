# -*- coding: utf-8 -*-
import urllib.request, json, time

def req(url, data=None, token=None, method=None):
    h = {'Content-Type': 'application/json'}
    if token: h['Authorization'] = token
    if data is not None: data = json.dumps(data, ensure_ascii=False).encode('utf-8')
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    return json.loads(urllib.request.urlopen(r).read())

# 0. Clean up old class (id=6) with Chinese name first
# Login teacher
t = req('http://localhost:8080/auth/campus/login', {'username':'T102015001','password':'123456'})
t_token = t['data']['token']
print('1. Login teacher: ' + t['data']['realName'])

# Delete class 6 (the one with ??? name)
try:
    req('http://localhost:8080/user/class/6/members', token=t_token)
    print('2. Class 6 exists, will keep for now')
except:
    print('2. Class 6 gone')

# Create new class with Chinese name
cls = req('http://localhost:8080/user/class',
    {'className':'\u52a8\u7269\u533b\u5b662025-1\u73ed','academicYear':'2025-2026','semester':'\u7b2c\u4e00\u5b66\u671f','description':'\u6d4b\u8bd5\u73ed\u7ea7'},
    token=t_token)
cid = cls['data']['id']
ccode = cls['data']['classCode']
print('3. Create class: id=' + str(cid) + ', code=' + ccode + ', teacher=' + cls['data']['teacherName'])

# Login student
s = req('http://localhost:8080/auth/campus/login', {'username':'20241001001','password':'123456'})
s_token = s['data']['token']
print('4. Login student: ' + s['data']['realName'])

# Join class
j = req('http://localhost:8080/user/class/join?classCode=' + ccode, token=s_token, method='POST')
print('5. Join class: ' + str(j['code']))

# ------ TEST 1: Normal sign-in (普通签到) ------
si1 = req('http://localhost:8080/user/class/sign-in',
    {'classId':cid,'title':'\u666e\u901a\u7b7e\u5230\u6d4b\u8bd5','signType':'\u666e\u901a\u7b7e\u5230','duration':30},
    token=t_token)
si1_id = si1['data']['id']
print('6. Normal sign-in created: id=' + str(si1_id))

dosi1 = req('http://localhost:8080/user/class/sign-in/do', {'signInId':si1_id}, token=s_token)
print('7. Normal sign-in result: ' + dosi1['data']['result'] + ' (should be \u6210\u529f)')

# ------ TEST 2: Password sign-in (密码签到) ------
si2 = req('http://localhost:8080/user/class/sign-in',
    {'classId':cid,'title':'\u5bc6\u7801\u7b7e\u5230\u6d4b\u8bd5','signType':'\u5bc6\u7801\u7b7e\u5230','signPassword':'123456','duration':30},
    token=t_token)
si2_id = si2['data']['id']
print('8. Password sign-in created: id=' + str(si2_id))

# Wrong password
try:
    req('http://localhost:8080/user/class/sign-in/do', {'signInId':si2_id,'inputPassword':'wrong'}, token=s_token)
except Exception as e:
    print('9. Wrong password: expected error')

# Correct password
dosi2 = req('http://localhost:8080/user/class/sign-in/do', {'signInId':si2_id,'inputPassword':'123456'}, token=s_token)
print('10. Correct password result: ' + dosi2['data']['result'] + ' (should be \u6210\u529f)')

# ------ TEST 3: Records ------
recs = req('http://localhost:8080/user/class/sign-in/' + str(si1_id) + '/records', token=t_token)
print('11. Normal sign-in records:')
for r in recs['data']:
    print('    ' + r['studentName'] + ' -> ' + r['result'])

recs2 = req('http://localhost:8080/user/class/sign-in/' + str(si2_id) + '/records', token=t_token)
print('12. Password sign-in records:')
for r in recs2['data']:
    print('    ' + r['studentName'] + ' -> ' + r['result'] + (' (' + r.get('failReason','') + ')' if r.get('failReason') else ''))

# ------ TEST 4: End sign-in ------
end1 = req('http://localhost:8080/user/class/sign-in/' + str(si1_id) + '/end', token=t_token, method='POST')
print('13. End normal sign-in: ' + str(end1['code']))

# ------ TEST 5: Homework ------
hw = req('http://localhost:8080/user/class/homework',
    {'classId':cid,'title':'\u7b2c\u4e00\u6b21\u4f5c\u4e1a','deadline':'2026-07-01T23:59:59','description':'\u8bf7\u5b8c\u6210\u7b2c\u4e00\u7ae0\u4e60\u9898'},
    token=t_token)
hw_id = hw['data']['id']
print('14. Homework created: id=' + str(hw_id))

sub = req('http://localhost:8080/user/class/homework/submit',
    {'homeworkId':hw_id,'content':'\u5df2\u5b8c\u6210\u7b2c\u4e00\u7ae0\u4e60\u9898'},
    token=s_token)
print('15. Submitted: id=' + str(sub['data']['id']))

grade = req('http://localhost:8080/user/class/homework/grade',
    {'submitId':sub['data']['id'],'score':92,'comment':'\u5f88\u597d'},
    token=t_token)
print('16. Graded: ' + str(grade['code']))

# ------ TEST 6: Members ------
members = req('http://localhost:8080/user/class/' + str(cid) + '/members', token=t_token)
print('17. Members:')
for m in members['data']:
    print('    ' + m['userName'] + ' (' + m['role'] + ')')

# ------ TEST 7: Student join again (should fail) ------
try:
    req('http://localhost:8080/user/class/join?classCode=' + ccode, token=s_token, method='POST')
    print('18. Join again: UNEXPECTED SUCCESS')
except Exception as e:
    print('18. Join again: correctly rejected')

print('')
print('=== ALL TESTS COMPLETED ===')
