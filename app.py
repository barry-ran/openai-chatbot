import openai
import streamlit as st
from streamlit_chat import message

# streamlit没有回调函数机制，每次用户交互都会从头到尾执行一遍app.py代码
# 所以需要用session_state来保存上一次的交互结果

# openai api
#openai.api_key = st.secrets['api_secret']
def generate_response(prompt):
    pre_prompt = [        
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    pre_prompt.extend(prompt)
    completions = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=pre_prompt,
        temperature=0.7,
    )
    
    message = completions.choices[0].message.content
    return message

# 测试cache(全局缓存，和会话无关，无论会话刷新多少次，只要参数不变，返回值不变，都是不会重复执行)
# https://docs.streamlit.io/library/advanced-features/caching
@st.cache_data
def test_cache(p1):
    print("***********test cache***********")
    return p1

test_cache("test")

# 测试session_state(会话缓存，和会话相关)
# 普通用户交互导致的rerun不会清空session_state，只有浏览器刷新或者新tab打开网页才会清空
# https://docs.streamlit.io/library/api-reference/session-state
if 'test_session_state' not in st.session_state:
    print("not in session_state")
    st.session_state['test_session_state'] = "data"
else:
    print("session_state")    

# 缓存
if 'ai_assistant' not in st.session_state:
    st.session_state['ai_assistant'] = []

if 'user' not in st.session_state:
    st.session_state['user'] = []

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

if 'cur_input' not in st.session_state:
    st.session_state['cur_input'] = ""

# 开始布局UI
st.title("🤖 chatBot : openAI GPT-3 + Streamlit")

openai.api_key = st.text_input("input openai api key: ","")    

# streamlit是顺序执行过程边执行边显示
# 代码逻辑肯定是先执行recv获取用户输入，再执行show显示结果，这样就先显示recv再显示show
# 但是我想show显示在上面，recv显示在下面，所以要用container来实现行布局，调整recv和show的顺序
# 补充：使用st.empty()占位也可以实现乱序插入元素的效果 https://docs.streamlit.io/knowledge-base/using-streamlit/insert-elements-out-of-order
show_container = st.container()
recv_container = st.container()

# 接收用户输入区域
with recv_container:
    def input_update():
        # 获取输入并清空输入框
        st.session_state.cur_input = st.session_state.input        
        st.session_state.input = " "
    
    # 只有第一次运行返回默认值，后面的运行返回用户输入的内容
    st.text_input("input your question: ", "", key="input", on_change=input_update)

print("cur_input: ", st.session_state['cur_input'])

# 生成并保存聊天记录 
if st.session_state.cur_input:    
    message_request = st.session_state.chat_history
    message_request.append({"role": "user", "content": st.session_state.cur_input})

    print("generate response begin")
    output = generate_response(message_request)
    print("generate response end")
    st.session_state.user.append(st.session_state.cur_input)
    st.session_state.ai_assistant.append(output)

    st.session_state.chat_history.append({"role": "user", "content": st.session_state.cur_input})
    st.session_state.chat_history.append({"role": "assistant", "content": output})

    if len(st.session_state.chat_history) > 10:
        st.session_state.chat_history = st.session_state.chat_history[-10:]
    
    st.session_state['cur_input'] = ""

# 聊天记录显示区域
with show_container:
    if st.session_state['ai_assistant']:
        for i in range(0, len(st.session_state['ai_assistant'])):
            message(st.session_state['user'][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["ai_assistant"][i], key=str(i) + '_ai_assistant')

