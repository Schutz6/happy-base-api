# happy-base-api
一款适合程序员的低代码框架，通过自建模块完成项目需求，个性化需求可以单独编写接口实现

### 平台介绍

工程目录介绍
- base 基础工具代码
- core 核心模块代码
- ext 用户扩展代码
- route 路由配置

执行代码介绍
- config.py 配置文件，配置数据库、缓存、存储目录等
- server.py 启动文件
- setup.py 源码编译
- test.py 一些测试代码


### 安装依赖
- 生成requirements.txt文件
- pip freeze > requirements.txt
- 安装requirements.txt依赖
- pip install -r requirements.txt