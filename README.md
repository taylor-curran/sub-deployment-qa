# sub-deployment-qa

`pip install prefect prefect-aws prefect-kubernetes python-dotenv`

`.env`

```
AWS_ACCESS_KEY_ID="<replace>"
AWS_SECRET_ACCESS_KEY="<replace>"
```

`python my_blocks.py`

`prefect deploy --all`

`prefect deployment run task-wrapped-deployments/task-wrapped-k8s --param sleep_time_subflows=70`


https://hub.docker.com/repository/docker/taycurran/task-wrapped-k8s/general