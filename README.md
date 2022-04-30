# Sport Marketplace Platform

**Version 1.0.0**

---
# Project Description
Welcome to the Sport Marketplace Platform, here you can find your perfect coach, see his/her rates, coast, location, posts and more!

## Project Technology:
- **Backed**   - Django Rest Framework.
- **DB**       - MYSQL (Now wrote with SQLITE. Soon it is going to be MYSQL)
- **Frontend** - React Native / ReactJS

---

#Django Rest Framework Files 
where are all the code?
1. Each module has models file\
   for example: '/sport_type/models.py'
<br/>
<br/>
2. For each module you have "api" folder. in that folder you have the api code.\
here you can find this files:
- serializer.py
- urls.py
- views.py

    For example '/coach_app/api'
3. Tests files explain here -> [Server Tests](#server-tests)
# How To Start 
project start is super easy,

- clone the project

```bash
git clone https://github.com/Bfit-company/bfit-django-server.git
```

great! now you got the project.

- run the server
```bash
sh docker_run.sh
```
The server will run on port **8000**

### Stop the server
For stop the server just write **CRL + C**

---
#<a name="server-tests"></a>Server Tests
As you know great project needs to be tested
### Tests in Django - 
In django every module has test file.(all the modules extends from **PYTEST**) 
test file example: user_app/tests.py

**How to run Tests**
for running tests in Django you just need to write the following line:

```bash
python3 manage.py test
```

Automatically all the tests.py in the project will run

