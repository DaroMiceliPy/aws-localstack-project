# Setting up
Please follow the next steps to setting up the project

### Start containers
In the project folder:

```docker
docker compose up --build
```

### Creating aws resources
 ```terraform
terraform init
```

 ```terraform
terraform apply
```

### Setup connection between airflow and localstack

1. From the `Admin > Connections` menu
2. Click the "+"
3. Add an Amazon Web Services connection with the following settings:

    * Connection Id: aws_localstack
    * Login: test
    * Password: test
    * Extra: `{"host": "http://localstack:4566", "region_name": "us-west-1"}`


# Enjoy!.
The project is ready!.