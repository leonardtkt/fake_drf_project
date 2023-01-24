# API

## Authentication

### Attaching Tokens to Requests

For clients to authenticate, the token key should be included in the Authorization HTTP header. The key should be prefixed by the string literal "Bearer", with whitespace separating the two strings. It should be a valid JWT token that is separated by two decimal places. For example:

```text
Authorization: Bearer ey0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTU4MDI1OTQwNSwianRpIjoiODQxMDhiMjdjYmNlNGE4NjkzNmM2YzFjMGM1Y2VlMjgiLCJ1c2VyX2lkIjoxfQ.zi8AlAD63_ZDiLl-PBIvNxIIGkaG9dodo8swlsYCKf5
```

The curl command line tool may be useful for testing token authenticated APIs. For example:

```bash
curl -X GET http://127.0.0.1:8000/ -H 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90dXBlIjoicmVmctVzaCIsImV4cCI6MTU4MDI1OTQwNSwianRpIjoiODQxMDhiMjdjYmNlNGE4NjkzNmM2YzFjMGM1Y2VlMjgiLCJ1c2VyX2lkIjoxfQ.zi8AlAD63_ZDiLl-PBIvNxIIGkaG9dodo8swlsYCKf4'
```

### Token Contents

Your token will decode to something like this (informational only - not needed to be used in relation to any HTTP requests):

```json
{
  "typ": "JWT",
  "alg": "HS256"
},
{
  "token_type": "access",
  "exp": 1812954379,
  "jti": "84b15c5287af51a58589698f2e7c9407",
  "user_id": 1
},
{} // signature data in third object
```

### Interacting with Tokens via Shell

You can retrieve a token for any user this way:

```python
from users.models import User
user = User.objects.get(id=<your_id>)
user.access_token
```

If you have received a token and want to inspect its contents, you can unpack it using a tool on the web
(see for example: https://www.jsonwebtoken.io/ - probably better to not add the signing key here though.)

Or via shell:

```python
import jwt
from django.conf import settings
token = '<paste your JWT token here>'
jwt.decode(token, algorithms=['HS256'], key=settings.SECRET_KEY)
```

It will print the contents and will throw a `InvalidSignatureError` if it doesn't match the secret key for your environment.

### Retrieving Tokens via API

A registered user can retrieve their access and refresh JWT tokens with the following request:

**Request**:

`POST` `/auth/token/`

Parameters:

Name | Type | Description
---|---|---
username | string | The user's username
password | string | The user's password

**Response**:

```json
{
  "refresh": "eyJ0eTAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTU4MDI1OTQwNSwianRpIjoiODQxMDhiMjdjYmNlNGE4NjkzNmM2YzFjMGM1Y2VlMjgiLCJ1c2VyX2lkIjoxfQ.zi8AlAD63_ZDiLl-PBIvNxIIGkaG9dodo8swlsYCKf4",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiRIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTgwMTczMzA1LCJqdGkiOiJiMmUyNTNlYjZlMWY0ZmViYmQxOTBjMjgwYzYyZTcwNSIsInVzZXJfaWQiOjF9.iYcmNenUq_GqH2ShEfdBM_B7p_JGaeiCtQ4fsE-jRQc"
}
```

Frontend can then use the refresh token to get a new access token after that specific access token expired.

`POST` `/auth/token/refresh/`

Parameters:

Name | Type | Description
---|---|---
refresh_token | string | The above refresh token initially provided.

**Response**:

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiRIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTgwMTczMzA1LCJqdGkiOiJiMmUyNTNlYjZlMWY0ZmViYmQxOTBjMjgwYzYyZTcwNSIsInVzZXJfaWQiOjF9.iYcmNenUq_GqH2ShEfdBM_B7p_JGaeiCtQ4fsE-jRQc"
}
```

## Structure

This project uses [drf-nested-routers](https://github.com/alanjds/drf-nested-routers). So if a group is a subset of another group, we should specify both in the path.

Example:

There are 1000 students at a school, but only 30 in a class. To obtain a list of students in that class, we visit the following relative url: /classes/5/students/. To see a detail view of one of those students we can visit /classes/5/students/219/.

## Documentation

There are two different sets of API documentation available for frontend developers. Both [Redoc](https://github.com/Redocly/redoc) and [Swagger](https://swagger.io/docs/) have endpoints which are available when the project is running with `DEBUG=True`.

* Redoc: [http://localhost:8000/redoc/](http://localhost:8000/redoc/)
* Swagger: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
