# Hướng dẫn

- Clone repo
```bash
git clone https://github.com/hari-huynh/vietnam-speech-diarization.git
```

- Cài đặt những thư viện cần thiết
```bash
pip install -r requirements.txt
```
- Chỉnh sửa những config của Label Studio trong file `config.yaml`
```yaml
label-studio:
  url: ...
  api-token: ...
  db-and-media-dir: ...
  project-id: ...
```

- Thêm những file `.mp3` vào thư mục `data`
- Chạy file `upload.py`
```bash
python upload.py
```
