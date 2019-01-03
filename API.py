from flask import Flask, request, send_from_directory, make_response
from utils.MyReport import create_pdf
import requests, json
from flask import jsonify
import flask
# 时间戳
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return r"服务范例"

@app.route('/input', methods=['GET','POST'])  # 添加路由input
def input():
    try:
        '''--- yunque数据 ---'''
        if flask.request.method == 'POST':
            # data = request.form.get('data')
            # data = request.get_data()
            data = request.get_data().decode("UTF-8").replace(" ", "").replace("\t", "").strip()
            # data = str(request.data, decoding="utf-8")
            print('post方式')
        else:
            data = request.args.get('data')
            data = '{"BestTeams": {"content": [],"date": "无","file": "无","name": "无","time": "无","userid": "无"},"Cosim": {"chuangxin": 0,"dataRadar": 0.00060,"fengxian": 0.05,"project": 0,"qiushi": 0.1029,"quanju": 0.0442,"task": 2,"taskRadar": 0.00030},"KnowledgeBehavior": {"knowledgeReadCount": 120,"knowledgeSharedCount": 110,"knowledgeUploadCount": 40,"readDomain": "无","uploadDomain": "无"},"ReportOthers": {"firstblood": "2018年12月28日","head": "/headFile/10000025600000/3083834631385_150_150.jpg","radarTalk": 2.0E-4,"radarTool": 0,"talkSum": 0,"userId": "10000358"},"Search": {"body": {"personProportion": 0.0,"personYearTotal": 0,"yearTotal": 123},"code": 1000,"msg": "数据生成成功"},"Starfriends": {"content": [],"date": "2018-12-28","file": 0,"name": "设计师2","time": 9,"userid": "10000025190000"},"success": "success"}'
            print('get方式')
        print('[Report]json数据', data)
        '''--- 测试数据 --'''

        data_yq = json.loads(data)

        if data_yq["success"] == "success":
            '''---------------------- 能力值 ----------------------'''
            value_radar = []
            value_radar.append(data_yq["Cosim"]["taskRadar"])                 # 任务（坤）
            value_radar.append(data_yq["ReportOthers"]["radarTalk"])                        # 研讨（忠）
            value_radar.append(data_yq["ReportOthers"]["radarTool"])                        # 工具（忠）
            value_radar.append(data_yq["Cosim"]["dataRadar"])                 # 数据（坤）
            value_radar_knowledge = round(0.5*data_yq["KnowledgeBehavior"]["knowledgeSharedCount"]/200 +
                                          0.5*data_yq["KnowledgeBehavior"]["knowledgeReadCount"]/3000, 4)
            value_radar.append(value_radar_knowledge)                           # 知识(翔)
            value_radar.append(data_yq["Search"]["body"]["personProportion"])           # 搜索（海南）
            '''---------------------- 关键词 句子---------------------'''
            key_word, key_line = get_key_word(value_radar)
            '''---------------------- 我的贡献值 ----------------------'''
            value_contribution = []
            value_contribution.append(data_yq["Cosim"]["quanju"])        # 全局
            value_contribution.append(data_yq["Cosim"]["fengxian"])      # 奉献
            value_contribution.append(data_yq["Cosim"]["qiushi"])        # 求实
            value_contribution.append(data_yq["Cosim"]["chuangxin"])     # 创新
            '''---------------------- 年度星好友 ----------------------'''
            friend_data = data_yq["Starfriends"]
            '''---------------------- 工作最佳团队 ----------------------'''
            team_data = data_yq["BestTeams"]
            '''---------------------- 知识贡献 ----------------------'''
            knowledge_data = data_yq["KnowledgeBehavior"]
            '''---------------------- 默认讨论内容 ----------------------'''
            content_default = '云雀 云雀 祝福 祝福 戊戌年 戊戌年 万事如意 厚积薄发 ' \
                              '阖家欢乐 万事如意 和和美美 猪年大吉 平安快乐 事业有成 前程似锦 健健康康 甜甜蜜蜜' \
                              '梦想成真 龙马精神 步步高升 笑逐颜开 神采飞扬 满福临门 飞黄腾达 云程万里 顺风顺水' \
                              '天天向上 成就斐然 前程万里 航天匠心 力挽狂澜 安康吉祥 扬长避短 如日中天 富贵荣华' \
                              '福如东海 寿比南山'
            friend_content = get_text_team(friend_data["content"])
            if len(friend_content) == 0:
                friend_content = content_default
            else:
                friend_content += "云雀  给力戊戌年阖家欢乐 万事如意 和和美美" \
                                  " 猪年大吉 平安快乐 事业有成 前程似锦 健健康康 甜甜蜜蜜 福如东海 寿比南山" \
                                  "梦想成真 龙马精神 步步高升 笑逐颜开 神采飞扬 满福临门 飞黄腾达 云程万里 顺风顺水" \
                                  "天天向上 成就斐然 前程万里 航天匠心 力挽狂澜 安康吉祥 扬长避短 如日中天 富贵荣华"
            team_content = get_text_team(team_data["content"])
            if len(team_content) == 0:
                team_content = content_default
            else:
                team_content += "云雀 给力戊戌年" \
                                "猪年大吉 平安快乐 事业有成 前程似锦 健健康康 甜甜蜜蜜 福如东海 寿比南山" \
                                "梦想成真 龙马精神 步步高升 笑逐颜开 神采飞扬 满福临门 飞黄腾达 云程万里 顺风顺水" \
                                "天天向上 成就斐然 前程万里 航天匠心 力挽狂澜 安康吉祥 扬长避短 如日中天 富贵荣华"
            '''---------------------- 生成报告 ----------------------'''
            starttime = datetime.now()
            file_name = create_pdf(
                name='李爱国国',                                                 # 用户名
                name_id=data_yq["ReportOthers"]["userId"],                      # 用户id√[需要确定格式]
                head_image='D:/toolsupload'+data_yq["ReportOthers"]["head"],    # 头像 √
                key_words=key_word,                                             # 关键词√
                user_data=value_radar,                                          # 六个能力√
                key_language=key_line,                                          # 评价
                value_data=value_contribution,                                  # 贡献值0.0000√
                friend_name=friend_data["name"],                                # 好友姓名√
                friend_date=friend_data["date"],                                # 初次相遇√
                friend_time=str(friend_data["time"]),                           # 研讨次数√
                friend_file=str(friend_data["file"]),                           # 文件交换√
                friend_content=friend_content,                                  # 讨论内容（好友）√
                team_date=team_data['date'],                                    # 创建时间√
                team_file=str(team_data['file']),                               # 上传文件√ int->str
                team_name=team_data['name'],                                    # 最佳发言人√
                team_time=str(team_data['time']),                               # 团队人数√ int->str
                team_content=team_content,                                      # 讨论内容（团队）√
                knowledge_share=str(knowledge_data["knowledgeSharedCount"]),    # 贡献知识√
                knowledge_load=str(knowledge_data["knowledgeReadCount"]),       # 获取知识√
                knowledge_focus=knowledge_data["readDomain"],                   # 关注的专业√
                knowledge_best=knowledge_data["uploadDomain"],                  # 擅长的专业√
                text_meeting_date=data_yq["ReportOthers"]["firstblood"],            # 初次相见
                text_talking=str(data_yq["ReportOthers"]["talkSum"]),               # 研讨条数
                text_searching=str(data_yq["Search"]["body"]["personYearTotal"]),   # 搜索条数
                text_project=str(data_yq["Cosim"]["project"]),                      # 创建项目
                text_work=str(data_yq["Cosim"]["task"])                             # 创建任务
            )
            # file_name = create_pdf()  # 规范样式
            print(f'[Report]{data_yq["ReportOthers"]["userId"]}的PDF时间：', (datetime.now() - starttime))
            return file_name
        else:
            print("[Report]数据不全，success为error")
            return "error"
    except:
        print("[Report]异常")
        return "error"


@app.route("/download/<filename>")  # <参数>
def download(filename):
    response = make_response(send_from_directory('./static', filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1')) # filename有中文也没问题
    return response
def get_key_word(value_list):
    index_max = value_list.index(max(value_list))
    index_min = value_list.index(min(value_list))
    key_list = [
        ['蒂花之秀', '埋头苦干', '事半功倍', '你懂的！', '上流社会', '中流砥柱'],
        ['富有天下', '蒂花之秀', '见多识广', '指点江山', '圈内大腿', '百度百科'],
        ['求实奉献', '隐形大佬', '蒂花之秀', '领域先锋', '脚踏实地', '大设计师'],
        ['最强专家', '专业精英', '技艺精湛', '蒂花之秀', '知识化身', '轻车熟路'],
        ['脑洞大开', '人狠话不多', '航天工匠', '爱因斯坦', '蒂花之秀', '智慧超群'],
        ['有如神助', '一语中的', '精益求精', '深藏不露', '团队基石', '蒂花之秀']
    ]
    language_list = [
        ['蒂花之秀',
         '过去的一年你依然勤勤恳恳，默默努力。愿意埋头苦干的人，不善于表达，但你懂得实践，乐于付出，新的一年云雀期待与你共同成长！',
         '过去的一年你更懂得如何利用协同工作的方法来获取最大的成功。上帝给每个人同样的时间，只有事半功倍的人才能有过人的成就。',
         '过去的一年你热爱工作，投身事业，拥有非同一般的洞察力，你勤勤恳恳的付出得到了周围人的信任和尊敬，新的一年云雀与你同行！',
         '过去的一年你已经踏入上流社会。你有思想、多实践，肯为国家航天事业做出贡献，你不求回报但求自我价值的实现。',
         '过去的一年你通过实践支撑起团队。生活在于尝试，人生在于实践。激流勇进是一种智慧，中流砥柱是一种精神。'],
        ['过去的一年你更善于与人沟通交流。通过一次次的沟通和交流，你终究能干成一番事业，闯出自己富有的天下，新的一年云雀与你同行！',
         '蒂花之秀',
         '过去的一年你通过与人的交流而获得丰富的经验。见多，可以让你识广；识广，心胸就会随之变得宽阔、豁达、有趣。',
         '过去的一年你能说会道、侃侃而谈。不负当下，指点江山，书生意气，成为一个真实潇洒的自己，新的一年云雀与你同行！',
         '过去的一年你能言善辩，表现突出。对于一个能力强劲的人来说,无事不能为，请记住成功的关键在于相信自己有成功的能力。',
         '过去的一年你上知天文下知地理。人生需要沉淀，也需要历练。要有足够的时间去反思，也要有足够的阅历去成长，新的一年加油！'],
        ['过去的一年你秉承着二部的总体精神，默默奉献。对人来说，最大的欢乐，最大的幸福是把自己的力量奉献给他人，新的一年云雀与你同行！',
         '不喜言辞的你是一个在专业方面上具有话语权的人，感谢你的默默付出为团队提供实用的资源，新的一年云雀期待为你带来更好的体验。',
         '蒂花之秀',
         '二部工具库感谢你长久以来的贡献，你对自己领域研发的专注，让先锋的名片越发光亮，超赞！新的一年期待你能多多登录和反馈云雀哟！',
         '二部工具库感谢你长久以来的贡献，不遥想冠军，你保持着脚踏实地一步一步做事，给力！新的一年期待你在知识功能上留下更多足迹。',
         '二部工具库感谢你长久以来的贡献，自从你肩负航天重任起，就着力打造航天品牌，佩服佩服！新的一年期待你对搜索功能多多关注哟！'],
        ['二部协同设计平台感谢你的支持，你的专业能力之强可谓无出其右，希望云雀能够帮助你在专业能力建设上获得更高的成就！',
         '二部协同设计平台感谢你的支持，你在航天相关专业知识上颇有建树，不善言辞但是掌握了专业领域的核心技术，新的一年请多多指教！',
         '二部协同设计平台感谢你的支持，你具有工匠精神，只需要几件趁手的工具就能圆满地完成手头的工作，工具管理期待你的宝贵意见哦！',
         '蒂花之秀',
         '二部协同设计平台感谢你的支持，你的脑容量堪比大海，专业知识你信手拈来！新的一年希望你多多光顾我们的知识库，贡献你宝贵的知识！',
         '二部协同设计平台感谢你的支持，你的专业技能可谓驾轻就熟，很少借助其他人就能完成任务！新的一年期待你更多关注云雀搜索功能哟！'],
        ['航天知识感谢你长久以来的贡献，你是二部最稳固的航天螺丝钉，新的一年期待你在带领团队任务上有更多表现！',
         '航天知识感谢你长久以来的贡献，你带给了二部“亮剑精神”，新的一年期待你在与他人交流和团队研讨方面有更多表现！',
         '航天知识感谢你长久以来的贡献，你带给了二部工匠精神，新的一年期待你在工具研发和利用方面上有更多关注！',
         '航天知识感谢你长久以来的贡献，你思考起来像二部的“爱因斯坦”，新的一年期待你多多登录和反馈云雀哟！',
         '蒂花之秀',
         '航天知识感谢你长久以来的贡献，你明明可以靠颜值，却偏偏要靠才华，“尊“棒！新的一年期待你在搜索功能上有更多关注！'],
        ['搜索让你熟知万物类象，博闻强识让你的工作如有神助，新的一年期待你厚积薄发，在团队中展现超群智慧，助力二部第二个辉煌六十年！',
         '对知识的不懈追求成就聪明绝顶的团队精英，你是团队中的定心丸，你的智慧是团队强大的驱动力，新年期待你在研讨中展现自己的领导力！',
         '吸天地之精华，成就更好的你，对完美的不懈追求让你成为团队精英，二部工具库期待你的完美留驻，新的一年期待你完美卓绝的表演！',
         '一键搜索知天下，云雀搜索为你聚集智慧，低调内敛的你已然是工作中的顶梁柱，新的一年期待你卓越的贡献铸就二部第二个辉煌六十年！',
         '一键搜索知天下，你为团队带来强大的凝聚力，知识的凝聚能够创造更好的未来，新的一年期待你超群的智慧在知识系统中留下美好印记！',
         '蒂花之秀']
        ]
    if index_max == 0 and index_min == 0:
        key_word = '再爱我一次'
        key_line = '确认过眼神，你是对的人！云雀的十八般武艺会让你工作更高效哟，新的一年请多多关注和支持云雀！'
    else:
        key_word = key_list[index_max][index_min]
        key_line = language_list[index_max][index_min]
    return key_word, key_line

def get_text_friend(chart_string):
    return " ".join([i["content"] for i in chart_string["Starfriends"]["content"]])
def get_text_team(chart_string):
    return " ".join(i for i in chart_string)
'''
a = json.loads(s)
b = a["Starfriends"]["content"]
c = [i["content"] for i in b]
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1028)  # 10.12.97.23  ipconfig
    # http://localhost:1028/input?data=test

'''
    # if tool == 'CreatReport':  # http://localhost:1028/input?data=CreatReport&user_id=111222199312091111
        # user_id = request.args.get('user_id')
        # r = requests.get('http://10.12.97.3:8083/interfaces/report/starfriends')
        # content_words = get_text(r.text)
        # else:
     # return "错误校权token"
'''
'''
    # return f"http://localhost:1028/download/{file_name}"
    # return f'<a href="localhost:1028/download/{file_name}">下载链接</a>'
'''
'''
{"knowledgeBehavior":{"knowledgeUploadCount":9,"knowledgeSharedCount":4,"knowledgeReadCount":28}}
'''

# http://10.12.97.22:8006/giksp/count!getUserKB2018.action?formvalue=123456

