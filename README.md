### 10 steps to deploy this API to a container on Heroku

1 - Create accounts on [Heroku](https://signup.heroku.com/account) and [Docker](https://www.docker.com/)

2 - Download and install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) and [Docker](https://www.docker.com/get-docker)

3 - Install the client tool of the Heroku Container Registry
```
heroku plugins:install heroku-container-registry
```

4 - Login to Heroku and to the Container Registry
```
heroku login
heroku container:login
```

5 - Open a terminal and clone this repository
```
git clone git@github.com:linkehub/linkehub_api.git
```

6 - Enter into the folder that contains the API
```
cd linkehub_api
```

7 - Inside the root of the project build an image with the Dockerfile. Don't forget of adding the . at the end of the command
```
docker image build -t linkehub-api:0.1 .
```

8 - Create a Heroku app and associate it with an instance of the API
```
heroku apps:create linkehub-api-2
```

9 - Deploy the new instance to a Docker container on Heroku
```
heroku container:push web --app linkehub-api-2
```

10 - Release the instance that you just deployed and open it
```
heroku container:release web --app linkehub-api-2
heroku open
```
<br>

### Starting the project locally and adding new libraries

1 - Make sure you have [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/#virtualenvironments-ref) and install it into the webapp folder
```
pip3 install --user virtualenv
virtualenv ENV
```

2 - Inside the root of the webapp, activate the [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/#virtualenvironments-ref)
```
source ENV/bin/activate 
```

3 - Install the list of requirements of the project
```
pip3 install -r requirements.txt
```

4 - Install or uninstall other libraries with pip3 as you need
```
pip3 install scipy
pip3 uninstall scipy
```

5 - Update the list of dependencies after you're done installing or uninstalling, this is important because the Dockerfile uses the requirements.txt to build the image
```
pip3 freeze > requirements.txt
```

6 - If you want to deactivate virtualenv
```
deactivate
```
<br>

### Running the API locally

1 - Inside the root of the webapp, export the Flask app
```
export FLASK_APP=app.py
```

2 - Run it
```
flask run
```
