import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key
API_KEY = "AIzaSyDnEAoBQYpAnbrO4M_vd90nlWdmr9rk9CM"  
Youtube_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Streamlit App Title
st.title("YouTube Viral Topics Tool")

# Input Fields
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)

# List of broader keywords related to Diddy's current situation
keywords = [
    "Diddy trial",
    "Sean Combs trial",
    "Diddy sex trafficking",
    "Sean Combs sex trafficking",
    "Diddy racketeering",
    "Diddy allegations",
    "Cassie testimony",
    "Diddy court",
    "Diddy legal",
    "Diddy latest news",
    "Diddy updates",
    "Diddy witness",
    "Diddy assault video",
    "Diddy hotel video",
    "Diddy former assistant testimony",
    "Diddy Mia testimony",
    "Diddy Bryana Bongolan",
    "Diddy legal proceedings",
    "Diddy criminal charges",
    "Diddy lawsuit",
    "Diddy accusations",
    "Diddy abuse",
    "Diddy controversies",
    "Diddy P. Diddy",
    "Puff Daddy trial",
    "Bad Boy Records scandal",
    "Diddy 'freak off'",
    "Diddy Dangle Balcony",
    "Diddy Bribe Security",
    "Diddy Forensic Video Expert",
    "Diddy Intercontinental Hotel",
    "Diddy A-list names",
    "Diddy Trump pardon"
]

# Fetch Data Button
if st.button("Fetch Data"):
    try:
        # Calculate date range
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        # Iterate over the list of keywords
        for keyword in keywords:
            st.write(f"Searching for keyword: {keyword}")

            # Define search parameters
            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5, # You might want to increase this for more results per keyword, but be mindful of API quota
                "key": API_KEY,
            }

            # Fetch video data
            response = requests.get(Youtube_URL, params=search_params)
            data = response.json()

            # Check if "items" key exists
            if "items" not in data or not data["items"]:
                st.warning(f"No videos found for keyword: {keyword}")
                continue

            videos = data["items"]
            video_ids = [video["id"]["videoId"] for video in videos if "id" in video and "videoId" in video["id"]]
            channel_ids = [video["snippet"]["channelId"] for video in videos if "snippet" in video and "channelId" in video["snippet"]]

            if not video_ids or not channel_ids:
                st.warning(f"Skipping keyword: {keyword} due to missing video/channel data.")
                continue

            # Fetch video statistics
            stats_params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()

            if "items" not in stats_data or not stats_data["items"]:
                st.warning(f"Failed to fetch video statistics for keyword: {keyword}")
                continue

            # Fetch channel statistics
            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()

            if "items" not in channel_data or not channel_data["items"]:
                st.warning(f"Failed to fetch channel statistics for keyword: {keyword}")
                continue

            stats_items = stats_data["items"]
            channels_items = channel_data["items"]

            # Create dictionaries for easier lookup
            video_stats_map = {item['id']: item['statistics'] for item in stats_items}
            channel_stats_map = {item['id']: item['statistics'] for item in channels_items}


            # Collect results
            for video_item in videos:
                video_id = video_item["id"]["videoId"]
                channel_id = video_item["snippet"]["channelId"]

                title = video_item["snippet"].get("title", "N/A")
                description = video_item["snippet"].get("description", "")[:200]
                video_url = f"https://www.youtube.com/watch?v={video_id}" # Corrected YouTube URL format

                # Get statistics using the maps
                video_statistics = video_stats_map.get(video_id, {})
                channel_statistics = channel_stats_map.get(channel_id, {})

                views = int(video_statistics.get("viewCount", 0))
                subs = int(channel_statistics.get("subscriberCount", 0))

                # Only include channels with fewer than 3,000 subscribers
                if subs < 3000:
                    all_results.append({
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Views": views,
                        "Subscribers": subs
                    })

        # Display results
        if all_results:
            # Sort results by views (descending) before displaying
            all_results.sort(key=lambda x: x["Views"], reverse=True)

            st.success(f"Found {len(all_results)} results across all keywords!")
            for result in all_results:
                st.markdown(
                    f"**Title:** {result['Title']} \n"
                    f"**Description:** {result['Description']} \n"
                    f"**URL:** [Watch Video]({result['URL']}) \n"
                    f"**Views:** {result['Views']:,} \n" # Format views with commas
                    f"**Subscribers:** {result['Subscribers']:,}" # Format subscribers with commas
                )
                st.write("---")
        else:
            st.warning("No results found for channels with fewer than 3,000 subscribers.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
