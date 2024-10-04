# Resume Parser

### Steps to run project into your local machine

- Clone the project
- download all the dependencies mentioned in the requirement.txt
- Create a mongo db database
- Setup the celery
- Run the celery worker using the command => `celery -A resumeparser worker --loglevel=info --pool=eventlet`
Reason of using eventlet is to handle concurrency effectively
- Run the django project 
- Call the API using postman with POST and name the value file and send the pdf file
