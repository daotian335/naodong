# 一次性补种：生成最近 31 天 ×12 篇，让 SEO 站立刻铺满新主题内容
import generate as g
from datetime import date, timedelta

posts = []
for i in range(31, 0, -1):
    d = date.today() - timedelta(days=i)
    posts += g.gen_day(d, 12)
posts += g.gen_day(date.today(), 12)
g.save_all(posts)
g.build(posts)
print("已补种 %d 篇文章（最近 31 天）" % len(posts))
