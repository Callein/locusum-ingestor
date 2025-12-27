#!/bin/bash

echo "Starting Batch Crawl..."

# Array of spiders
SPIDERS=("texas_tribune" "dallas_news" "houston_chronicle" "community_impact")

for spider in "${SPIDERS[@]}"
do
    echo "Running spider: $spider"
    scrapy crawl "$spider"
    echo "---------------------------------"
done

echo "All spiders finished."
