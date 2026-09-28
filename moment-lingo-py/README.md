# 项目依赖导出指南

本项目使用 `uv` 作为包依赖管理工具。如果你需要导出项目的依赖记录（如生成 `requirements.txt`），请参考以下步骤：

## 1. 仅导出“直接依赖”

如果你只想导出项目明确引用的直接依赖（即 `pyproject.toml` 中声明的包，不包含它们的子依赖），请在终端中运行以下命令：

```bash
uv pip compile --no-deps pyproject.toml -o direct_requirements.txt
```

**说明**：
- `--no-deps`: 告诉 uv 忽略包的子依赖，仅编译当前文件指定的包。
- `-o direct_requirements.txt`: 将导出的直接依赖结果保存到 `direct_requirements.txt` 文件中。

## 2. 导出“所有依赖”（包含子依赖/完整环境）

如果你需要导出包含所有子依赖的完整依赖列表（这通常用于在生产环境中精确还原相同的依赖版本），请使用 `uv export` 命令：

```bash
uv export --no-hashes --no-emit-project -o requirements.txt
```

**说明**：
- `--no-hashes`: 在生成的 requirements 文件中省略哈希值，使其更加清爽和兼容。
- `--no-emit-project`: 在导出的依赖列表中不包含当前项目自身的引用。
- `-o requirements.txt`: 将结果输出到 `requirements.txt`。

## 3. 查看依赖树

如果你只是想在终端中查看当前项目的依赖层级结构，可以使用：

```bash
uv tree
```
如果只想查看第一层（即直接依赖），可以指定深度：
```bash
uv tree --depth 1
```

## 4. Docker 挂载开发环境指南

项目中提供了一个专为“挂载运行”设计的 `Dockerfile`，这使得容器仅作为干净的执行环境（只负责提供 Python 环境、uv 并在启动时安装依赖）。所有的代码和依赖文件都在宿主机中通过 Volume 映射。

**构建基础镜像**（包含 Python + uv）：
```bash
docker build -t moment-lingo-py:local .
```

**运行容器并挂载项目代码**（以 PowerShell 为例）：
```powershell
docker run -d `
  --name moment-lingo-app `
  -v "${PWD}:/app" `
  -p 8000:8000 `
  moment-lingo-py:local
```
*(如果是 Linux/macOS 环境下，请将 `${PWD}` 替换为 `$(pwd)`)*

**说明**：
- `-v "${PWD}:/app"`: 将当前宿主机的所有项目文件（包括 `main.py` 和 `direct_requirements.txt`）映射到容器内的 `/app` 目录。
- 每次启动/重启这个容器时，它都会根据挂载的最新 `direct_requirements.txt` 检查并安装更新直接依赖，然后执行代码。你在本地的代码更改会在容器内即时生效。

