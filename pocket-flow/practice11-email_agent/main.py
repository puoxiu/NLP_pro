from dotenv import load_dotenv

from flow import create_flow

load_dotenv()

def main():
    flow = create_flow()
    shared = {
        'email_sender': 'hris',
        'email_title': '请查收《离职指引手册》，跟进您的离职流程',
        'email_content':'公司将采用电子形式与您签订离职材料，您将收到材料签署短信及邮件链接，届时请您通过短信/邮件链接完成文件签署。签署完成并待公司审核盖章后，公司将发送电子版证明到您个人邮箱，正编电子签署指引请见附件3，实习生电子签署指引请见附件4，党组织关系转出指引请见附件5。附：根据《民法典》《电子签名法》等相关规定，电子签名签订的电子文件与书面文件具有同等法律效力。若您对电子签署有疑问或不接受电子签署，请联系人力资源部。谢谢！'
    }

    flow.run(shared=shared)


def test():
    from agent_test.router_test import router_test

    router_test()
    


if __name__ == '__main__':
    test()
