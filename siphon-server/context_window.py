from siphon_server.core.pipeline import SiphonPipeline
from siphon_api.enums.action_type import ActionType
from conduit.sync import Model


videos = """
https://www.youtube.com/watch?v=uv9jAQ_MiK0
https://www.youtube.com/watch?v=BHlIYTDvegM
https://www.youtube.com/watch?v=m2vzoAP1tGo
https://www.youtube.com/watch?v=Ir7iA60QqFQ
https://www.youtube.com/watch?v=BkjAgs8APJE
https://www.youtube.com/watch?v=tg117mBfuJs
https://www.youtube.com/watch?v=oE_ZqcluUZ0
https://www.youtube.com/watch?v=bjalAgAVIkc
https://www.youtube.com/watch?v=mdfOJC-dvfk
https://www.youtube.com/watch?v=OXgg-DnM33I
https://www.youtube.com/watch?v=FoDpTfJfngg&pp=ugUEEgJlbg%3D%3D
https://www.youtube.com/watch?v=j3xkzgiZUCk
https://www.youtube.com/watch?v=CbJSgan4mfQ
https://www.youtube.com/watch?v=ktyPMv54hT0
https://www.youtube.com/watch?v=2t9XrPcAiHg
https://www.youtube.com/watch?v=5CKuiuc5cJM
https://www.youtube.com/watch?v=NvB50FqNurg
""".strip().split("\n")
pcs = []
pipeline = SiphonPipeline()
for video in videos:
    result = pipeline.process(video, action=ActionType.GULP, use_cache=False)
    pcs.append(result)


model = Model("gpt")
# Sort pcs by len(pc.content.text)
pcss = sorted(pcs, key=lambda pc: len(pc.content.text))
print([(len(pc.content.text), pc.source.uri) for pc in pcss])
for pc in pcss:
    print("--------------------------------")
    print("## Video transcript Length:", len(pc.content.text))
    print("## Tokens (per tiktoken): ", str(model.tokenize(pc.content.text)))
    print("## Video URI:", pc.source.uri)
    print("## Vide Summary:", pc.enrichment.summary)
    print("--------------------------------")
