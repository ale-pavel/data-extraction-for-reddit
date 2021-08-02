# data-extraction-homework

Homework:

Build a strategy to download and store all reddit posts and comments (including upvotes and downvotes) for a given subreddit (eg reddit.com/r/sanfrancisco).

Write down an executable script in any language to run your strategy.

Storage of your choice among Redis, MongoDB, or Mysql. Up to you choose which one you think fits best and/or you are more familiar with.


## Installation
Packages needed include pymongo and requests. Todo requirements.txt. docker-engine must be installed, along with docker-compose and mongosh/mongo.

Credentials are also needed to run this project, in particular:
- Reddit username/password into ```secret.txt```
- Reddit Dev Keys into ```api_key.txt```

## Prerequisites
Run the following commands to create the db needed for the job:

    docker-compose up -d
    docker exec -it mongodb bash
    mongo
    use db

Then start the job with:

    ./run_job.sh

After executing the job, clean MongoDB data (removing the entire db) by:

    ./mongo_shell.sh
    use db
    db.dropDatabase()

This allows to avoid duplicates problems, which have not been handled at all in the code.

Remember to stop the Docker containers with:

    docker-compose down
