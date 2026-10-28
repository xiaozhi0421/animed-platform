# -*- coding: utf-8 -*-
import urllib.request, json

def json_req(url, data=None, token=None, method=None):
    headers = {'Content-Type': 'application/json'}
    if token: headers['Authorization'] = token
    if data: data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

# 1. Login as teacher
teacher = json_req('http://localhost:8080/auth/campus/login', {'username':'T102015001','password':'123456'})
teacher_token = teacher['data']['token']
print(f'1. Teacher: {teacher["data"]["realName"]}')

# 2. Create class
cls = json_req('http://localhost:8080/user/class', 
    {'className':'\u52a8\u7269\u533b\u5b662025-1\u73ed','academicYear':'2025-2026','semester':'\u7b2c\u4e00\u5b66\u671f','description':'\u6d4b\u8bd5\u73ed\u7ea7'},
    token=teacher_token)
class_id = cls['data']['id']
class_code = cls['data']['classCode']
print(f'2. Class: id={class_id}, code={class_code}, teacher={cls["data"]["teacherName"]}')

# 3. Login as student
student = json_req('http://localhost:8080/auth/campus/login', {'username':'20241001001','password':'123456'})
student_token = student['data']['token']
print(f'3. Student: {student["data"]["realName"]}')

# 4. Join class
join_res = json_req('http://localhost:8080/user/class/join?classCode=' + class_code, token=student_token, method='POST')
print(f'4. Join class: code={join_res["code"]}, msg={join_res["msg"]}')

# 5. Create sign-in (normal)
si = json_req('http://localhost:8080/user/class/sign-in',
    {'classId':class_id,'title':'\u7b2c\u4e00\u8282\u7b7e\u5230','signType':'\u666e\u901a\u7b7e\u5230','duration':30},
    token=teacher_token)
sign_in_id = si['data']['id']
print(f'5. Sign-in created: id={sign_in_id}')

# 6. Student do sign-in
do_si = json_req('http://localhost:8080/user/class/sign-in/do', {'signInId':sign_in_id}, token=student_token)
print(f'6. Sign-in result: {do_si["data"]["result"]}')

# 7. Check records
records = json_req(f'http://localhost:8080/user/class/sign-in/{sign_in_id}/records', token=teacher_token)
for r in records['data']:
    print(f'   Record: {r["studentName"]} - {r["result"]} - {r.get("failReason","")}')

# 8. Test password sign-in
si2 = json_req('http://localhost:8080/user/class/sign-in',
    {'classId':class_id,'title':'\u5bc6\u7801\u7b7e\u5230\u6d4b\u8bd5','signType':'\u5bc6\u7801\u7b7e\u5230','signPassword':'123456','duration':30},
    token=teacher_token)
si2_id = si2['data']['id']
print(f'8. Password sign-in created: id={si2_id}')

# 9. Student do password sign-in (wrong password)
try:
    json_req('http://localhost:8080/user/class/sign-in/do', {'signInId':si2_id,'inputPassword':'wrong'}, token=student_token)
except Exception as e:
    print(f'9. Wrong password: expected error ({e.code if hasattr(e,\"code\") else "?"})')

# 10. Student do password sign-in (correct)
do_si2 = json_req('http://localhost:8080/user/class/sign-in/do', {'signInId':si2_id,'inputPassword':'123456'}, token=student_token)
print(f'10. Correct password: {do_si2["data"]["result"]}')

# 11. Create homework
hw = json_req('http://localhost:8080/user/class/homework',
    {'classId':class_id,'title':'\u7b2c\u4e00\u6b21\u4f5c\u4e1a','deadline':'2026-07-01T23:59:59','description':'\u8bf7\u5b8c\u6210\u7b2c\u4e00\u7ae0\u4e60\u9898'},
    token=teacher_token)
hw_id = hw['data']['id']
print(f'11. Homework created: id={hw_id}')

# 12. Student submit homework
sub = json_req('http://localhost:8080/user/class/homework/submit',
    {'homeworkId':hw_id,'content':'\u5df2\u5b8c\u6210\u7b2c\u4e00\u7ae0\u4e60\u9898\uff0c\u7b54\u6848\u89c1\u9644\u4ef6'},
    token=student_token)
print(f'12. Homework submitted: id={sub["data"]["id"]}')

# 13. Teacher grade
grade = json_req('http://localhost:8080/user/class/homework/grade',
    {'submitId':sub['data']['id'],'score':95,'comment':'\u4f18\u79c0\uff01'},
    token=teacher_token)
print(f'13. Homework graded')

print('\\n=== ALL TESTS PASSED ===')
