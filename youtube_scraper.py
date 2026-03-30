from playwright.sync_api import sync_playwright
import csv
import boto3

def scrape_youtube():
    with sync_playwright() as p:   # ✅ Proper lifecycle management
        browser = p.chromium.launch(headless=True)  # ✅ Use True for container
        page = browser.new_page()

        # Go directly to search results (faster + avoids UI interaction)
        page.goto(
            "https://www.youtube.com/results?search_query=tamil+songs",
            wait_until="domcontentloaded"
        )

        # Wait for videos to load
        page.wait_for_selector("ytd-video-renderer", timeout=30000)

        # Scroll a bit to load more results
        page.mouse.wheel(0, 2000)
        page.wait_for_timeout(2000)

        video_elements = page.query_selector_all("ytd-video-renderer")

        videos = []

        for element in video_elements[:10]:
            title_el = element.query_selector("#video-title")
            channel_el = element.query_selector("ytd-channel-name a")
            views_el = element.query_selector("#metadata-line span:nth-child(1)")

            title = title_el.inner_text().strip() if title_el else "N/A"
            channel = channel_el.inner_text().strip() if channel_el else "N/A"
            views = views_el.inner_text().strip() if views_el else "N/A"

            videos.append({
                "title": title,
                "channel": channel,
                "views": views
            })

            print(f"✅ {title} | {channel} | {views}")

        browser.close()
        # return videos
    with open("youtube_videos.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "channel", "views"])
            writer.writeheader()
            writer.writerows(videos)

    print(f"\nSaved {len(videos)} videos to youtube_videos.csv")


if __name__ == "__main__":
    scrape_youtube()

# import csv
# from playwright.sync_api import sync_playwright
# import boto3


# def scrape_youtube():
#         p = sync_playwright()
#         browser = p.chromium.launch(headless=False)
#         page = browser.new_page()
#         page.goto("https://www.youtube.com", wait_until="networkidle")
#         page.wait_for_timeout(3000)

#         # Click the search input and type the query
#         search_box = page.wait_for_selector(
#             "input.ytSearchboxComponentInput", timeout=15000
#         )
#         search_box.click()
#         page.wait_for_timeout(500)
#         search_box.fill("tamil songs")

#         # Click the search button
#         page.click("button.ytSearchboxComponentSearchButton")
#         print("Searched for 'tamil songs'")

#         # Wait for search results to load
#         page.wait_for_selector("ytd-video-renderer", timeout=30000)
#         page.mouse.wheel(0, 1000)
#         page.wait_for_timeout(3000)

#         # Search results use ytd-video-renderer
#         video_elements = page.query_selector_all("ytd-video-renderer")

#         videos = []
#         for element in video_elements[:10]:
#             title_el = element.query_selector("#video-title")
#             channel_el = element.query_selector(
#                 "ytd-channel-name #text-container yt-formatted-string a"
#             )
#             views_el = element.query_selector(
#                 "#metadata-line span.inline-metadata-item"
#             )

#             title = title_el.inner_text().strip() if title_el else "N/A"
#             channel = channel_el.inner_text().strip() if channel_el else "N/A"
#             views = views_el.inner_text().strip() if views_el else "N/A"

#             videos.append({"title": title, "channel": channel, "views": views})
#             print(f"Scraped: {title}")

#         browser.close()

#     # Write to CSV
#     # with open("youtube_videos.csv", "w", newline="", encoding="utf-8") as f:
#     #     writer = csv.DictWriter(f, fieldnames=["title", "channel", "views"])
#     #     writer.writeheader()
#     #     writer.writerows(videos)

#     # print(f"\nSaved {len(videos)} videos to youtube_videos.csv")
#     # s3 = boto.client('s3')


# if __name__ == "__main__":
#     scrape_youtube()

# import csv
# from playwright.sync_api import sync_playwright
# import boto3


# def scrape_youtube():
#         p = sync_playwright()
#         browser = p.chromium.launch(headless=False)
#         page = browser.new_page()
#         page.goto("https://www.youtube.com", wait_until="networkidle")
#         page.wait_for_timeout(3000)

#         # Click the search input and type the query
#         search_box = page.wait_for_selector(
#             "input.ytSearchboxComponentInput", timeout=15000
#         )
#         search_box.click()
#         page.wait_for_timeout(500)
#         search_box.fill("tamil songs")

#         # Click the search button
#         page.click("button.ytSearchboxComponentSearchButton")
#         print("Searched for 'tamil songs'")

#         # Wait for search results to load
#         page.wait_for_selector("ytd-video-renderer", timeout=30000)
#         page.mouse.wheel(0, 1000)
#         page.wait_for_timeout(3000)

#         # Search results use ytd-video-renderer
#         video_elements = page.query_selector_all("ytd-video-renderer")

#         videos = []
#         for element in video_elements[:10]:
#             title_el = element.query_selector("#video-title")
#             channel_el = element.query_selector(
#                 "ytd-channel-name #text-container yt-formatted-string a"
#             )
#             views_el = element.query_selector(
#                 "#metadata-line span.inline-metadata-item"
#             )

#             title = title_el.inner_text().strip() if title_el else "N/A"
#             channel = channel_el.inner_text().strip() if channel_el else "N/A"
#             views = views_el.inner_text().strip() if views_el else "N/A"

#             videos.append({"title": title, "channel": channel, "views": views})
#             print(f"Scraped: {title}")

#         browser.close()

#     # Write to CSV
#     # with open("youtube_videos.csv", "w", newline="", encoding="utf-8") as f:
#     #     writer = csv.DictWriter(f, fieldnames=["title", "channel", "views"])
#     #     writer.writeheader()
#     #     writer.writerows(videos)

#     # print(f"\nSaved {len(videos)} videos to youtube_videos.csv")
#     # s3 = boto.client('s3')


# if __name__ == "__main__":
#     scrape_youtube()