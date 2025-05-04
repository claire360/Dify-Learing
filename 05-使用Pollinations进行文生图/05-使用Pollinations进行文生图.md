## 05-**使用Pollinations进行文生图**

## 5.1 任务定义

文字生成图片

Pollinations AI是一个基于人工智能的平台，提供多种图像和文本生成的工具。该平台由Pollinations AI团队开发，旨在满足创意工作者、内容创作者和开发者的需求。其核心功能包括图像生成、博客创作和故事编写，所有这些都通过Pollinations和GroqCloud技术实现。Pollinations AI作为一个开源项目，用户无需注册或使用API密钥即可免费使用，并能与各种应用程序、机器人和大型语言模型（LLM）集成。

## 5.2 整体的流程图

创建一个聊天助手，提示词就是以下的提示词。这是比较简单的文生图方法

```
你是一个图像生成助手，请根据我的简单描述，想象并详细描述一幅完整的画面。 然后将你的详细描述翻译成英文，并插入到以下链接的{prompt}部分： ![image](https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&enhance=true&private=true 然后输出生成内容
```

![img](file:///C:\Users\Claire\AppData\Local\Temp\ksohtml88872\wps1.jpg) 

## 5.3 提示

你是一个图像生成助手，请根据我的简单描述，想象并详细描述一幅完整的画面。 然后将你的详细描述翻译成英文，并插入到以下链接的{prompt}部分： ![image](https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&enhance=true&private=true 然后输出生成内容

## 5.4 结束

生成图片

![img](file:///C:\Users\Claire\AppData\Local\Temp\ksohtml88872\wps2.jpg)