from yt_comments import fetch_comments as fetch_comments_live

def fetch_comments(video_id):
    if not video_id:
        return ["⚠️ No video_id provided"]
    vid, comments = fetch_comments_live(video_id)
    return comments
