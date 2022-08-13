# SaobbyCAPTCHARelease
Saobby人机验证  
代码下下来之后你需要:  
1. 按照`requirements.txt`安装依赖
2. 在`captcha-bg`目录中添加验证码背景图片,可添加多个,文件名需要为`序号.png`(序号从1开始)(里面默认有两个文件,你要删掉换成你自己的)
3. 在`captcha-font`目录中添加生成验证码所需的字体,可添加多个,文件名需要为`序号.ttf`(序号从1开始)(里面默认有两个文件,你要删掉换成你自己的)
4. 在`config.py`中修改配置
5. 运行`server.py`,浏览器访问`localhost:9999`即可看到验证码窗口
