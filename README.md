# spiketrap-homework

Homework:

Build a strategy to download and store all reddit posts and comments (including upvotes and downvotes) for a given subreddit (eg reddit.com/r/sanfrancisco).

Write down an executable script in any language to run your strategy.

Storage of your choice among Redis, MongoDB, or Mysql. Up to you choose which one you think fits best and/or you are more familiar with.


## Installation
Packages needed include pymongo and requests. Todo requirements.txt.

## Prerequisites
Run the following commands to create the db needed for the job:

    docker-compose up -d
    docker exec -it mongodb bash
    mongo
    use db

Then start the job with:

    ./run_job.sh

Remember to stop the Docker containers with:

    docker-compose down
