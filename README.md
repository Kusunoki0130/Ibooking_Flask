# ibooking-flask





windows 下环境需求：

python 版本：3.10

site-packages：

- Flask
- Flask-Login
- geopy
- pytest
- pytest-flask
- pytest-cov（2023.6.2 新增）
- rsa
- SQLAlchemy



启动指令：

1. 单元测试：切换到目录 `ibooking_flask/test`，运行如下指令：

   ```shell
   ......\ibooking_flask\test> pytest
   ```

   若需要输出覆盖率等统计信息：

   ```shell
   ......\ibooking_flask\test> pytest --cov
   ```

2. web后端：切换到目录 `ibooking_flask/ibooking`，运行如下指令：

   ```shell
   ......\ibooking_flask\ibooking> python run.py
   ```

3. 在 Ubuntu 虚拟机中使用 docker 部署 web 后端：

   - 安装 docker 和 docker-compose

   - 切换到目录 `ibooking_flask/docker`，运行如下命令：

     ```shell
     ......\ibooking_flask\docker$ sudo docker-compose up
     ```

     > 从浏览器访问 Web 服务的 ip 为虚拟机的局域网 ip，在 Ubuntu 中使用 ifconfig 找到 ens33 口对应的 ip。

   - 打包镜像，首先使用如下命令找到本地容器使用的镜像 Id：

     ```shell
     ......\ibooking_flask\docker$ sudo docker images
     ```

   - 通过镜像 Id 将其打包成 tar 文件并保存到本地：

     ```shell
     ......\ibooking_flask\docker$ sudo docker save [镜像ID] > ibooking_image.tar
     ```

   - 将本地 tar 格式的文件加载为 docker 镜像：

     ```shell
     ......\ibooking_flask\docker$ sudo docker load < ibooking_image.tar
     ```

   - 根据新导入镜像的 ID 配置其 repository 和 tag

     ```shell
     ......\ibooking_flask\docker$ sudo docker tag [镜像ID] ibooking_image:1.0.0
     ```

   - 在 docker-compose.yaml 中配置镜像：

     ```yaml
     version: "3"
     
     services:
     
       ibooking:
         build: ../ibooking/
         image: ibooking_image:1.0.0
         ports:
           - "5000:5000"
     ```

4. 使用 Devcloud 流水线构建的 docker 镜像部署 web 后端：

   - 从 CodeArt 中选择流水线并运行，待其运行结束

   - 在安装好 docker 的 Ubuntu 虚拟机中，打开命令行并登录容器镜像服务访问凭证，格式为：

     ```shell
     ...$ sudo docker login -u cn-north-4@[Access Key Id] -p [Password] swr.cn-north-4.myhuaweicloud.com
     ```

     > 将 [Access Key Id] 和 [Password] 替换成微信群文件 credentials.csv 中给出的值

   - 拉取 docker 镜像：

     ```shell
     ...$ sudo docker pull swr.cn-north-4.myhuaweicloud.com/fdu-ibooking-team-20/ibooking_image:v1.0.0
     ```

   - 创建一个 docker 容器，并运行该镜像：

     ```shell
     ...$ sudo docker run --name ibooking_devcloud -p 5000:5000 [镜像ID]
     ```

     > [镜像ID] 使用 sudo docker images 查看
     >
     > 从浏览器访问 Web 服务的 ip 为虚拟机的局域网 ip，在 Ubuntu 中使用 ifconfig 找到 ens33 口对应的 ip。
