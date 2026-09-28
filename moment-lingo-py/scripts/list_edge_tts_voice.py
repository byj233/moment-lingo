import json

import edge_tts


async def list_voices():
    voices = await edge_tts.list_voices()
    return voices


def list_us_and_uk_voices(voices: list):
    res = {
        "us": [],
        "uk": []
    }

    for item in voices:
        if item['Locale'] == "en-US":
            res["us"].append(item)
        elif item['Locale'] == "en-GB":
            res["uk"].append(item)

    with open("../us_and_uk_voices.json", "w") as f:
        json.dump(res, f, indent=4)


if __name__ == "__main__":
    import asyncio

    voices = asyncio.run(list_voices())
    list_us_and_uk_voices(voices)
