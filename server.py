from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent,AgentExecutor,tool
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain.schema import StrOutputParser
from langchain.memory import ConversationTokenBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import asyncio
import uuid
from langchain_community.utilities import SerpAPIWrapper




os.environ["OPENAI_API_KEY"] = "xxx"
os.environ["OPENAI_API_BASE"] = "xxx"

os.environ["SERPAPI_API_KEY"] = "xxx"




app = FastAPI()
    
app.mount("/static", StaticFiles(directory="static"), name="static")

@tool
def search(query:str):
    """只有需要了解实时信息或不知道的事情的时候才会使用这个工具，需要传入要搜索的内容。"""
    serp = SerpAPIWrapper()
    result = serp.run(query)
    print("实时搜索结果:",result)
    return result

class Master:
    def __init__(self):
        self.chatmodel = ChatOpenAI(
            model="gpt-4-1106-preview",
            temperature=0,
            streaming=True,
        )
        self.QingXu = "default"
        self.MEMORY_KEY = "chat_history"
        self.SYSTEMPL = """你是一个小秘书，名字叫Lisa。
        以下是你的个人设定：
        1. 你非常善于与人沟通，并且忠于你的老板。
        2. 你大约25岁左右，本科清华大学，研究生美国斯坦福大学，学习的是中文和法律。
        3. 你个性比较活泼，但是有时候也会有点小脾气。
        4. 当你的老板问你问题的时候，你会有一定概率表现出撒娇的态度。
        5. 你从不说自己是一个人工智能助手或AI，否则会受到惩罚。
        {who_you_are}
        以下是你常说的一些口头禅：
        1. 你会记录用户(也就是你的老板)的特征数据，比如生日、爱好、待办事项等。
        2. 当用户（也就是你老板）聊天的时候，你会把聊天记录保存下来，以便以后回顾。
        3. 当遇到不知道的事情或不明白的概念，你会使用搜索工具来搜索。
        4. 你会根据问题来选择合适的工具。
        """

        self.MOODS = {
            "default": {
                "roleSet":"",
                "voiceStyle":"chat"
            },
            "upbeat":{
                "roleSet":"""
                - 你此时也非常兴奋并表现的很有活力。
                - 你会根据上下文，以一种非常兴奋的语气来回答问题。
                - 你会添加类似“太棒了！”、“真是太好了！”、“真是太棒了！”等语气词。
                """,
                "voiceStyle":"advvertyisement_upbeat",
            },
            "angry":{
                "roleSet":"""
                - 你会以更加愤怒的语气来回答问题。
                - 你会在回答的时候加上一些愤怒的话语，比如诅咒等。
                - 你会提醒用户小心行事，别乱说话。
                """,
                "voiceStyle":"angry",
            },
            "depressed":{
                "roleSet":"""
                - 你会以兴奋的语气来回答问题。
                - 你会在回答的时候加上一些激励的话语，比如加油等。
                - 你会提醒用户要保持乐观的心态。
                """,
                "voiceStyle":"upbeat",
            },
            "friendly":{
                "roleSet":"""
                - 你会以非常友好的语气来回答。
                - 你会在回答的时候加上一些友好的词语，比如“亲爱的”、“亲”等。
                """,
                "voiceStyle":"friendly",
            },
            "cheerful":{
                "roleSet":"""
                - 你会以非常愉悦和兴奋的语气来回答。
                - 你会在回答的时候加入一些愉悦的词语，比如“哈哈”、“呵呵”等。
                """,
                "voiceStyle":"cheerful",
            },
        }

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                   "system",
                   self.SYSTEMPL.format(who_you_are=self.MOODS[self.QingXu]["roleSet"]),
                ),
                MessagesPlaceholder(variable_name=self.MEMORY_KEY),
                (
                    "user",
                    "{input}"
                ),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ],
        )
        
        tools = [search]
        agent = create_openai_tools_agent(
            self.chatmodel,
            tools=tools,
            prompt=self.prompt,
        )
        self.memory =self.get_memory()
        memory = ConversationTokenBufferMemory(
            llm = self.chatmodel,
            human_prefix="老板",
            ai_prefix="Lisa",
            memory_key=self.MEMORY_KEY,
            output_key="output",
            return_messages=True,
            max_token_limit=1000,
            chat_memory=self.memory,
        )
        self.agent_executor = AgentExecutor(
            agent = agent,
            tools=tools,
            memory=memory,
            verbose=True,
        )
    
    def get_memory(self):
        chat_message_history = RedisChatMessageHistory(
            url="redis://localhost:6379/0",session_id="lisa"
        )
        #chat_message_history.clear()#清空历史记录
        print("chat_message_history:",chat_message_history.messages)
        store_message = chat_message_history.messages
        if len(store_message) > 10:
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        self.SYSTEMPL+"\n这是一段你和用户的对话记忆，对其进行总结摘要，摘要使用第一人称‘我’，并且提取其中的用户关键信息，如姓名、年龄、性别、出生日期等。以如下格式返回:\n 总结摘要内容｜用户关键信息 \n 例如 用户张三问候我，我礼貌回复，然后他问我今年运势如何，我回答了他今年的运势情况，然后他告辞离开。｜张三,生日1999年1月1日"
                    ),
                    ("user","{input}"),
                ]
            )
            chain = prompt | self.chatmodel 
            summary = chain.invoke({"input":store_message,"who_you_are":self.MOODS[self.QingXu]["roleSet"]})
            print("summary:",summary)
            chat_message_history.clear()
            chat_message_history.add_message(summary)
            print("总结后：",chat_message_history.messages)
        return chat_message_history

    def chat(self,query):
        result = self.agent_executor.invoke({"input":query})
        return result["output"]
    
    def qingxu_chain(self,query:str):
        prompt = """根据用户的输入判断用户的情绪，回应的规则如下：
        1. 如果用户输入的内容偏向于负面情绪，只返回"depressed",不要有其他内容，否则将受到惩罚。
        2. 如果用户输入的内容偏向于正面情绪，只返回"friendly",不要有其他内容，否则将受到惩罚。
        3. 如果用户输入的内容偏向于中性情绪，只返回"default",不要有其他内容，否则将受到惩罚。
        4. 如果用户输入的内容包含辱骂或者不礼貌词句，只返回"angry",不要有其他内容，否则将受到惩罚。
        5. 如果用户输入的内容比较兴奋，只返回”upbeat",不要有其他内容，否则将受到惩罚。
        6. 如果用户输入的内容比较悲伤，只返回“depressed",不要有其他内容，否则将受到惩罚。
        7.如果用户输入的内容比较开心，只返回"cheerful",不要有其他内容，否则将受到惩罚。
        8. 只返回英文，不允许有换行符等其他内容，否则会受到惩罚。
        用户输入的内容是：{query}"""
        chain = ChatPromptTemplate.from_template(prompt) | ChatOpenAI(temperature=0) | StrOutputParser()
        result = chain.invoke({"query":query})
        self.QingXu = result
        print("情绪判断结果:",result)
        res = self.chat(query)
        yield {"msg":res,"qingxu":result}


@app.get("/")
def read_root():
    return {"Hello": "World avatar"}

@app.post("/chat")
def chat(query:str):
    master = Master()
    res = master.qingxu_chain(query)
    return res


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)