# emogi-codetest
I put this together quicking to scrape a few pages from the frontpage of reddit, store it in mongo and provide alternative scores for sorting.

It generates out a simple table with some basic data and the new scores, you must explicity refresh the data in the DB by either hitting `/listings/refresh` or clicking the refresh link on the front page.

# Running this thing
The best way to run this is with docker-compose. A simple `docker-compose up --build` will rebuild and start a Python and Mongo container. You could run it on your local as well as long as the dependencies in `docker/pip.txt` are met

# Requirements
All listings that are not images (imgur domain or valid image suffix) are filtered out.

Generates custom top and hot scores. I don't have much experience in weighting algorithms, so these are very simple scores. Top is essentially the given reddit score, with additional weight given to comments, while Hot is the same with additional weight on age of the post.  As a post ages, the potential score decreases.

> Weaknesses in these scores:
> - It would have been very interesting to work with reddit's true data, they no longer provide Up's and Down's and rather just a net score. It would be cool to figure out a way to balance 1000up/900down vs 100up/0down (same score, very different postings)
> - Using comment count in scoring has inherint weaknesses in vote rigging. Given more time I think it would be interesting to pull comments, generate top or hot scores for each one, and then use that as a factor in the listing score. Listings with quality comments and discussions should be given precedence over those with just a large number of comments 

REST API
> There wasn't much to do here
> - GET requests on `/listings` return already processed listings
> - GET requests on `/listings/refresh` will pull, process and store a new set of data
> - GET requests on `/trending` will return aggregated count, hot and top scores for the current dataset
> I wanted to add params to the refresh for directing to a specific subreddit or controlling the page depth (default is 5)

Index page
> This was just a really quick way to visualize what was being stored in the DB. I dropped jQuery/dataTables on for easy sorting/paging on the frontend. Definitely not a scalable solution but it is what it is
