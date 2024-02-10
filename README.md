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

![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/disp1.png?raw=true)
![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/disp2.png?raw=true)
![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/disp3.png?raw=true)
![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/disp4.png?raw=true)
![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/disp5.png?raw=true)
![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/disp6.png?raw=true)
![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/disp7.png?raw=true)
![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/disp8.png?raw=true)
![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/disp9.png?raw=true)
![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/disp10.png?raw=true)

![alt text](https://github.com/kayprogrammer/socialnet-v3/blob/main/display/admin.png?raw=true)
