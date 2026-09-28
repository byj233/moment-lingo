import os
import time

import meilisearch
from dotenv import load_dotenv

import utils

# 从环境变量读取 Meilisearch 配置（见项目根目录 .env），避免把地址和密钥硬编码在代码里
load_dotenv()

client = meilisearch.Client(os.getenv('MEILI_HOST', ''), os.getenv('MEILI_API_KEY', ''))


def create():
    index_name = 'vocabulary'
    client.create_index(index_name, {
        'primaryKey': 'vocabularyId'
    })

    data = utils.read_json('vocabulary.json')

    n_data = []
    for item in data:
        core = ''
        if item.get('type') == 'word':
            core = item.get('word')
            weight = 2 + len(item.get('tags'))
        elif item.get('type') == 'phrase':
            core = item.get('word')
            weight = 1 + len(item.get('tags'))
        else:
            weight = 0

        n_data.append({
            'vocabularyId': item.get('vocabularyId'),
            'word': item.get('word'),
            "core": core,
            'translation': item.get('translation'),
            'explanation': item.get('explanation'),
            'weight': weight,
        })

    # 定义每批插入的数量
    batch_size = 500000
    total = len(n_data)

    # 计算总批次数
    total_batches = (total + batch_size - 1) // batch_size
    print(f"总共需要插入 {total} 条数据，分为 {total_batches} 批处理")

    # 分批插入数据
    for i in range(total_batches):
        # 计算当前批次的起始和结束索引
        start = i * batch_size
        end = start + batch_size
        batch_data = n_data[start:end]

        print(f"正在插入第 {i + 1}/{total_batches} 批数据，共 {len(batch_data)} 条")

        # 插入当前批次数据
        task = client.index(index_name).add_documents(batch_data)

        # 轮询任务状态，直到任务完成
        while True:
            task_status = client.get_task(task.task_uid)
            if task_status.status == 'succeeded':
                print(f"第 {i + 1} 批插入成功！\n")
                break
            else:
                # 任务未完成，等待1秒后继续查询
                time.sleep(1)

    print("所有数据插入完成")


def delete(index: str):
    client.delete_index(index)


def search():
    index = client.index('vocabulary')
    res = index.search('abandon', {
        'matchingStrategy': 'last',
        'limit': 10
    })

    for item in res.get('hits'):
        print(item)
        print('-------------')
    # print(res.get('hits'))


def sort_setting():
    index = client.index('vocabulary')
    res = index.update_settings({
        "sortableAttributes": ["weight"]
    })

    print(res)


def rank_setting():
    index = client.index('vocabulary')
    res = index.update_settings({
        "rankingRules": [
            "sort",
            "attribute",
            "exactness",
            "words",
            "typo",
            "proximity"
        ],
    })

    print(res)

def filter_ranking():
    index = client.index('vocabulary')
    res = index.update_settings({
        "filterableAttributes": ["word"]
    })

    print(res)


if __name__ == "__main__":
    # test()
    # create()
    # sort_setting()
    # rank_setting()
    filter_ranking()
    # search()
    # delete('vocabulary')
