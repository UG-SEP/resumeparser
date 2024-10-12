# Resume Parser

A Django-based resume parsing system that handles resume uploads, processes them asynchronously using Celery, and stores parsed data in MongoDB.

## Getting Started

Follow these steps to set up and run the project on your local machine.

### 1. Clone the Repository

Fork and clone the repository to your local machine

### 2. Install Dependencies
```bash
cd resumeparser

pip install -r requirements.txt
```

### 3.  Install and Setup MongoDB

- Download MongoDB from the official site.
- Follow the installation instructions for MongoDB.
- After installation, run MongoDB using the command:
- Create a database

 ### 4. Setup Environment Variables

 ```bash
DEBUG=TRUE
MONGODB_URI=mongodb://localhost:27017/
MONGODB_NAME=DATABASE_NAME_HERE
API_KEY=OPENAI_API_KEY
SERVER_URL=SERVER_URL_HERE
```

### 5.  Install and Setup Redis

- [Download Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-mac-os/) for Mac using HomeBrew
- Run the command `redis-server` on the shell/cmd
- Check for whether the `redis server` is working or not using `redis-cli ping` it will output PONG

### 6. Run LocalHost and Celery Worker

- Open the project and run the following command on two different terminal
```bash
  py manage.py runserver
  celery -A resumeparser worker --loglevel=info --pool=eventlet

  ```
### 7. Using the API

You can interact with the resume parser API using Postman:

1. Open Postman.
2. Create a new POST request.
3. Set the URL to `http://127.0.0.1:8000/upload/`
4. In the Body tab, select form-data, set the key to `resumes`, and upload your PDF file.
5. Send the request.

You should receive a response indicating the status of your resume parsing request.




