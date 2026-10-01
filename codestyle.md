# Backend Code Style

## 标准来源

本项目后端代码主要参考：

- PEP 8 — Style Guide for Python Code: https://peps.python.org/pep-0008/
- PEP 257 — Docstring Conventions: https://peps.python.org/pep-0257/

## 约定

1. 使用 4 个空格缩进，不使用 Tab。
2. 函数、变量使用 `snake_case`；类名使用 `PascalCase`；常量使用 `UPPER_CASE`。
3. 单个函数只承担清晰职责，表达式解析、数据库、HTTP API 分模块实现。
4. 公共模块、类和关键函数使用简洁 docstring。
5. 行宽尽量控制在 88–100 字符以内，复杂表达式使用括号换行。
6. 使用参数化 SQL，不把用户输入拼接进 SQL 字符串。
7. 对外 API 返回统一 JSON：成功包含 `success: true`，失败包含 `success: false`、`code`、`message`。
8. 捕获可预期的业务异常，不使用空 `except`。
9. 禁止使用 `eval`、`exec` 或任何把用户表达式当 Python 程序执行的方式。
10. 新功能应补充 `unittest` 测试；后端运行时只使用 Python 标准库，减少环境依赖。
