from app import app, mongo
from .models import RedditApi
from flask import request, redirect, jsonify, render_template, make_response

@app.route('/')
def index():
    # get the thing    
    r = RedditApi()

    # get our frontpage listings
    image_listings = r.get_image_listings()

    # get trending subreddits
    trending_subreddits = r.aggregate_subreddits(image_listings)

    return render_template('list_listings.html', 
        listings=image_listings,
        trending_subreddits=trending_subreddits
    )

@app.route('/trending')
def trending_subreddits():
    r = RedditApi()

    frontpage = r.get_image_listings()

    trending_subreddits = r.aggregate_subreddits(frontpage)

    return jsonify(trending_subreddits)

@app.route('/listings')
def list_frontpage():
    r = RedditApi()

    frontpage = r.get_listings()

    return jsonify(frontpage)

@app.route('/listings/images')
def list_images():
    r = RedditApi()

    # i'm not really good with python ObjectIds were really
    # causing issues
    frontpage = r.get_image_listings()

    # filter down to only imgur listings
    image_listings = filter_images(frontpage)

    return jsonify(image_listings)

@app.route('/listings/refresh')
def refresh_listings():
    r = RedditApi()

    # grab our front page listings
    frontpage = r.request_listings()
    app.logger.info('found %i frontpage listings', len(frontpage))

    # clear out our listings
    mongo.db.listings.remove({})

    for listing in frontpage:

        # calculate top score
        listing['custom_top'] = r.top_score(listing)

        # calculate hot score
        listing['custom_hot'] = r.hot_score(listing)

        mongo.db.listings.insert_one(listing)

        # jsonify throws a error with ObjectIds
        listing.pop('_id', None)

    return redirect(request.referrer or '/listings')
