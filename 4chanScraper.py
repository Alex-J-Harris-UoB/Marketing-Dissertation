import requests
import json
import os
import html

def cleanup(l):
    l = l.replace("<br>", "\n")
    l = l.replace("<wbr>", "")
    l = l.replace("</span>", "")
    l = l.replace("<span class=\"quote\">>", "")
    l = l.replace("\n\n", "\n")
    l = l.replace("\n\n\n", "\n")
    return l

def get_posts():
    lines = []
    url = "https://a.4cdn.org/pol/catalog.json"
    req = requests.get(url)
    req_json = json.loads(req.text)
    for index in range(len(req_json)):
        threads = req_json[index]["threads"]
        for i in range(len(threads)):
            if "sub" in threads[i]:
                sub = html.unescape(threads[i]["sub"])
                lines.append("POST: " + sub + "\n")
            if "com" in threads[i]:
                com = html.unescape(threads[i]["com"])
                lines.append(com + "\n")
            if "last_replies" in threads[i]:
                for reps in range(len(threads[i]["last_replies"])):
                    reply = threads[i]["last_replies"][reps]
                    if 'com' in reply:
                        r = html.unescape(reply['com'])
                        if "<br>" in r:
                            r = r.split("<br>")
                            r = html.unescape(r[len(r) - 1])
                        lines.append("REPLY: " + r + "\n")
    lines_clean = [cleanup(x) for x in lines]
    print(len(lines_clean))
    archive = open("archive May 2.txt", mode="a+", encoding="utf-8")
    archive.writelines(lines_clean)
    archive.close()

get_posts()
