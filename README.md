# 832402216 Calculator Backend

后端项目：软件工程实践第一次作业——前后端分离计算器。

- 学生：刘鉴浩（Liu Jianhao）
- 学号：832402216
- 技术栈：Python 3.10+ / WSGI / SQLite / unittest
- 运行依赖：**仅 Python 标准库，无第三方运行依赖**
- 核心原则：浏览器不计算最终结果；表达式解析、异常处理、历史持久化全部在后端完成。

## 功能

- 四则运算：`+ - * /`
- 复合表达式与运算符优先级
- 括号
- 小数
- 一元正负号（如 `-5 + 8`、`3 * -2`）
- 非法表达式检测
- 除零检测
- SQLite 持久化计算历史
- 查询、搜索、单条删除、清空历史
- 统计历史总数
- CORS 支持
- 不使用 `eval` / `exec`

## 项目结构

```text
832402216_calculator_backend/
├── src/
│   ├── app.py          # WSGI HTTP/JSON API
│   ├── database.py     # SQLite 数据访问
│   ├── parser.py       # 安全递归下降表达式解析器
│   └── run.py          # 本地开发入口
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   └── test_parser.py
├── requirements.txt
├── README.md
└── codestyle.md
```

## 本地启动

无需安装 Flask 或其他第三方包：

```bash
cd 832402216_calculator_backend
python src/run.py
```

默认地址：`http://127.0.0.1:5000`

健康检查：`GET http://127.0.0.1:5000/health`

SQLite 文件默认自动创建在：`data/calculator.db`。

## API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | 健康检查 |
| `POST` | `/api/calculate` | 后端解析并计算表达式，成功后保存历史 |
| `GET` | `/api/history` | 查询历史记录，可用 `?search=关键词` |
| `DELETE` | `/api/history/<id>` | 删除指定历史 |
| `DELETE` | `/api/history` | 清空全部历史（扩展功能） |
| `GET` | `/api/stats` | 查询历史数量（扩展功能） |

计算请求示例：

```json
{
  "expression": "(1+2)*3"
}
```

成功响应示例：

```json
{
  "success": true,
  "expression": "(1+2)*3",
  "result": "9",
  "history": {
    "id": 1,
    "expression": "(1+2)*3",
    "result": "9",
    "created_at": "2026-10-01T12:00:00+00:00"
  }
}
```

## 环境变量

| Name | Default | Meaning |
|---|---|---|
| `CALCULATOR_DB_PATH` | `data/calculator.db` | SQLite 数据库文件位置 |
| `ALLOWED_ORIGINS` | `*` | CORS 允许的前端来源，多个来源用逗号分隔 |

正式部署时，建议把 `ALLOWED_ORIGINS` 改成你的 GitHub Pages 地址。

## 自动测试

```bash
python -m unittest discover -s tests -v
```

测试覆盖核心表达式、优先级、括号、小数、一元正负号、除零、非法输入、真实 HTTP API、历史写入和删除。

## PythonAnywhere 部署

1. 在 PythonAnywhere 创建账号并打开 Bash Console。
2. 执行：

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/832402216_calculator_backend.git
```

3. 打开 **Web** → **Add a new web app** → 选择 **Manual configuration** → Python 3.x。
4. 打开该 Web App 的 **WSGI configuration file**，将内容中的项目部分改为：

```python
import os
import sys

project_src = '/home/YOUR_PYTHONANYWHERE_USERNAME/832402216_calculator_backend/src'
if project_src not in sys.path:
    sys.path.insert(0, project_src)

# 可选：上线后把 * 换成你的 GitHub Pages 域名
os.environ['ALLOWED_ORIGINS'] = '*'

from app import application
```

5. 点击 **Reload**。
6. 打开：

```text
https://YOUR_PYTHONANYWHERE_USERNAME.pythonanywhere.com/health
```

看到 `success: true` 即部署成功。
7. 把前端 `src/config.js` 的线上 API 地址改成该域名。

> SQLite 位于 PythonAnywhere 用户目录的持久化文件系统中，因此页面刷新、浏览器重开以及 Web App Reload 后，历史仍保留。

## 前后端连接

本地开发时，前端 `config.js` 自动使用 `http://127.0.0.1:5000`。
线上部署时，把 `config.js` 中的 `https://YOUR_USERNAME.pythonanywhere.com` 替换为真实后端域名，再推送前端仓库并启用 GitHub Pages。
