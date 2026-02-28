# miniThincaServer (Python)
让你的 SEGAY 机器能刷上 PASELI（Python 版）。

## 运行方式
1. 安装 Python 3.10+
2. 启动服务：
```bash
python mini_thinca_server.py
```
或指定 IP/端口：
```bash
python mini_thinca_server.py 192.168.1.10 --port 80
```

## VFD 模拟器
可选安装：
```bash
pip install pyserial
python vfd_emu.py COM11
```

## 配置机台
- 写入 `thincaMod4.mct` 到 Mifare 卡。
- 修改 `env.json` 的 `root_endpoint` 为 `http://你的IP/thinca`。
- 修改 `resource.xml` 的 `/thincaResource/common/commonPrimaryUri` 为 `http://你的IP/thinca/common-shop/`。

## 路由兼容性
已保留原 C# 版本核心路由：
- `/thinca`
- `/thinca/terminals`
- `/thinca/common-shop/initauth.jsp`
- `/thinca/common-shop/emlist.jsp`
- `/thinca/common-shop/stage2`
- `/thinca/common-shop/emstage2`
- `/thinca/emoney/{brand}/{termSerial}/{method}`

## 说明
本仓库已迁移为 Python 代码结构，核心逻辑位于 `mini_thinca_lib/`，服务入口为 `mini_thinca_server.py`。
