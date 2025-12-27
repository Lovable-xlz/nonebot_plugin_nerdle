# nonebot_plugin_nerdle
适用于 Nonebot2 的 nerdle 猜等式插件

# 安装步骤（Windows 环境下，对 Linux 的兼容性未知）
1. 将文件夹 `nonebot_plugin_nerdle` 下载并移动到你的项目所在目录 `.\.venv\Lib\site-packages` 下
2. 打开终端，在项目根目录输入 `pip install -e .\.venv\Lib\site-packages\nonebot_plugin_nerdle` 以安装该插件。

   请确保你的环境中存在 `setuptools` 和 `wheel` 库！
3. 在你的项目的 `pyproject.toml` 中添加如下内容：

```json
dependencies = [
    "nonebot-plugin-nerdle>=0.1.0",
    # 其余部分保持你的内容不变
]
nonebot-plugin-nerdle = ["nonebot_plugin_nerdle"]
```

4. 运行你的项目，检查是否能正常加载该插件。
