

### steps taken:
```sh
#---------testing locally
heroku local web -f Procfile.mac
#---------deploying
# create the app
heroku create toronto-crime-dash-app 
# add the app as a remote git branch (https://devcenter.heroku.com/articles/git#for-an-existing-heroku-app)
heroku git:remote -a toronto-crime-dash-app
# push the code up (for pushing a non-main branch, but wasn't working properly: https://stackoverflow.com/questions/2971550/heroku-how-to-push-different-local-git-branches-to-heroku-master)
git push heroku main
# git push https://git.heroku.com/toronto-crime-dash-app.git main
# scale and open
heroku ps:scale web=1
heroku open
# logs
heroku logs --tail
```

### trouble shooting
- Why am I seeing "Couldn't find that process type" when trying to scale dynos?
  - https://help.heroku.com/W23OAFGK/why-am-i-seeing-couldn-t-find-that-process-type-when-trying-to-scale-dynos


### multiple apps in 1 repo: (WIP)
- https://stackoverflow.com/questions/41461517/deploy-two-separate-heroku-apps-from-same-git-repo
- multi-procfile abilities (https://elements.heroku.com/buildpacks/heroku/heroku-buildpack-multi-procfile)
