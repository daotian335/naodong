#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日胡说 · 静态 SEO 生成器（Cloudflare Pages / GitHub Pages 通用）
- 服务端预生成真实 HTML 文章页 => 爬虫能读到文字 => 可做 SEO
- 每天（GitHub Actions）新增 N 篇，历史永久保留 => 收录越积越多
- 零 API、零成本、纯标准库
用法: python generate.py
"""
import random, json, os, hashlib
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(ROOT, "posts.json")
DIST = os.path.join(ROOT, "dist")

# ---------- 词库（与旧版一致） ----------
WEIRD_PLACE = ["小区电梯","老房子阁楼","公司茶水间","出租屋衣柜","深夜便利店","地铁末班车","老家旧仓库","合租屋浴室","单位档案室","山顶小庙"]
WEIRD_THING = ["自己上下跑","传来打字声","灯一闪一闪","飘出饭菜香","贴着张新纸条","回放着昨天的新闻","多了双湿脚印","响起了儿歌声","照出不存在的人","自动归位了"]
WEIRD_REASON = ["物业说是检修","厂家说是感应","邻居说从没这回事","监控偏偏那段坏了","电工说线路早断了","房东说前任住户也提过","物业经理连夜辞职了","物业说系统升级","谁都解释不清","业主群已炸"]
BS_TOPIC = ["拖延症","爱睡懒觉","爱囤东西","爱刷短视频","爱迟到","选择困难","爱点奶茶","爱熬夜","爱发呆","爱砍价"]
BS_CLAIM = ["人类进化的自我保护机制","远古祖先留下的生存智慧","大脑在帮你筛选重要信息","身体在偷偷优化能量分配","基因里写好的节能程序","集体潜意识的温柔提醒","一种被低估的修复模式","高等生命体的缓冲策略","文明进步的隐性成本","神经系统自带的杀毒逻辑"]
BS_DETAIL = ["论文指出这能躲过无数陷阱","研究表明它在帮你看清真相","数据显示它在降低你的焦虑","实验证明它提升了决策质量","观察发现它延长了平均寿命","统计显示它减少了无效社交","考证说明它保护了物种延续","测算发现它节约了认知资源","记录显示它增强了心理韧性","推演得出它在守护创造力"]

# 笑话精选池（谐音梗 + 三国搞笑 + 日常反转）
JOKE_POOL = [
  {"t":"虾的社交困境", "b":'虾的朋友圈不敢发动态，因为一开口就是"我虾了"。'},
  {"t":"螃蟹的买菜路线", "b":'螃蟹出门买菜，别人问它怎么走，它说：我横着扫码。'},
  {"t":"香蕉的败因", "b":'香蕉和苹果打架，香蕉输了，因为苹果有"果"力。'},
  {"t":"汤圆的惨叫", "b":'汤圆滚下楼梯，哭着喊：我完了，露馅了！'},
  {"t":"脚滑的狐狸", "b":'什么动物最容易摔倒？狐狸，因为它脚滑（狡猾）。'},
  {"t":"布的恐惧", "b":'布和纸最怕什么？布怕一万，纸怕万一——不怕一万，只怕万一。'},
  {"t":"迷路的鹿", "b":'从前有只鹿走着走着迷路了，于是变成了马路。'},
  {"t":"鸭子的呼救", "b":'小鸭子迷路了一直叫：鸭迷鸭迷鸭迷……（雅米雅米）。'},
  {"t":"海鸥的沉默", "b":'为什么海鸥飞到巴黎就不叫了？因为巴黎鸥来哑（巴黎欧莱雅）。'},
  {"t":"洋葱的委屈", "b":'土豆和洋葱一起吃最难过，因为洋葱土豆（阴阳吐槽）。'},
  {"t":"牛奶的感叹", "b":'牛奶过期了，对着冰箱叹气：我的人生变质了。'},
  {"t":"饼干的呼救", "b":'饼干掉进咖啡，爬起来喊：救命，我泡软了！'},
  {"t":"西瓜的心事", "b":'西瓜切开里面全是籽，它说：这是我的一肚子话。'},
  {"t":"面条的泳后感受", "b":'面条去游泳，上岸后说：好家伙，我软了。'},
  {"t":"鸡蛋的心碎", "b":'鸡蛋爱上了石头，表白时心碎，成了散黄蛋。'},
  {"t":"张飞的健身房", "b":'张飞开了家健身房，说自己在长坂坡吼退曹军，客户都说他"声波燃脂"效果奇佳。关羽：那我的"脸红增肌班"是不是也能开？'},
  {"t":"诸葛亮的朋友圈", "b":'诸葛亮借完东风发朋友圈：今天帮人放了个风筝，周瑜说下次送我VIP草船借箭卡。评论区曹操已屏蔽。'},
  {"t":"孙权的读书建议", "b":'孙权劝吕蒙读书：别天天打《王者东吴》了。吕蒙：我读《霸道主公爱上我》行吗？孙权：……那还是继续打游戏吧。'},
  {"t":"关羽的凡尔赛", "b":'关羽凡尔赛发言：每天用青龙偃月刀修眉，顺手就打理了胡子。张飞：二哥你眉毛是不是涂了赤兔牌染色膏？'},
  {"t":"司马懿的会员", "b":'司马懿熬死诸葛亮后点播《向天再借五百年》，侍卫：主公，B站会员要借曹丕的账号吗？司马懿：……不急，我还能再苟几集。'},
  {"t":"赵云的快递差评", "b":'赵云长坂坡送快递，阿斗收货后给了一星差评：包裹晃动剧烈，差点头晕。'},
  {"t":"刘备的三缺一", "b":'三顾茅庐后，刘备紧握诸葛亮的手热泪盈眶：兄弟们，我们不再三缺一了！'},
  {"t":"关羽的断后", "b":'关羽冲进帐：被包围了，大哥快走！刘备：云长帮我断后！关羽手起刀落把刘禅砍成两截。刘备：尼玛我说的不是这个！'},
  {"t":"貂蝉的烦恼", "b":'吕布：宝贝，董卓送你的包为啥不背？貂蝉：LV的"连环计"联名款太沉了，不如你送我赤兔电动车钥匙？'},
  {"t":"曹操的头疼", "b":'华佗：丞相，开颅手术考虑一下？曹操：孤宁可头痛，也不能让你知道我脑内全是《短歌行》没保存的草稿！'},
  {"t":"黄忠的比赛", "b":'黄忠参加老年射箭赛，裁判：大爷您这弓超规格了吧？黄忠：年轻人，这叫传统工艺复原款！赛后采访：你大爷永远是你大爷。'},
  {"t":"诸葛亮的放屁", "b":'诸葛亮想放屁又怕刘备听见，便学啄木鸟叫了两声趁机放了。刘备：你再学一次吧，刚才你放屁声太大我没听见。'},
  {"t":"刘备摔孩子", "b":'刘备摔孩子，是为了让孩子接受挫折教育——这是专家说的，不是我编的。'},
  {"t":"周瑜的荆州", "b":'周瑜借出荆州之后要不回来，因为没经过公证。'},
  {"t":"关羽的刀郎", "b":'关羽五绺长髯，使一口青龙偃月刀，人们送他一个美称：刀郎。曹操听了默默把《2002年的第一场雪》设成了铃声。'},
  {"t":"咸鱼翻身失败", "b":'本想咸鱼翻身，结果没翻好，粘锅了。'},
  {"t":"减肥的真相", "b":'减肥这件事：嘴巴答应得飞快，身体坚决反对。'},
  {"t":"闹钟的意义", "b":'闹钟的作用不是叫醒我，是提醒我还能再睡十分钟。'},
  {"t":"苦瓜的误会", "b":'去买水果，老板说这瓜特别甜。我咬了一口：一点都不甜啊。老板淡定：哦，那是苦瓜。'},
  {"t":"星星的区别", "b":'我问朋友你和星星有啥区别，他说不知道。我说：星星在天上，你在我心里。顿了两秒补了句：不过是在我心里犯傻。'},
  {"t":"钱包的坦白", "b":'我对钱包说：马年要到了你准备好了吗？钱包叹气：别提了，我已经被马踩扁了。'},
  {"t":"老板的画饼", "b":'老板：新一年大家要马上进入工作状态！我：好的老板，但我现在只想马上退休。'},
  {"t":"摸鱼日常", "b":'每天的状态：间歇性想辞职，持续性在上班。'},
  {"t":"打工人真相", "b":'以前叫"牛马"，今年是"真马"。身份升级了，工资啥时候升级？'},
  {"t":"孙悟空的紧箍咒", "b":'唐僧念紧箍咒，其实是播放语音备忘录："已到达大雷音寺，请注意倒车雷达"。孙悟空：师父你这咒语还带导航？'},
  {"t":"悟空求职", "b":'孙悟空简历写"曾大闹天宫"，HR问为何离职，他说：玉帝不让我进蟠桃园，说我会偷吃。HR：这理由我信。'},
  {"t":"八戒减肥", "b":'猪八戒说在减肥，方法是"不照镜子"——眼不见为净。悟空：二师兄这不叫减肥，这叫自欺欺猪。'},
  {"t":"沙僧的台词", "b":'沙僧取经路上就三句：大师兄师父被抓了、二师兄师父被抓了、大师兄二师兄被抓了。导演：你这演技叫"复读机流"。'},
  {"t":"火眼金睛", "b":'孙悟空的火眼金睛其实是近视加散光，看谁都像妖怪，所以见谁打谁。观音：这眼该配镜了。'},
  {"t":"如来的手掌", "b":'如来伸手，悟空翻十万八千里没出去。佛祖：这叫5G全覆盖，信号满格，你别想跑。'},
  {"t":"红孩儿直播", "b":'红孩儿会三昧真火，开直播卖打火机，粉丝问"能烧真钱吗"，他说"能，但你舍得吗"。'},
  {"t":"二郎神加眼", "b":'二郎神三只眼嫌少，去眼科加了一只变"四郎神"，专治各种不服。哮天犬：主人你现在是四边形了。'},
  {"t":"武松打虎", "b":'武松打虎其实是老虎抢他酒，他醉了上来一顿揍。老虎：我只是想尝一口，至于吗。'},
  {"t":"林冲买刀", "b":'林冲花重金买宝刀，高俅说"此刀认主"。林冲：认主个屁，明明是你想坑我钱。'},
  {"t":"黑旋风", "b":'李逵外号黑旋风，因为他一砍人大家就旋风一样跑了，他追着喊：别跑，我还没拍完照！'},
  {"t":"及时雨", "b":'宋江叫及时雨，因为他发朋友圈总赶在雨天。兄弟：你这雨下得真"及时"（讽刺脸）。'},
  {"t":"鲁智深拔树", "b":'鲁智深倒拔垂杨柳，其实是树挡了他晒被子，一气之下连根拔了。邻居：大力出奇迹。'},
  {"t":"高俅的球", "b":'高俅靠踢球当太尉，皇帝说：你球踢得好，下届世界杯带你去。高俅：谢主隆恩。'},
  {"t":"通灵宝玉", "b":'宝玉含玉而生，那玉其实是块充电宝，没电了他就来精神。黛玉：你这玉怎么还带USB口。'},
  {"t":"黛玉葬花", "b":'林黛玉葬花是垃圾分类，她说花瓣属湿垃圾不能乱扔。宝玉：妹妹真环保，下次带个分类桶。'},
  {"t":"宝钗金锁", "b":'宝钗金锁刻"不离不弃"，是她妈网购的"情侣锁"，配宝玉的玉包邮到家。宝玉：这锁我早有了。'},
  {"t":"凤辣子", "b":'王熙凤精于算计人称凤辣子，其实是开了家网贷，利息算得比谁都溜。贾琏：你贷给我那笔啥时候免。'},
  {"t":"刘姥姥进园", "b":'刘姥姥进大观园见啥都新鲜：这马桶还会自己冲水？贾母：姥姥，那是智能款，声控的。'},
  {"t":"宝玉挨打", "b":'贾政打宝玉因他不考公务员。贾政：你看看林家，探花出身。宝玉：爹，我现在考也来不及了。'},
  {"t":"白素贞报恩", "b":'白素贞报恩嫁许仙，因前世许仙救过一条蛇。白素贞：这恩得用一辈子还。许仙：姐，我那会儿就是顺手。'},
  {"t":"法海不懂爱", "b":'法海总说"妖就是妖"，其实他暗恋白素贞，用"除妖"掩饰。小青：你这掩饰也太硬了。'},
  {"t":"小青吐槽", "b":'小青天天给姐姐当电灯泡，说：我才是这剧最大受害者，恋爱我没份，打怪我在前。'},
  {"t":"雄黄酒", "b":'端午喝雄黄酒白素贞现形，许仙吓死。白素贞盗仙草救他，许仙醒来：老婆你又去哪野了。'},
  {"t":"七兄弟", "b":'七葫芦娃各有本领，爷爷说：你们七个凑一起能组个复仇者联盟。蛇精：那我当灭霸。'},
  {"t":"蛇精的如意", "b":'蛇精的如意说变就变，蝎子精：老婆哪买的我也整一个。蛇精：拼多多九块九包邮，限购三件。'},
  {"t":"二娃偷窥", "b":'二娃千里眼顺风耳偷看蛇精练功，蛇精：你这算偷窥，我要报警。二娃：我这是侦查，合法。'},
  {"t":"水火娃", "b":'水娃吐水火娃喷火，俩人吵架家里先发大水又着火。爷爷：你俩还是住校吧。'},
  {"t":"愚公的产权", "b":'愚公移山，智叟说他傻，愚公：我不傻，我买了山的产权，开发商不让挪，我只能自己挖。'},
  {"t":"智叟的算盘", "b":'智叟劝愚公别挖，其实他想承包这山搞旅游，愚公挖走了他就没生意。智叟：你坏我好事。'},
  {"t":"夸娥氏二子", "b":'天帝感动派夸娥氏二子搬山，二子：爸，这活又外包给我们。天帝：家族企业，懂得都懂。'},
  {"t":"后羿射日", "b":'后羿射九个太阳剩一个，其实是他箭法差九个才中，第十个躲得快。天帝：你这KPI不达标啊。'},
  {"t":"嫦娥奔月", "b":'嫦娥奔月是因误服后羿的减肥药，一飞冲天。后羿：那是我花三百两买的，你当糖吃了？'},
  {"t":"精卫填海", "b":'精卫衔石填海，海说：你填你的我淹我的，别累着。精卫：我填的不是海，是执念。'},
  {"t":"哪吒闹海", "b":'哪吒抽了龙王三太子筋做绦带，龙王：你抽我儿子筋？哪吒：手误，当腰带使了，还挺合身。'},
  {"t":"龟兔赛跑", "b":'龟兔赛跑兔子输了，其实他买了乌龟的保险，乌龟赢了他有提成。兔子：这局我赢了。'},
  {"t":"守株待兔", "b":'农夫守株待兔，其实他在树下摆摊卖兔子，专等兔子撞死当货源。邻居：你这生意真绝。'},
  {"t":"掩耳盗铃", "b":'掩耳盗铃的人以为自己听不见别人也听不见。邻居：你聋了不等于我聋，报警了啊。'},
  {"t":"刻舟求剑", "b":'刻舟求剑的人剑掉船上刻记号，船夫：哥，水不长脚你刻它干啥，下游捞去吧。'},
  {"t":"女娲补天", "b":'女娲补天用五彩石，其实她家天花板漏了拿石头糊上，顺便发朋友圈：今日手作，限量版。'},
  {"t":"对牛弹琴", "b":'对牛弹琴，牛说：你弹你的我吃我的，别指望我鼓掌，我只会反刍。'}
]

# 故事精选池（野史魔改）
STORY_POOL = [
  {"t":"张飞其实是女的", "b":'桃园三结义，张飞其实是个女的。因为她的秘密被孙权发现了，所以只能白天杀敌，晚上侍候孙权。华佗给张飞推背，问张非是不是他杀的，他说不是，说是温酒杀的——因为温酒煮华雄。'},
  {"t":"关羽温酒斩华雄", "b":'关羽温酒斩华雄，其实是因为他喝酒上头，把华雄当成了送外卖的，一刀下去才发现认错人。'},
  {"t":"诸葛亮的天气预报", "b":'诸葛亮借东风，其实是提前看了手机天气预报，挑了个有大风的日子。周瑜到现在还以为他真会法术。'},
  {"t":"刘备三顾茅庐", "b":'刘备三顾茅庐，前两次诸葛亮都在午睡，第三次诸葛亮干脆装不在家。刘备：这兄弟，比我还能磨。'},
  {"t":"曹操煮酒论英雄", "b":'曹操煮酒论英雄，刘备吓得筷子都掉了。其实不是怕，是他那天没吃早饭，手抖。'},
  {"t":"赵云长坂坡迷路", "b":'赵云长坂坡七进七出，其实是导航走错了路，绕来绕去没出去，顺手把阿斗救了。'},
  {"t":"周瑜的死因", "b":'周瑜被气死，临死前喊"既生瑜何生亮"，其实是因为诸葛亮朋友圈从不给他点赞。'},
  {"t":"吕布的最佳孝子", "b":'吕布认丁原当干爹，又认董卓当干爹，人称三国最佳孝子。可惜两位爹都没活过他。'},
  {"t":"貂蝉的副业", "b":'貂蝉用连环计让吕布和董卓反目，事儿办完她自己偷偷开了家美妆店，生意比打仗好。'},
  {"t":"司马懿的体检", "b":'司马懿能熬死诸葛亮，靠的不是智谋，是体检报告比别人好。人家年年体检，孔明熬夜写稿。'},
  {"t":"张飞的长坂桥头", "b":'张飞在长坂桥大吼退曹军，其实是他刚喝了假酒，嗓门大得自己都怕。曹军以为有伏兵，全跑了。'},
  {"t":"红脸黑脸白脸", "b":'关羽为什么是红脸？不是害羞，是高血脂。张飞为什么是黑脸？不是晒的，是肝硬化。曹操白脸？缺铁性贫血。'},
  {"t":"华佗刮骨疗毒", "b":'华佗给关羽刮骨疗毒时，关羽在干嘛？在参加三国围棋擂台赛，一边下棋一边刮，面不改色。'},
  {"t":"刘备双手过膝", "b":'刘备双手过膝，别人说他帝王之相。其实是缺钙，站久了膝盖打弯，手自然就垂下去了。'},
  {"t":"阿斗扶不起来", "b":'阿斗扶不起来，不是笨，是缺锌。补了钙铁锌维生素之后，他只是懒，不是扶不起来。'},
  {"t":"草船借箭真相", "b":'草船借箭，诸葛亮算准大雾。其实他前一天看了天气预报，周瑜的箭是白送的。'},
  {"t":"空城计的破绽", "b":'诸葛亮摆空城计，司马懿明知有伏兵却退了。因为司马懿想：这老小子万一死了，我回去也得被曹睿炒了。'},
  {"t":"桃园年龄之谜", "b":'桃园三结义，刘备是大哥、关羽老二、张飞老三。但张飞其实比刘备还大两岁，只是心眼少，甘当老三。'},
  {"t":"曹操的短歌行", "b":'曹操写《短歌行》得意地念给郭嘉听。郭嘉：丞相，这歌虽短却意蕴悠长，正所谓"短中见长"。曹操大笑。郭嘉补刀：再精简点就能"短而精"了。'},
  {"t":"山东女婿打架", "b":'整个三国就是一群山东女婿在打群架——曹操、刘备、孙权的夫人都来自山东临沭一带。所以赤壁之战，本质是老丈人家的内部矛盾。'},
  {"t":"张飞的胡子", "b":'张飞羡慕关羽的美髯，关羽说：你不如多喝点老酒。张飞当真喝醉，第二天一摸胡子还是老样子。'},
  {"t":"刘备的自我介绍", "b":'刘备第一次去隆中，下马恭敬敲门自报家门：汉左将军、宜城亭侯、豫州牧、皇叔刘备。门童懵了：这么多称呼我记不住。刘备：你就说刘备来了就行。'},
  {"t":"董卓的四大理想", "b":'董卓的四大理想：吕布整天爸爸叫，王允老儿早挂掉，貂蝉不演无间道，中原百姓朝我笑。'},
  {"t":"诸葛亮的锦囊", "b":'孙权追刘备到江边，刘备打开第三个锦囊，里面是件蓝紧身衣、红短裤、红披风，字条写：变成超人，可退敌兵！刘备内牛满面。'},
  {"t":"杨修之死", "b":'曹操为何杀杨修？因为杨修在书店看到一本作者叫孟德斯鸠的书，大笑：哈哈孟德这个鸟东西也能写书？曹操闻言大怒。'},
  {"t":"张飞的兵器", "b":'刘关张去铸兵器，铁匠对刘备说你有剑用，对关羽说你有刀用。轮到张飞，刘备慌忙拉住：三弟，依你脾气还是别去了——他有丈八蛇矛啊。'},
  {"t":"曹操青梅煮酒", "b":'曹操青梅煮酒邀刘备，问了个深刻问题：今天，你喝了没有？刘备：……喝了。'},
  {"t":"刘备摔阿斗", "b":'赵云救回阿斗，刘备一把摔地上：为你这孺子，几损我一员大将！其实他瞄了下地面是草坪，才敢摔的。'},
  {"t":"司马懿的忍功", "b":'司马懿被诸葛亮送女人衣服羞辱，不但没生气还穿上了，因为他算过：忍一时风平浪静，忍到对方先死。'},
  {"t":"张飞的嗓门", "b":'张飞嗓门大，在当阳桥一声吼，桥都震了。曹操探子回报：前方有巨型音响部队，建议绕行。'},
  {"t":"诸葛亮的短信", "b":'诸葛亮在锦囊里写的是什么？短信呗。每次出征前群发：兄弟们挺住，我马上到。'},
  {"t":"周瑜的嫉妒", "b":'周瑜嫉妒诸葛亮，不是因为才华，是因为诸葛亮朋友圈的九宫格每次都比他精致。'},
  {"t":"刘备暗度陈仓", "b":'刘备吃完西瓜把皮扔身后。关羽路过一脚踩上滑倒，爬起来幽怨：大哥你扔西瓜皮好歹说一声。刘备：二弟，我这在练习暗度陈仓。'},
  {"t":"大闹天宫真相", "b":'孙悟空大闹天宫，不是想造反，是想去天庭网吧包夜，玉帝不让，他急了把路由器拔了，全网瘫痪。'},
  {"t":"三打白骨精", "b":'白骨精是唐僧前女友，变化来试探他。悟空看破不说破，一棒送走：兄弟，这缘份我替你斩了。'},
  {"t":"八戒戏嫦娥", "b":'猪八戒调戏嫦娥被贬下凡，其实他只是想求个签名，被误会成骚扰，背了上千年黑锅。'},
  {"t":"真假美猴王", "b":'六耳猕猴是悟空的分身，其实是悟空自己演的，就为向唐僧证明：没我你取不了经。唐僧：我信了还不行吗。'},
  {"t":"女儿国国王", "b":'女儿国国王看上唐僧，唐僧没动心是假的，他只是想起今天忘给悟空发工资，怕猴哥闹情绪。'},
  {"t":"人参果", "b":'镇元大仙的人参果被悟空偷吃，要油炸他。观音来劝：别炸了，这猴子是我VIP客户，欠我三筐蟠桃。'},
  {"t":"逼上梁山", "b":'林冲被高俅"逼上梁山"，其实是高俅群里@他：兄弟来我们公司，福利好。林冲：那我不客气了。'},
  {"t":"智取生辰纲", "b":'吴用智取生辰纲，在杨志水里下蒙汗药。杨志醒来货没了，还收到一张水费账单：本次用药用水3升。'},
  {"t":"鲁智深出家", "b":'鲁智深出家是因为分手了。方丈：施主看破红尘了？鲁智深：看破了，主要是看破前任。'},
  {"t":"宋江招安", "b":'宋江一心招安，因为梁山房贷压力大。他对兄弟们说：咱还是得有个编制，五险一金它不香吗。'},
  {"t":"李逵背母", "b":'李逵背母上山遇虎，母亲被吃。他大哭：娘你咋不跑快点。其实他娘那天穿了双不合脚的新鞋。'},
  {"t":"木石前盟", "b":'宝玉是石头，黛玉是绛珠草，石头天天给她浇水，草感动了投胎来还债。这大概是最早的"滴水之恩涌泉相报"。'},
  {"t":"黛玉烧稿", "b":'黛玉死前烧诗稿，其实是在清微信聊天记录，怕宝玉看到她那些吃醋的话。紫鹃：姑娘，烧了也晚了。'},
  {"t":"元春省亲", "b":'元春省亲建大观园花光积蓄，贾府后来败落，有一部分原因写在账本上：省亲预算超支。'},
  {"t":"宝玉出家", "b":'宝玉最后出家，不是看破红尘，是考了三次公务员没中，心灰意冷去庙里当了个保安，包吃包住。'},
  {"t":"晴雯撕扇", "b":'晴雯撕扇子，宝玉笑袭人哭——因为扇子是袭人刚买的，还没用就撕了。袭人：我的钱也不是大风刮来的。'},
  {"t":"水漫金山", "b":'白素贞水漫金山救许仙，其实是发动全城洒水车。法海：你这是违规用水，罚款五百！'},
  {"t":"断桥相会", "b":'断桥上白素贞许仙重逢，许仙：老婆我错了。白素贞：错啥，下次别乱喝雄黄，我救你一次累半年。'},
  {"t":"盗仙草", "b":'白素贞上昆仑盗仙草，守山童子拦她，她掏出"亲夫病危证明"，童子一看：快去快回，别声张。'},
  {"t":"葫芦山", "b":'葫芦山压着蛇精蝎子精，老汉采药误放。爷爷：我就挖个野菜，怎么挖出俩妖怪，还附赠一只穿山甲。'},
  {"t":"七子连心", "b":'七葫芦娃合体成葫芦小金刚，妖怪们：你们这开挂！小金刚：这叫团队作战，不懂了吧。'},
  {"t":"爷爷被抓", "b":'爷爷被蛇精抓了N次，蛇精：这老头是我抓过最多次的人质，我都快成他粉丝了。'},
  {"t":"移山真相", "b":'愚公移山不是真搬，是他想修条路邻居不让过，只好自己挖通，成了史上第一位隧道工程师。'},
  {"t":"两座山", "b":'太行王屋二山挡路，愚公说：这俩山像我前妻和她妈，堵得我喘不过气，必须搬。'},
  {"t":"牛郎织女", "b":'牛郎织女被银河隔开，每年七夕鹊桥相会，其实是王母搞的"异地恋考核"，过了才准在一起。'},
  {"t":"孟姜女", "b":'孟姜女哭长城塌了一段，工头：这质量，怪不得秦始皇要重修，验收都没过。'},
  {"t":"梁祝化蝶", "b":'梁祝化蝶，其实是俩人考学失败想不开，死后变蝴蝶，寓意"有些墙飞不过去"。'},
  {"t":"八仙过海", "b":'八仙过海各显神通，其实是抢着买单谁都不服，就比谁过海花样多。铁拐李：我拄拐都能赢。'},
  {"t":"大禹治水", "b":'大禹治水三过家门不入，其实他和老婆吵架了不好意思回去。妻：回来吃饭！禹：在忙，治水呢。'},
  {"t":"盘古开天", "b":'盘古开天死后身体化万物，风说他呼的气，云说他流的汗。朋友：你这遗体捐赠真彻底。'},
  {"t":"田螺姑娘", "b":'田螺姑娘每天给穷汉做饭，穷汉偷看发现是田螺精，说：妹子，你螺盖别老开着，进灰。'},
  {"t":"叶公好龙", "b":'叶公好龙，真龙来了他吓跑。龙：你这喜好是表面的，我申请退货，运费你出。'},
  {"t":"狐假虎威", "b":'狐狸借老虎威风，老虎后来知道了：你借我名气行，分我一半好处。狐狸：成交，三七开。'},
  {"t":"拔苗助长", "b":'农夫拔苗助长苗死了，他：我是想让它长快点，谁知道它这么娇气，比我还能作。'},
]
NEWS_HEAD = ["某","一","本地","网传","据称","有","多家","神秘","深夜","凌晨"]
NEWS_OBJ = ["小区","公司","学校","商场","公园","医院","车站","网吧","工厂","寺庙"]
NEWS_EVT = ["电梯自顾自运行","监控拍到不该有的画面","灯全灭后又亮起","传来无人说话声","地面出现奇怪水痕","猫集体朝一个方向叫","广播念出陌生名字","空调吹出旧歌","门自动开合","时钟快了三小时"]
TIMES = ["刚刚","8分钟前","23分钟前","1小时前","2小时前","3小时前","5小时前","昨天","前天","上周"]

CATS = {
    "news":  {"tag":"诡异快讯","cls":"t-news","icon":"\U0001F4F0","color":"#7c5cff"},
    "weird": {"tag":"诡异趣事","cls":"t-weird","icon":"\U0001F47B","color":"#3aa0ff"},
    "bs":    {"tag":"一本胡说","cls":"t-bs","icon":"\U0001F92A","color":"#ff8a3a"},
    "joke":  {"tag":"笑话","cls":"t-joke","icon":"\U0001F602","color":"#ff5c8a"},
    "story": {"tag":"故事","cls":"t-story","icon":"\U0001F4D6","color":"#2bbf8a"},
}

def gen_news(rng): return rng.choice(NEWS_HEAD)+rng.choice(NEWS_OBJ)+rng.choice(NEWS_EVT)+"，"+rng.choice(WEIRD_REASON)+"。"
def gen_weird(rng): return "我家"+rng.choice(WEIRD_PLACE)+"半夜"+rng.choice(WEIRD_THING)+"，"+rng.choice(WEIRD_REASON)+"。但为什么每次都正好那么巧？这事我到现在没想通。"
def gen_bs(rng): return "科学家称："+rng.choice(BS_TOPIC)+"是"+rng.choice(BS_CLAIM)+"。"+rng.choice(BS_DETAIL)+"。所以你今天这样，是在保护物种延续。有理有据，令人信服。"
def gen_joke(rng):
    return rng.choice(JOKE_POOL)["b"]
def gen_story(rng):
    return rng.choice(STORY_POOL)["b"]

GEN = {"news":gen_news,"weird":gen_weird,"bs":gen_bs,"joke":gen_joke,"story":gen_story}

def title_for(cat, body, rng):
    if cat=="news": return body[:18]+("\u2026" if len(body)>18 else "")
    if cat=="weird": return "我家"+rng.choice(WEIRD_PLACE)+"的那件怪事"
    if cat=="bs": return "研究称"+rng.choice(BS_TOPIC)+"竟是"+rng.choice(BS_CLAIM)[:6]
    return body[:18]

def make_rng(d):
    s = int(hashlib.md5(("naodong-"+d.isoformat()).encode("utf-8")).hexdigest(), 16)
    return random.Random(s)

def gen_day(d, n=12):
    rng = make_rng(d)
    # 笑话/故事是精选段子，权重调高，整体更好笑
    weights = ["joke"]*6 + ["story"]*4 + ["bs"]*4 + ["weird"]*2 + ["news"]*2
    posts = []
    for i in range(n):
        cat = rng.choice(weights)
        if cat=="joke":
            it = rng.choice(JOKE_POOL); body = it["b"]; title = it["t"]
        elif cat=="story":
            it = rng.choice(STORY_POOL); body = it["b"]; title = it["t"]
        else:
            body = GEN[cat](rng)
            title = title_for(cat, body, rng)
        posts.append({
            "id": d.isoformat()+"-"+("%02d"%(i+1)),
            "date": d.isoformat(),
            "cat": cat,
            "tag": CATS[cat]["tag"],
            "cls": CATS[cat]["cls"],
            "icon": CATS[cat]["icon"],
            "color": CATS[cat]["color"],
            "title": title,
            "body": body,
            "read": "%d.%dw"%(rng.randint(3,52), rng.randint(0,9)),
        })
    return posts

def load_all():
    if os.path.exists(STATE):
        try: return json.load(open(STATE, encoding="utf-8"))
        except Exception: return []
    return []

def save_all(posts):
    json.dump(posts, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def esc(s):
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

INDEX_TPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>每日胡说 · 诡异趣事/胡说/笑话/故事/运势，每天来刷</title>
<meta name="description" content="每日胡说：每天更新诡异快讯、怪奇趣事、一本胡说、爆笑笑话和暖心故事，还有每日运势、趣味测试和今日灵签，午休刷一眼，烦心事少一半。">
<meta property="og:title" content="每日胡说">
<meta property="og:type" content="website">
<link rel="stylesheet" href="/style.css">
</head>
<body>
<header class="hd">
  <div class="logo">\U0001F4AD 每日胡说</div>
  <div class="slogan">诡异 · 胡说 · 笑话 · 故事 · 运势 —— 每天来刷一眼</div>
</header>

<main class="wrap">
  <section class="hero">
    <div class="daily">__DATE__ 今日精选</div>
    <h1>今天有什么新鲜的胡说八道？</h1>
    <a class="star" href="#" onclick="alert('已收藏！明天同一时间回来，又有新的');return false;">\U00002B50 收藏本站</a>
  </section>

  <section class="feed">
    <h2>最新内容</h2>
    <div class="list">__POSTS__</div>
  </section>

  <section class="play">
    <div class="card fort">
      <h3>\U0001F52E 每日运势</h3>
      <div class="zx"><button class="zbtn">选生肖看今日运</button></div>
      <div class="zout" id="zout" style="display:none"></div>
    </div>
    <div class="card fort">
      <h3>\U0001F9EA 趣味测试</h3>
      <div id="quiz">
        <p id="qtext">测测你是哪种摸鱼高手？</p>
        <div id="qopts"></div>
      </div>
      <div class="qout" id="qout" style="display:none"></div>
    </div>
    <div class="card fort">
      <h3>\U0001F3F4 今日灵签</h3>
      <button id="lotBtn">\U0001F3F4 抽一签</button>
      <div class="lot" id="lotbox" style="display:none">
        <div id="lotSign" class="big"></div>
        <div id="lotTitle"></div>
        <div id="lotDesc"></div>
      </div>
    </div>
  </section>

  <section class="dance">
    <h2>\U0001F57B 每日舞蹈</h2>
    <div class="dhint">每天换一种舞，刷到就想跟着扭（纯前端动画，零成本，不开电脑也自动换）</div>
    <div class="stage" id="stage"></div>
    <div class="dname" id="danceName"></div>
    <div class="dcap" id="danceCap"></div>
  </section>

  <section class="money">
    <h2>\U0001F4B0 支持一下</h2>
    <div class="mc">
      <div class="mcard"><div class="mi">\U0001F49D</div><div class="mt">微信赞赏</div><div class="md" id="wxbox">赞赏码待设置</div></div>
      <div class="mcard"><div class="mi">\U000026A1</div><div class="mt">爱发电赞助</div><div class="md" id="afdian">afdian.com 主页待设置（去 afdian.com 注册后把链接发我）</div></div>
      <div class="mcard"><div class="mi">\U0001F6D2</div><div class="mt">好物推荐</div><div class="md">多多进宝/淘宝联盟待设置</div></div>
      <div class="mcard"><div class="mi">\U0001F4FA</div><div class="mt">跟我玩</div><div class="md" id="social">抖音/视频号待设置（发我账号我填）</div></div>
    </div>
  </section>
</main>

<footer class="ft">每日胡说 · 内容由程序自动生成，纯属娱乐，切勿当真 · 每天自动更新</footer>

<script>
var SITE_CONFIG = {
  wxQr: "",            // 微信赞赏码图片(可内联base64或外链)
  afdian: "",          // 爱发电主页链接
  douyin: "",          // 抖音号
  weishi: ""           // 视频号
};
// 运势
var ZODIAC = ["鼠","牛","虎","兔","龙","蛇","马","羊","猴","鸡","狗","猪"];
var LUCKY = ["红","橙","黄","绿","青","蓝","紫","粉","金","银"];
var YI = ["表白","摸鱼","吃火锅","发呆","散步","买彩票","睡懒觉","撸猫","喝奶茶","吐槽"];
var JI = ["加班","开会","算账","搬砖","赶deadline","相亲","减肥","早起","还花呗","立flag"];
function rngFrom(str){var h=1779033703;for(var k=0;k<str.length;k++){h=(h^str.charCodeAt(k))*2654435761>>>0;}return function(){h=(h+0x6D2B79F5)>>>0;var t=Math.imul(h^(h>>>15),1|h);t=(t+Math.imul(t^(t>>>7),61|t))^t;return ((t^(t>>>14))>>>0)/4294967296;};}
function bar(v){return '<div class="bar"><i style="width:'+v+'%"></i></div>';}
document.querySelector('.zbtn').onclick=function(){
  var z=prompt('输入你的生肖（如 龙）','龙'); if(!z)return;
  var d=new Date(); var key=z+' '+d.getFullYear()+'-'+(d.getMonth()+1)+'-'+d.getDate();
  var r=rngFrom(key);
  var out='<p>【'+z+'】今日运势</p>';
  out+='财运 '+bar(20+Math.floor(r()*80))+'桃花 '+bar(20+Math.floor(r()*80))+'健康 '+bar(20+Math.floor(r()*80));
  out+='<p>幸运色：'+LUCKY[Math.floor(r()*LUCKY.length)]+' ｜ 宜：'+YI[Math.floor(r()*YI.length)]+' ｜ 忌：'+JI[Math.floor(r()*JI.length)]+'</p>';
  document.getElementById('zout').innerHTML=out; document.getElementById('zout').style.display='block';
};
// 测试
var Q={
  q:"测测你是哪种摸鱼高手？",
  o:["上班就困，下班精神","随时想搞点副业","能躺着绝不坐着","计划永远明天开始"],
  r:["随遇而安型：佛系摸鱼，快乐至上","副业狂魔型：主业划水，副业搞钱","随时跑路型：身体在工位，心已离职","拖延大师型：明日复明日，摸鱼无止境"]
};
(function(){
  var box=document.getElementById('qopts');
  Q.o.forEach(function(t,i){var b=document.createElement('button');b.textContent=t;b.onclick=function(){var rr=rngFrom(t+'x');var res=Q.r[Math.floor(rr()*Q.r.length)];document.getElementById('qout').innerHTML='<p>你是：<b>'+res+'</b></p>';document.getElementById('qout').style.display='block';box.style.display='none';};box.appendChild(b);});
})();
// 灵签
var LOTS=[{t:"上上签",d:"今日宜躺平，诸事皆顺"},{t:"中平签",d:"平淡是真，别凑热闹"},{t:"下下签",d:"宜吃顿好的，祸从口出少说话"},{t:"吃货签",d:"今日运势写在胃里，去吃！"},{t:"桃花签",d:"宜主动，今晚有人想你"},{t:"财神签",d:"宜捡钱，走路低头看"},{t:"咸鱼签",d:"宜翻身，就今天"}];
document.getElementById('lotBtn').onclick=function(){
  var d=new Date(); var key=d.getFullYear()+'-'+(d.getMonth()+1)+'-'+d.getDate();
  if(localStorage.getItem('lot_'+key)){document.getElementById('lotbox').innerHTML='<div class="big">\U0001F3F4</div><p>今日已抽 · 明天再来</p>';document.getElementById('lotbox').style.display='block';return;}
  var rr=rngFrom('lot'+key); var l=LOTS[Math.floor(rr()*LOTS.length)];
  localStorage.setItem('lot_'+key,'1');
  document.getElementById('lotSign').textContent='\U0001F3F4';
  document.getElementById('lotTitle').textContent='【'+l.t+'】';
  document.getElementById('lotDesc').textContent=l.d;
  document.getElementById('lotbox').style.display='block';
};
// 每日舞蹈（按天换舞种，纯前端动画）
(function(){
  var DANCES=[
    {n:"机械舞",e:["🤖","🕺","🤖","💃","🕺"],a:"d-shake",c:"今日 BGM：车间进行曲。动起来像被按了开关。"},
    {n:"摇摆舞",e:["💃","🕺","💃","🕺","🐶"],a:"d-wob",c:"左右摇摆，烦恼跟着甩出去。"},
    {n:"陀螺舞",e:["🌀","🕺","💃","🌀","🕺"],a:"d-spin",c:"转就完事了，转晕了就不想上班。"},
    {n:"弹簧舞",e:["🕺","💃","🐰","🕺","💃"],a:"d-jump",c:"一蹦一蹦，像刚发了工资。"},
    {n:"踢腿舞",e:["🦵","🕺","💃","🕺","🦵"],a:"d-kick",c:"腿都快踢到天花板了，注意安全。"},
    {n:"抖肩舞",e:["🕺","💃","🐱","🕺","💃"],a:"d-wob",c:"肩膀抖起来，班味瞬间少一半。"},
    {n:"扭腰舞",e:["💃","🕺","🐻","💃","🕺"],a:"d-kick",c:"腰是借来的，今天必须扭够本。"}
  ];
  var d=new Date(); var key=d.getFullYear()+'-'+(d.getMonth()+1)+'-'+d.getDate();
  var r=rngFrom('dance'+key); var dn=DANCES[Math.floor(r()*DANCES.length)];
  document.getElementById('danceName').textContent='今日舞种：'+dn.n;
  document.getElementById('danceCap').textContent=dn.c;
  var st=document.getElementById('stage');
  dn.e.forEach(function(x,i){var s=document.createElement('span');s.className='dancer '+dn.a;s.textContent=x;s.style.animationDelay=(i*0.12)+'s';st.appendChild(s);});
})();
// 填充变现位
if(SITE_CONFIG.wxQr) document.getElementById('wxbox').innerHTML='<img src="'+SITE_CONFIG.wxQr+'" style="width:160px">';
if(SITE_CONFIG.afdian) document.getElementById('afdian').innerHTML='<a href="'+SITE_CONFIG.afdian+'" target="_blank">'+SITE_CONFIG.afdian+'</a>';
if(SITE_CONFIG.douyin||SITE_CONFIG.weishi){var s='';if(SITE_CONFIG.douyin)s+='抖音：'+SITE_CONFIG.douyin+' ';if(SITE_CONFIG.weishi)s+='视频号：'+SITE_CONFIG.weishi;document.getElementById('social').textContent=s;}
</script>
</body>
</html>
"""

POST_TPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ - 每日胡说</title>
<meta name="description" content="__DESC__">
<meta property="og:title" content="__TITLE__">
<meta property="og:type" content="article">
<script type="application/ld+json">__LD__</script>
<link rel="stylesheet" href="/style.css">
</head>
<body>
<header class="hd"><div class="logo">\U0001F4AD 每日胡说</div></header>
<main class="wrap">
<article class="postpage">
  <div class="tag">__TAG__</div>
  <h1>__TITLE__</h1>
  <div class="meta">__DATE__ 发布</div>
  <p class="body">__BODY__</p>
  <a class="back" href="/">\U00002B05 回到首页看更多</a>
</article>
</main>
<footer class="ft">每日胡说 · 内容由程序自动生成，纯属娱乐</footer>
</body>
</html>
"""

CSS = """*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#f5f6fb;color:#222;line-height:1.6}
.hd{background:linear-gradient(120deg,#7c5cff,#3aa0ff);color:#fff;padding:18px 20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap}
.logo{font-size:22px;font-weight:800}
.slogan{font-size:13px;opacity:.9}
.wrap{max-width:760px;margin:0 auto;padding:18px}
.hero{background:#fff;border-radius:14px;padding:22px;margin-bottom:18px;box-shadow:0 2px 12px rgba(0,0,0,.05)}
.daily{color:#7c5cff;font-size:13px;font-weight:700}
.hero h1{font-size:24px;margin:8px 0 14px}
.star{display:inline-block;background:#ff5c8a;color:#fff;padding:8px 16px;border-radius:20px;text-decoration:none;font-size:14px}
.feed h2,.play h2,.money h2{font-size:18px;margin:18px 0 10px}
.list a{display:flex;align-items:center;gap:10px;background:#fff;border-radius:10px;padding:12px 14px;margin-bottom:8px;text-decoration:none;color:#222;box-shadow:0 1px 6px rgba(0,0,0,.04)}
.ic{font-size:20px}
.tt{flex:1;font-size:15px}
.rd{color:#999;font-size:12px}
.play{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}
.card{background:#fff;border-radius:12px;padding:14px;box-shadow:0 1px 6px rgba(0,0,0,.05)}
.card h3{font-size:15px;margin-bottom:10px}
.zbtn,#lotBtn,.fort button{cursor:pointer;border:none;background:#7c5cff;color:#fff;padding:8px 14px;border-radius:8px;font-size:13px}
.zout,.qout,.lot{margin-top:10px;font-size:13px}
.bar{background:#eee;border-radius:6px;height:10px;overflow:hidden;margin:4px 0}
.bar i{display:block;height:100%;background:linear-gradient(90deg,#3aa0ff,#7c5cff)}
.big{font-size:40px;text-align:center}
.fort button{margin-top:6px}
.money .mc{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.mcard{background:#fff;border-radius:12px;padding:14px;box-shadow:0 1px 6px rgba(0,0,0,.05);text-align:center}
.mi{font-size:28px}
.mt{font-weight:700;margin:6px 0}
.md{font-size:12px;color:#777}
.ft{text-align:center;color:#999;font-size:12px;padding:20px}
.postpage{background:#fff;border-radius:14px;padding:22px;box-shadow:0 2px 12px rgba(0,0,0,.05)}
.tag{display:inline-block;background:#7c5cff;color:#fff;padding:3px 10px;border-radius:6px;font-size:12px}
.postpage h1{font-size:24px;margin:10px 0}
.meta{color:#999;font-size:13px;margin-bottom:14px}
.body{font-size:17px;margin-bottom:20px}
.back{display:inline-block;background:#ff5c8a;color:#fff;padding:8px 16px;border-radius:20px;text-decoration:none}
.dance{background:linear-gradient(120deg,#1b1230,#2a1b4d);border-radius:14px;padding:20px;margin:18px 0;color:#fff;text-align:center}
.dance h2{color:#fff;margin:0 0 4px}
.dance .dhint{font-size:12px;color:#cbb8ff;margin-bottom:12px}
.stage{display:flex;justify-content:center;gap:16px;flex-wrap:wrap;min-height:96px;align-items:flex-end}
.dancer{font-size:46px;line-height:1;display:inline-block;transform-origin:bottom center}
.d-kick{animation:kick .9s ease-in-out infinite}
.d-spin{animation:spin 1.3s linear infinite}
.d-wob{animation:wob .7s ease-in-out infinite}
.d-jump{animation:jump .8s ease-in-out infinite}
.d-shake{animation:shake .5s ease-in-out infinite}
@keyframes kick{0%,100%{transform:translateY(0) rotate(-8deg)}50%{transform:translateY(-14px) rotate(8deg)}}
@keyframes spin{0%{transform:rotate(0)}100%{transform:rotate(360deg)}}
@keyframes wob{0%,100%{transform:rotate(-14deg)}50%{transform:rotate(14deg)}}
@keyframes jump{0%,100%{transform:translateY(0)}50%{transform:translateY(-22px)}}
@keyframes shake{0%,100%{transform:translateX(0)}25%{transform:translateX(-10px)}75%{transform:translateX(10px)}}
.dance .dname{font-size:18px;font-weight:800;margin-top:14px;color:#ffd86b}
.dance .dcap{font-size:13px;color:#e7dcff;margin-top:6px;min-height:34px}
@media(max-width:680px){.play{grid-template-columns:1fr}.money .mc{grid-template-columns:1fr}.dancer{font-size:38px}}
"""

def build(posts):
    os.makedirs(os.path.join(DIST,"posts"), exist_ok=True)
    # 样式
    open(os.path.join(DIST,"style.css"),"w",encoding="utf-8").write(CSS)
    # 首页列表
    latest = posts[:48]
    items = "\n".join(
        '<a class="'+p["cls"]+'" href="/posts/'+p["id"]+'.html"><span class="ic">'+p["icon"]+'</span><span class="tt">'+esc(p["title"])+'</span><span class="rd">'+p["read"]+'</span></a>'
        for p in latest)
    # 分类统计（简单导航文字）
    cats_html = " ".join('<span style="color:'+CATS[c]["color"]+'">'+CATS[c]["icon"]+CATS[c]["tag"]+'</span>' for c in CATS)
    idx = INDEX_TPL.replace("__POSTS__", items).replace("__DATE__", date.today().isoformat()).replace("__CATS__", cats_html)
    open(os.path.join(DIST,"index.html"),"w",encoding="utf-8").write(idx)
    # 文章页
    for p in posts:
        desc = p["body"][:60]
        ld = {"@context":"https://schema.org","@type":"Article","headline":p["title"],"datePublished":p["date"],"articleBody":p["body"]}
        body = (POST_TPL
                .replace("__TITLE__", esc(p["title"]))
                .replace("__TAG__", p["tag"])
                .replace("__DATE__", p["date"])
                .replace("__BODY__", esc(p["body"]))
                .replace("__DESC__", esc(desc))
                .replace("__LD__", json.dumps(ld, ensure_ascii=False)))
        open(os.path.join(DIST,"posts", p["id"]+".html"),"w",encoding="utf-8").write(body)
    # sitemap
    base = "https://naodong.tttttttttt.top"
    urls = [base+"/"] + [base+"/posts/"+p["id"]+".html" for p in posts]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "\n".join("  <url><loc>"+u+"</loc></url>" for u in urls)
    sm += "\n</urlset>\n"
    open(os.path.join(DIST,"sitemap.xml"),"w",encoding="utf-8").write(sm)
    open(os.path.join(DIST,"robots.txt"),"w",encoding="utf-8").write(
        "User-agent: *\nAllow: /\nSitemap: "+base+"/sitemap.xml\n")
    print("已生成 %d 个文章页 + 首页 + sitemap.xml + robots.txt 到 dist/" % len(posts))

def main():
    today = date.today()
    all_posts = load_all()
    days = {p["date"] for p in all_posts}
    if today.isoformat() not in days:
        new = gen_day(today, 12)
        all_posts = new + all_posts
        if len(all_posts) > 600:
            all_posts = all_posts[:600]
        save_all(all_posts)
        print("今日新增 %d 篇，总计 %d 篇" % (len(new), len(all_posts)))
    else:
        print("今日已生成，跳过。总计 %d 篇" % len(all_posts))
    build(all_posts)

if __name__ == "__main__":
    main()
