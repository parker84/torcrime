# deploying_app_to_beanstalk\\



### To Use AWS EB CLI
1. I setup a user with access to beanstalk
    1. https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#id_users_create_console
2. installed AWS CLI: 
    1. https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-mac.html#cliv2-mac-install-cmd
3. Configured AWS CLI corresponding to that user:
    1. https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html#cli-quick-configuration
4. install and setup EB CLI:
   1. https://docs.amazonaws.cn/en_us/elasticbeanstalk/latest/dg/eb-cli3-install.html
   2. https://docs.amazonaws.cn/en_us/elasticbeanstalk/latest/dg/eb-cli3-configuration.html


### launching the app
- https://docs.amazonaws.cn/en_us/elasticbeanstalk/latest/dg/create-deploy-python-flask.html#python-flask-create-app
- dash specifications: https://medium.com/@austinlasseter/deploying-a-dash-app-with-elastic-beanstalk-console-27a834ebe91d
  - might work in console if we use 3.6?

steps used in dash:
```sh
cd ./visualization
eb init -p python-3.6 tor-crime-app --region ca-central-1
# 3.7 didnt want to work for me
eb init
# Y
eb create tor-crime-app
```

### managing apps:
- go the management console corresponding to that IAM user and be sure to set the region to Canada