from pocketflow import Node
import yaml
import re
from utils.call_llm import call_llm


class Router(Node):
    def prep(self, shared):
        return shared['email_sender'], shared['email_title'], shared['email_content']
    

    def exec(self, prep_res):
        email_sender, email_title, email_content = prep_res

        prompt = f"""
你是专业的邮件分类助手，负责根据邮件内容判断处理方式。请严格遵循以下规则，对邮件进行分类并给出推理过程。

### 核心分类规则
请根据邮件的发件人、主题、正文内容，从以下三类中选择最适合的处理方式：
- **ignore**：适用于营销广告、垃圾邮件、与工作无关的闲聊（如纯寒暄、无关活动邀请）等，无需任何关注或处理的邮件。
- **notify**：适用于需要知晓但无需回复的信息，例如：团队成员oa通知、公司重要公告（如制度更新）、系统维护提醒、会议纪要抄送等。
- **respond**：适用于需要直接回复或采取行动的内容，例如：同事的工作问题咨询、客户的需求沟通、会议时间/地点确认请求、任务协作催促等。

### 待分析邮件信息
发件人：{email_sender}
邮件主题：{email_title}
邮件正文：{email_content}

### 推理要求
请结合上述分类规则，详细分析该邮件为何属于某一类别（需说明具体匹配的规则内容，如“邮件正文提到‘请确认周五会议时间’，符合respond中‘会议请求需要回复’的规则”）。

### 输出格式
请严格按照以下YAML格式返回结果，不得添加额外内容：

```yaml
reason: |
    <此处填写推理过程，需换行时用4个空格缩进>
answer: <此处填写分类结果，只能是ignore/notify/respond中的一个>

        """
        print("=" * 60)
        print("正在分析邮件类别...")
        res = call_llm(prompt)

        yaml_content = re.search(r'```yaml(.*?)```', res, re.DOTALL).group(1).strip()
        data = yaml.safe_load(yaml_content)
        reason = data.get('reason', '')
        answer = data.get('answer', '')
        return reason, answer
    

    def post(self, shared, prep_res, exec_res):
        print(f"分类结束, 类别为{exec_res[1]}...")
        # print(exec_res[1])
        shared['reason'] = exec_res[0]
        shared['answer'] = exec_res[1]

        match shared['answer']:
            case 'ignore':
                return 'ignore'
            case 'notify':
                return 'notify'
            case 'respond':
                return 'respond'
            

class Ignore(Node):
    def prep(self, shared):
        return shared['reason'], shared['answer']
    

    def exec(self, prep_res):
        # 日志记录、输出打印、数据入库等操作
        
        return 
    
    def post(self, shared, prep_res, exec_res):
        return 

class Notify(Node):
    def prep(self, shared):
        return shared['reason'], shared['answer']
    

    def exec(self, prep_res):
        # 日志记录、输出打印、数据入库等操作
        
        return 
    
    def post(self, shared, prep_res, exec_res):
        return 


# 需要回复节点
# 同时，需要判断是否需要：添加todolist、rag搜索、 执行输入，还是直接回复
class Respond(Node):
    def prep(self, shared):

        return shared['reason'], shared['answer']
    

    def exec(self, prep_res):
        
        return 
    
    def post(self, shared, prep_res, exec_res):
        return 
    
