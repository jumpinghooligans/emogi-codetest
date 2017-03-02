from app import app, mongo
import math, time, requests

class RedditApi():

    # how much does a comment count towards a score
    comment_multiplier = 3

    # the api was a bit finnicky
    pages_count = 5
    max_failures = 3

    # crank this up to increase how fast time
    # will decay the score
    time_power = 1.5
    
    # Most of this should all be factored out into models
    def request_listings(self, subreddit=None):

        # how deep should we go?
        pages_count = self.pages_count

        # how many failures?
        max_failures = self.max_failures
        failed_requests = 0

        # setup the subreddit
        if subreddit:
            subreddit = '/r/' + subreddit

        else:
            subreddit = '/'
            
        app.logger.info('requesting %s' % subreddit)

        # reddits paging
        after_token = None

        app.logger.info('requesting %i pages' % pages_count)

        # store all the pages data
        full_listings = []

        # params outside the while so if we end up re-requesting
        # we don't overwrite
        params = {}

        while pages_count > 0 and failed_requests <= max_failures:

            if after_token:
                params['after'] = after_token

            # make the request
            res = requests.get('https://reddit.com/' + subreddit + '.json', params)

            # if we have a valid response
            if res.status_code == requests.codes.ok:

                # grab the children
                children = res.json().get('data', {}).get('children', None)
                after = res.json().get('data', {}).get('after', None)

                # if we have it, append it
                if children:

                    app.logger.info('successfully grabbed %i new listings' % len(children))

                    # token for the next page
                    if after:

                        app.logger.info('grabbed after token: %s' % after)

                        after_token = after

                    full_listings += children

                    # decrement
                    pages_count -= 1

                    # reset failures
                    failed_requests = 0

                    # we're done here, on to the next page
                    continue

            # Any falure above should increase the failed_requests count
            failed_requests += 1

            # increasing sleep time
            sleep_time = failed_requests * 2

            app.logger.error('Request failed: %s, sleeping for %i' % (str(res.json()), sleep_time))

            time.sleep(sleep_time)


        app.logger.info('returning %i total listings' % len(full_listings))

        return full_listings

    # I haven't figured out Python and serialization
    # This is the best I could do in the time allotted
    def get_listings(self, ):

        all_listings = [ listing for listing in mongo.db.listings.find() ]

        for listing in all_listings:
            listing.pop('_id')

        return all_listings

    # Filter out images based on domain or suffix
    def filter_images(self, listings):

        imgur_domains = ['i.imgur.com', 'imgur.com']
        img_suffix = ['png', 'jpg', 'jpeg', 'gif', 'gifv']

        image_listings = []

        for listing in listings:

            listing_data = listing.get('data')

            # Check if its from imgur
            if listing_data.get('domain') in imgur_domains:

                image_listings.append(listing)

            # Check if its ends in an image suffix
            elif listing_data.get('url') in img_suffix:

                image_listings.append(listing)

        return image_listings

    # Calculate our TOP score
    # 
    # This is simply the total points plus
    # our "comment points"
    def top_score(self, listing):

        return listing.get('data').get('score') + self.comment_score(listing)

    # Calculate our POPULAR score
    # 
    # Logarithmic decay applied to total score
    # Comment score
    def hot_score(self, listing):

        # get the age in ms
        created = listing.get('data').get('created_utc')
        age = time.time() - created

        time_decay = age ** self.time_power

        return round((self.top_score(listing) ** 2) / time_decay)

    def comment_score(self, listing):

        return listing.get('data').get('num_comments') * self.comment_multiplier