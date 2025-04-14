from flask import Flask, request, send_file, render_template_string, after_this_request
import yt_dlp
import uuid
import os
import tempfile

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>Trình tải video</title>
</head>
<body style="font-family: sans-serif; padding: 2rem;">
  <h2>Tải video từ YouTube</h2>
  <form method="get" action="/download">
    <input name="url" type="text" placeholder="Dán link video..." style="width: 400px;" required /><br><br>
    <label>Chọn định dạng:</label>
    <select name="format">
      <option value="mp4">MP4 (video)</option>
      <option value="mp3">MP3 (âm thanh)</option>
    </select><br><br>
    <button type="submit">Tải video</button>
  </form>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download')
def download():
    video_url = request.args.get("url")
    fmt = request.args.get("format", "mp4")
    temp_dir = tempfile.gettempdir()
    temp_id = uuid.uuid4().hex

    if fmt == "mp4":
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': os.path.join(temp_dir, f"{temp_id}.mp4"),
            'quiet': True,
        }
        output_file = f"{temp_id}.mp4"
    elif fmt == "mp3":
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]',
            'outtmpl': os.path.join(temp_dir, f"{temp_id}.m4a"),
            'quiet': True,
        }
        output_file = f"{temp_id}.m4a"
    else:
        return {"error": "Định dạng không hợp lệ"}, 400

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        file_path = os.path.join(temp_dir, output_file)

        @after_this_request
        def cleanup(response):
            try:
                os.remove(file_path)
            except:
                pass
            return response

        return send_file(
            file_path,
            as_attachment=True,
            download_name=output_file.replace(".m4a", ".mp3"),
            mimetype='application/octet-stream'
        )
    except Exception as e:
        return {"error": f"Tải video thất bại: {str(e)}"}, 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
