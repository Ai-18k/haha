# _*_ coding:UTF-8 _*
import os
import uiautomation as auto
import time

# 打开微信（假设微信已经登录并在运行）
# 如果微信没有打开，可以通过 os.system() 打开
os.system("start E:\wechat\WeChat.exe")

# 查找微信主窗口
wechat_window = auto.WindowControl(searchDepth=1, Name="微信")


# 将微信窗口置于前台
wechat_window.SetActive()

# 查找左侧的联系人列表区域
contact_list = wechat_window.ListControl(foundIndex=1)

# 找到第一个联系人（假设要与第一个联系人互动）
first_contact = contact_list.ListItemControl(foundIndex=1)

first_contact.Click()

# 等待聊天窗口加载
time.sleep(1)

# 查找消息显示区域
message_area = wechat_window.ListControl(foundIndex=2)

# 获取最新消息（假设消息显示为文本形式）
# 这里我们获取最后一条消息的内容
last_message = message_area.GetChildren()[-1].Name

# 打印获取的消息
print(f"Received message: {last_message}")

# 在输入框中输入回复

input_control = wechat_window.EditControl(foundIndex=2)
input_control.Click()
input_control.SendKeys("This is an automated reply.")

# 发送消息（假设按 Enter 发送）
input_control.SendKeys('{Enter}')

# 打印回复完成
print("Reply sent!")




