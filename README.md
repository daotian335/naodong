# 每日胡说 · 静态 SEO 版（Cloudflare Pages 部署）

零成本、零 API、可被搜索引擎收录、每天自动更新、不关站。

## 文件说明
- `generate.py` —— 生成器：预生成真实 HTML 文章页 + 首页 + sitemap，每篇带结构化数据，爬虫可读。
- `posts.json` —— 累积的文章数据（GitHub Actions 每天往里加新文，历史永久保留）。
- `dist/` —— 生成出来的静态站，部署的就是这个目录。
- `.github/workflows/deploy.yml` —— 每天北京时间 08:00 自动生成 + 部署到 Cloudflare Pages。

## 你只要做 4 步（都不花钱）

### 第 1 步：在 GitHub 建一个空仓库
1. 打开 github.com，点右上角 **+ → New repository**
2. 仓库名填 `naodong`（随便起也行）
3. 选 **Public**（或 Private 也行，Actions 免费）
4. 不要勾 "Add README"，直接 **Create repository**

### 第 2 步：把本文件夹所有文件传上去
最省事：装 **GitHub Desktop**（desktop.github.com，图形界面，不用记命令）
1. 登录后选 **File → Clone repository** 把你刚建的仓库克隆到电脑
2. 把 `naodong-pages` 里的全部文件（generate.py、posts.json、dist/、.github/）**复制进**那个仓库文件夹
3. 左上角填个说明，点 **Commit → Push origin**
> 嫌麻烦也可以把文件夹压缩发我，我帮你推（需要你给我一个 GitHub 临时令牌，用完即删）。

### 第 3 步：Cloudflare 上建 Pages 项目并授权
1. 打开 dash.cloudflare.com → **Workers 和 Pages → 创建 → Pages → 连接 GitHub**
2. 授权 Cloudflare 访问你的 GitHub，选 `naodong` 仓库
3. 项目名填 `naodong`，**构建命令留空，输出目录填 `dist`**（其实用 Actions 部署，这里只是建项目）
4. 建好后，去 **设置 → 环境变量/Secrets**，加两个：
   - `CLOUDFLARE_API_TOKEN`（在 dash.cloudflare.com/profile/api-tokens 建，权限勾 Pages:Edit）
   - `CLOUDFLARE_ACCOUNT_ID`（dash 右下角 "账户 ID"）
5. 去项目 **自定义域**，绑 `naodong.tttttttttt.top`

### 第 4 步：把域名 NS 切到 Cloudflare
1. 在 Cloudflare 添加站点 `naodong.tttttttttt.top`，它会给你两个 NS 地址
2. 去你注册域名的地方（Porkbun/Namesilo 等），把 NS 改成 Cloudflare 给的那两个
3. 等几分钟生效，浏览器开 `https://naodong.tttttttttt.top` 即可

## 之后就全自动了
- 每天北京时间 08:00，GitHub Actions 自动生成新内容 + 部署，**不开电脑、不打开 AI 也更新**
- 搜索引擎抓到真实 HTML → 收录 → 更多人看到
- Cloudflare Pages **不考核访问量，永不因没人看而关站**

## 变现位填真实信息
打开 `generate.py` 顶部的 `SITE_CONFIG`（在 INDEX_TPL 的脚本里），把：
- `wxQr` 填微信赞赏码图片地址（或内联 base64）
- `afdian` 填你的爱发电主页
- `douyin` / `weishi` 填你的抖音号 / 视频号
改完再 push 一次即生效。

## 本地预览 / 手动生成
```
python generate.py        # 生成 dist/
# 用任意静态服务器打开 dist/ 即可看
```
