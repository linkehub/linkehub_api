### 10 steps to deploy [this API](https://github.com/linkehub/linkehub_api) to a container on Heroku

1 - Create an account on [Heroku](https://signup.heroku.com/account)

2 - Download [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

3 - Login
```
heroku login
```

4 - Open a terminal and clone [this repository](https://github.com/linkehub/linkehub_api):
```
git clone git@github.com:linkehub/linkehub_api.git
```

5 - Enter into the folder that contains the API
```
cd linkehub_api
```

6 - Create a Heroku app and associate it with an instance of the API
```
Heroku apps:create linkehub-api-2
```

7 - Verify if the heroku remote is associate with the local git repository:
```
git remote -v
```

8 - Login into the Heroku Container Registry
```
heroku container:login
```

9 - Deploy the new instance to a Docker container on Heroku
```
heroku container:push web
```

10 - Verify if your instance is running
```
heroku open
```
