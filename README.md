# Long-Task
Atlan Challenge


## Challenge Statement

We want to offer an implementation through which the user can stop the long-running task at any given point in time, and can choose to resume or terminate it. This will ensure that the resources like compute/memory/storage/time are used efficiently at our end, and do not go into processing tasks that have already been stopped (and then to roll back the work done post the stop-action)

## Functionalities

- **Upload a CSV File** A dummy CSV file can be uploaded to the server.
- **Download/Export** Any database table can be exported as a CSV file.
  Following operations are available in both upload/download.
- `Pause` Pauses the upload/download.
- `Resume` Resumes the upload/download.
- `Terminate` Terminates/Rollbacks the upload/download.

# Implementation

### Upload
Rows are constantly being read from **sample_data.csv** and stored in the database by a background process (celery worker). Each process has a unique *task_name* value associated with it. The *task_name* together with *user_id* (associated with a user) can be used to perform the following operations on a running upload process
	- Pause
	- Resume
	- See Progress
	- Terminate

### Download/Export

- A database table from the server (which was previously created by an upload task) can be exported as a CSV file. This export/download process has the **same** *task_name* & *user_id* associated with it which was previously used to create this table (by some upload process). The *task_name* together with *user_id* (associated with each user) can be used to perform the following operations on a running download/export process
	- Pause
	- Resume
	- See Progress
	- Terminate

(Redis is used to store the state of a process. A running process stops if its corresponding task_status is set to "pause" in the redis store. Similarly, a task is resumed by changing the task_status to "run". The task_status also stores some additional data such as progress of the task as well as last processed row)


## Techstack

- **Framework** - Django
- **Database** - PostgreSQL + Redis
- **Language** - Python

## ⬇️ Run with docker-compose

```
# clone the repository to your local machine
$ git clone https://github.com/abhi204/Long-Task.git

# Run
$ docker-compose up -d --build

# Then Run
$ sudo docker-compose up

# Visit http://localhost:8000/ in your browser
```







## API Endpoints

| METHODS |      ENDPOINTS      |                                       DESCRIPTION |
| :-------------- | :-----------------: | ------------------------------------------------: |
| POST            |    /upload/start    |                      Start uploading the **sample_data.csv** File |
| POST            |    /upload/pause    |                                  Pause the upload |
| POST            |   /upload/resume    |                                 Resume the upload |
| POST            |  /upload/terminate  |                              Terminate the upload |
| POST             |  /upload/progress   |               Get the percentage upload completion |
| POST            |   /download/start   | Start downloading/exporting from DB into CSV file |
| POST            |   /download/pause   |                                Pause the download |
| POST            |  /download/resume   |                               Resume the download |
| POST            | /download/terminate |                            Terminate the download |
| POST            | /download/progress  |             Get the percentage download completion \ Get download link for exported csv file |

## [View sample requests](https://www.postman.com/collections/0cf41e8e8160c2b331df)
