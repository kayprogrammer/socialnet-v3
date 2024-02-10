# SOCIALNET V3

![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/fastapi.png?raw=true)


#### FASTAPI DOCS: [Documentation](https://fastapi.tiangolo.com/)
#### PICCOLO DOCS: [Documentation](https://piccolo-orm.readthedocs.io/) 
#### PG ADMIN: [Documentation](https://pgadmin.org) 


## How to run locally

* Download this repo or run: 
```bash
    $ git clone git@github.com:kayprogrammer/socialnet-v3.git
```

#### In the root directory:
- Install all dependencies
```bash
    $ pip install -r requirements.txt
```
- Create an `.env` file and copy the contents from the `.env.example` to the file and set the respective values. A postgres database can be created with PG ADMIN or psql

- Run Locally
```bash
    $ alembic upgrade heads 
```
```bash
    $ uvicorn app.main:app --debug --reload
```

- Run With Docker
```bash
    $ docker-compose up --build -d --remove-orphans
```
OR
```bash
    $ make build
```

- Test Coverage
```bash
    $ pytest --disable-warnings -vv
```
OR
```bash
    $ make test
```

![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/display1.png?raw=true)
![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/display2.png?raw=true)
![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/display3.png?raw=true)
![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/display4.png?raw=true)
![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/display5.png?raw=true)
![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/display6.png?raw=true)
![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/display7.png?raw=true)
![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/display8.png?raw=true)
![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/display9.png?raw=true)
![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/display10.png?raw=true)

![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/admin.png?raw=true)
