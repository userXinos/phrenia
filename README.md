# Phrenia

chatbot 

### Run locally

<details>
  <summary>Prepare environment with conda</summary>

  ```bash
  conda create -y python=3.12 -n phrenia
  conda activate phrenia
  ```
</details>

```bash
pip install -r requirements.lock.txt
cp simple.config.json config.json
vim config.json
python main.py
```

[Discord Developer Portal](https://discord.com/developers/applications)