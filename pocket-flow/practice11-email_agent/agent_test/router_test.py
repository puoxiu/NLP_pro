from dotenv import load_dotenv

from flow import create_flow

load_dotenv()


test_emails = [
    # 1. ignore（营销广告）
    {
        "email_sender": "marketing@shoppingsite.com",
        "email_title": "【限时特惠】新款电子产品低至5折，点击抢购！",
        "email_content": "亲爱的用户，本周我店推出年度大促，手机、电脑等产品全场5折起，更有满减券可领！点击下方链接立即选购，错过再等一年！https://www.shoppingsite.com/promo"
    },
    # 2. ignore（无关闲聊）
    {
        "email_sender": "oldclassmate@example.com",
        "email_title": "好久不见，最近过得怎么样？",
        "email_content": "嗨，还记得我吗？大学毕业后就没联系了，最近看你朋友圈好像换工作了？有空聚聚聊聊天呀~ 不着急回复，忙的话就算啦"
    },
    # 3. notify（团队通知）
    {
        "email_sender": "team_leader@company.com",
        "email_title": "【通知】本周部门例会时间调整",
        "email_content": "各位同事，原定于周五下午3点的部门例会调整为周五上午10点，地点不变（3楼会议室）。请大家提前准备周报，无需回复，收到请知悉。"
    },
    # 4. notify（系统维护提醒）
    {
        "email_sender": "it_support@company.com",
        "email_title": "【提醒】今晚23点将进行OA系统维护",
        "email_content": "为提升系统稳定性，IT部门计划于今晚23:00-次日01:00对OA系统进行维护，期间系统可能无法登录。请大家提前处理相关工作，无需回复，如有紧急问题联系IT支持：123456。"
    },
    # 5. notify（请假告知）
    {
        "email_sender": "colleague@company.com",
        "email_title": "【请假通知】下周一我将请假一天",
        "email_content": "各位，因个人事务，下周一（8月11日）我将请假一天，期间我的工作由小李临时接手。如有紧急问题可联系小李：xiaoli@company.com。无需回复，特此告知。"
    },
    # 6. respond（工作问题咨询）
    {
        "email_sender": "new_employee@company.com",
        "email_title": "请教关于报销流程的问题",
        "email_content": "您好，我是新来的员工小王，想请教一下差旅费报销需要准备哪些材料？报销单是在线填写还是纸质版？麻烦您有空时回复一下，谢谢！"
    },
    # 7. respond（会议请求）
    {
        "email_sender": "client@partner.com",
        "email_title": "关于合作方案的讨论，想约个会议",
        "email_content": "您好，我们对上次讨论的合作方案有一些细节想进一步沟通，请问您本周三或周四下午有空吗？希望能约个30分钟的线上会议，麻烦您告知方便的时间，我来安排会议链接。"
    },
    # 8. respond（文件确认）
    {
        "email_sender": "project_manager@company.com",
        "email_title": "请确认这份项目进度表是否准确",
        "email_content": "附件是我整理的项目最新进度表，其中标注了延期的任务和原因。请您核对是否准确，若有问题请在今天下班前回复我，以便我调整后续计划，谢谢！"
    },
    # 9. respond（任务协作催促）
    {
        "email_sender": "teammate@company.com",
        "email_title": "麻烦提供一下你负责的模块测试数据",
        "email_content": "咱们的项目明天要进行联调，需要你负责的用户模块测试数据来做兼容性测试。麻烦你今天下午3点前发给我可以吗？如果有困难请告诉我，我来协调时间，谢谢！"
    },
    # 10. respond（紧急事项处理）
    {
        "email_sender": "customer@example.com",
        "email_title": "系统使用时遇到错误，无法提交订单",
        "email_content": "您好，我在使用贵公司的系统提交订单时，点击“确认”后一直显示错误代码E502，尝试多次都无法解决。这是一个紧急订单，麻烦您尽快帮忙看看是什么问题，我的联系方式：138xxxx8888，盼复！"
    }
]


def router_test():
    flow = create_flow()
    
    for email in test_emails:
        shared = email
        flow.run(shared=shared)