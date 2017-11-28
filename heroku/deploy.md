
## Deploying via Heroku

Start by [signing up](https://signup.heroku.com/). After that we can install the [heroku-cli](https://devcenter.heroku.com/articles/heroku-cli) to interact with heroku.

```bash
# On a mac we can use homebrew
brew install heroku/brew/heroku

# the heroku-cli need to sync with our account,
# type in the command below and enter our information
heroku login

# we then create the application,
# replace <appname> with the actual name,
# once deployed the application will be available at
# http://<appname>.herokuapp.com.
heroku create <appname>
```

Next we define a `Procfile` so that Heroku knows what command to use to start the application, note that the file should be called Procfile with no file extension. In our case the content should look something like:

```
web: knowledge_repo --repo <knowledge-repo-name> deploy
```

Replace the <knowledge-repo-name> with the actual name for the `knowledge-repo`. Remember to also include the dependencies in a `requirements.txt` file (e.g. the knowledge repo uses `gunicorn` for web server).


```bash
# we should now be able to run it locally
heroku local web

# to push local changes and deploy
# do the normal add and commit
git add --all
git commit -m "some message"

# deploy it
git push heroku master
```


heroku open