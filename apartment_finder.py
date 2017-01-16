from craigslist import CraigslistHousing
from slackclient import SlackClient
from coords import *
import math
import json

CONFIG_FILE = 'config.json'

class Config:
    def __init__(self, site, category, area, filters, num_listings_to_scrape):
        self.site = site
        self.category = category
        self.area = area
        self.filters = filtersself.num_listings_to_scrape = num_listings_to_scrape

class ListingResult:
    def __init__(self, result):
        self.cl_result = result
        self.area = ""
        self.cta_dist = float('NaN')
        self.cta_station = "???"

def in_box(coords, box):
    if not coords or not box:
        return False

    if box[0][0] <= coords[0] <= box[1][0] and box[0][1] <= coords[1] <= box[1][1]:
        return True
    return False

def get_area(result):
    geotag = result["geotag"]
    area_found = False
    area = ""
    for area, coords in NEIGHBORHOOD_COORDS.items():
        if in_box(geotag, coords):
            return area
    
def get_reported_area(result):
    location = result["where"]
    for area, coords in NEIGHBORHOOD_COORDS.iteritems():
        if area and coords:
            if area.lower() in location.lower():
                return area
    
def set_area(dec_result, area, reported_area):
    if area:
        dec_result.area = area
    elif reported_area:
        dec_result.area = reported_area
    
def coord_distance(x1,y1,x2,y2):
    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return dist

def km_to_mi(km):
    TO_MILE_CONVERSION_FACTOR = 0.621371
    return CONVERSION_FACTOR * km
     
def set_cta_dist(dec_result):
    near_cta = False
    cta_dist = float('NaN')
    cta_name = "" 
    MAX_TRANSIT_DIST_KM = 0.804672 #half mile

    geotag = dec_result.cl_result["geotag"]
    if not geotag:
        return
    for station, coords in CTA_STATIONS.items():
        dist = coord_distance(coords[0], coords[1], geotag[0], geotag[1])
        if dist < MAX_TRANSIT_DIST_KM:
            if (math.isnan(cta_dist) or dist < cta_dist):
                cta_name = station
                near_cta = True
                cta_dist = dist

    dec_result.cta_dist = km_to_mi(cta_dist)
    dec_result.cta_station = cta_name
    
def load_listings_from_craigslist(craigslist, num_listings_to_scrape):
    results = craigslist.get_results(sort_by='newest', geotagged=True, limit=num_listings_to_scrape)
    listing_results = []
    for result in results:
        dec_result = ListingResult(result)
        set_area(dec_result, get_area(result), get_reported_area(result))
        set_cta_dist(dec_result)

        if not is_eligible_listing(dec_result):
            continue
        else:
            listing_results.append(dec_result)
    return listing_results
   
def is_blacklist_name(listing_name):
    BLACKLIST = ['studio', '1 bedroom' '1 br', 'one bedroom', 'one br', '1br', '1bedroom']
    for entry in BLACKLIST:
        if entry.lower() in listing_name.lower():
            return True
    return False;
    
def is_eligible_listing(listing):
        return listing.area and not is_blacklist_name(listing.cl_result["name"])

def output_to_slack(listing_results, slack_token, slack_channel):
    sc = SlackClient(slack_token)
    for dec_result in listing_results:
        result = dec_result.cl_result

        desc = "{0} | {1} | {2}: {3:.2f} mi | {4} | <{5}>".format(
                        result["price"], 
                        dec_result.area, 
                        dec_result.cta_station, 
                        dec_result.cta_dist, 
                        result["name"], 
                        result["url"])
        sc.api_call(
            "chat.postMessage", channel=slack_channel, text=desc, username='pybot', icon_emoji=':robot_face:'
        )
    
def main(config, slack_token, slack_channel):
    craigslist = CraigslistHousing (site = config.site, area = config.area, category = config.category, filters = config.filters )
    results = load_listings_from_craigslist(craigslist, num_listings_to_scrape = config.num_listings_to_scrape)
    output_to_slack(results, slack_token, slack_channel)
    
if __name__ == '__main__':
    with open(CONFIG_FILE) as config_file:
        data = json.load(config_file)
        slack_token = data["slack"]["token"]
        slack_channel = data["slack"]["channel"]
        config = Config(data["craigslist"]["site"], data["craigslist"]["category"], data["craigslist"]["area"], data["filters"], data["num_listings_to_scrape"])
    main(config, slack_token, slack_channel)