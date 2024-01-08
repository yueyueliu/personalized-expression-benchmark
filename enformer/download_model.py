import tensorflow_hub as hub
import urllib.request

# TF Hub 模型的 URL
tfhub_url = 'https://tfhub.dev/deepmind/enformer/1'

# 下载模型
model = hub.load(tfhub_url)

# 保存模型到本地
destination = './model'
model.save(destination)
