import json
from datetime import datetime

# 读取两个文件
with open('../us_and_uk_voices.json', 'r', encoding='utf-8') as f:
    source_data = json.load(f)

with open('../voice.json', 'r', encoding='utf-8') as f:
    current_data = json.load(f)

# 从 source_data 提取 edge-tts 数据
source_voices = {}
for region in ['us', 'uk']:
    for voice in source_data[region]:
        voice_key = voice['ShortName']
        source_voices[voice_key] = {
            'voice_name': voice['ShortName'].split('-')[2].replace('Neural', '').replace('Multilingual', ''),
            'voice_key': voice_key,
            'type': region,
            'model': 'edge-tts',
            'gender': voice.get('Gender', ''),
            'voice_tag': voice.get('VoiceTag', {})
        }

# 从 current_data 提取 edge-tts 数据
current_voices = {}
for voice in current_data:
    if voice['model'] == 'edge-tts':
        current_voices[voice['voice_key']] = voice

# 找出新增的语音
new_voices = []
for key, voice in source_voices.items():
    if key not in current_voices:
        new_voices.append(voice)

# 找出删除的语音
deleted_voices = []
for key, voice in current_voices.items():
    if key not in source_voices:
        deleted_voices.append(voice)

print("=" * 80)
print("新增的 edge-tts 语音 (us_and_uk_voices.json 中有但 voice.json 中没有):")
print("=" * 80)
for voice in new_voices:
    print(f"- {voice['voice_name']} ({voice['voice_key']}) - {voice['type'].upper()}")

print("\n" + "=" * 80)
print("已删除的 edge-tts 语音 (voice.json 中有但 us_and_uk_voices.json 中没有):")
print("=" * 80)
for voice in deleted_voices:
    print(f"- {voice['voice_name']} ({voice['voice_key']}) - {voice['type'].upper()}")

# 生成新的数据格式（用于 voice.json）
print("\n" + "=" * 80)
print("建议的 voice.json 更新格式（新增部分）：")
print("=" * 80)

# 查找当前最大的 voice_id
max_id = max([v['voice_id'] for v in current_data]) if current_data else 0

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

for i, voice in enumerate(new_voices, 1):
    # 根据性别设置标签
    tags = []
    if voice['gender'] == 'Female':
        tags.append('女性')
    elif voice['gender'] == 'Male':
        tags.append('男性')
    
    # 尝试从 VoiceTag 获取更多信息
    personalities = voice.get('voice_tag', {}).get('VoicePersonalities', [])
    if personalities:
        tags.append(personalities[0])
    
    new_entry = {
        "voice_id": max_id + i,
        "voice_name": voice['voice_name'],
        "voice_key": voice['voice_key'],
        "type": voice['type'],
        "model": voice['model'],
        "tags": tags,
        "weight": 0,
        "created_at": now,
        "updated_at": now
    }
    print(json.dumps(new_entry, ensure_ascii=False, indent=2))
    if i < len(new_voices):
        print(",")
