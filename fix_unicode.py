import re
p = r"C:\Users\Administrator\WorkBuddy\2026-09-15-14-18-54\naodong-pages\generate.py"
s = open(p, encoding="utf-8").read()
s2 = re.sub(r'\\u\{([0-9A-Fa-f]+)\}', lambda m: '\\U' + m.group(1).zfill(8), s)
open(p, "w", encoding="utf-8").write(s2)
print("已修复 \\u{...} 转义 ->", s2.count("\\U000"), "处")
