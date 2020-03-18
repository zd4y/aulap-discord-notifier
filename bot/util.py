import json
import urllib.parse


class AulapError(Exception):
    """
    Base exception for AulaPlaneta errors
    """


class InvalidToken(AulapError):
    """
    Raised when given token is invalid
    """


def get_url_params(url):
    url = str(url)
    parsed = urllib.parse.urlparse(url).query
    return urllib.parse.parse_qs(parsed)


async def post(session, url, *args, **kwargs):
    async with session.post(url, *args, **kwargs) as response:
        return response.url


async def fetch_json(session, url, *args, **kwargs):
    async with session.get(url, *args, **kwargs) as response:
        return (await response.json()), response.url, response.status


async def get_student_id(session_token, username, token):
    if token is None:
        raise InvalidToken('You must provide a token!')
    url = 'https://wapi.aulaplaneta.com/WAPI_AulaPlaneta/api/alumnos/GetAlumnoByUserName'
    params = {
        'pUserName': username
    }
    res_json, _, status_code = await fetch_json(session_token, url, params=params, headers={'Authorization': f'Session {token}'})
    if status_code == 401:
        raise InvalidToken('The given token is invalid!')
    elif status_code == 400:
        return None
    return int(res_json['alum_id'])


async def get_token(session_token, username, password):
    url = 'https://registro.aulaplaneta.com/'
    data = {
        '__VIEWSTATE': '/wEPDwUKMTU4ODQxNTYxNw9kFgJmD2QWAgIDD2QWBAIGD2QWBAIGD2QWDgIBDw8WAh4HVmlzaWJsZWdkZAIDDw8WBB4E'
                       'VGV4dAUUYWxlamFuZHJvYXJpYXNvcm96Y28fAGdkZAIFDw8WBB8BBRRhbGVqYW5kcm9hcmlhc29yb3pjbx8AaBYCHgtw'
                       'bGFjZWhvbGRlcgUgSW50cm9kdWNlIHR1IHVzdWFyaW8gYXVsYVBsYW5ldGFkAgkPDxYCHwBnZBYCZg8PZBYCHwIFGElu'
                       'dHJvZHVjZSB0dSBDb250cmFzZcOxYWQCCw8PFgIfAWVkZAINDw8WAh8AaGRkAg8PDxYCHwBnZGQCCg8PFgIeC05hdmln'
                       'YXRlVXJsZGRkAgwPFgIfAQURIDIwMjAgYXVsYVBsYW5ldGFkZMUh7zynTDVq6xx3MZuRHtGOL/Q6',
        '__EVENTVALIDATION': '/wEdAAjEbGKQZ8EEQn3eu/45K5k1V/NIUwxcgk8uhraZFeo/T5jc8X/OeYsNy9+KgXIoSOYr7FpIrmWo7EoLvI'
                             'uOrC02/qHWVgK0CvFlJT41CcJ6fy7P61kkq/D0tJYZVkgmdwARq65RFnLgS8cXVQFK4w1+fDc81s1mqdL2EfJ3'
                             'ShYdE6hCiDipf/+Do8vuEa7Mma7CsJUa',
        'userNamehidden': username,
        'ctl00$Content$txtPassword': password,
        'ctl00$Content$btnLogin': 'entrar'
    }

    url = await post(session_token, url, data=data)
    url = get_url_params(url)
    url = urllib.parse.unquote(url['UrlRedirect'][0])
    url = get_url_params(url)
    access_token = json.loads(url['access_token'][0])['access_token']

    return access_token


async def get_homeworks(session_token, student_id, token):
    if token is None:
        raise InvalidToken('You must provide a token!')
    params = {
        'pAlumno': student_id,
        'pTop': 5
    }
    url = 'https://wapi.aulaplaneta.com/WAPI_AulaPlaneta/api/tareas/GetTareasActivasSinAcabarByAlumno'
    res_json, _, status_code = await fetch_json(session_token, url, params=params, headers={'Authorization': f'Session {token}'})
    if status_code == 401:
        raise InvalidToken('The given token is invalid!')
    return res_json
