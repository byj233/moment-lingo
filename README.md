<div align="center">

<img src="./moment-lingo-vue/public/logo.webp" width="120" alt="moment-lingo logo" />

# moment-lingo

**一个开源的、多端英语学习平台**

Web · H5 · 浏览器插件 · App · 微信小程序

[🌐 在线体验](https://www.momentlingo.cn) · [功能特性](#功能特性) · [快速开始](#快速开始) · [参与贡献](#参与贡献)

<img alt="License" src="https://img.shields.io/badge/License-MIT-blue.svg" />
<img alt="Go" src="https://img.shields.io/badge/Go-1.26-00ADD8?logo=go&logoColor=white" />
<img alt="Python" src="https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white" />
<img alt="Vue" src="https://img.shields.io/badge/Vue-3-4FC08D?logo=vuedotjs&logoColor=white" />
<img alt="PRs Welcome" src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" />

</div>

## 这是什么

moment-lingo 是一个面向英语学习者的多端平台，围绕 **「查词 → 记忆 → 写作 → 口语」** 的学习闭环构建：

在网页上遇到生词可以直接划词翻译，查过的词自动沉淀成自己的单词本；写作文可以交给 AI 逐句批改；想练口语时，可以打开实时语音对话。

项目由四个可独立部署的子项目组成，通过 HTTP 与 WebSocket 协作，代码全部开源，欢迎一起完善。

## 功能特性

**📖 学习端（Web / H5 / App）**

- 词汇详情：音标、释义、例句、词形变化（原形 / 过去式 / 复数 / 比较级等）
- 单词本与单词书，按书归类学习
- 基于 Meilisearch 的全文搜索
- 注册登录，支持邮箱验证码与短信验证码
- AI 写作辅助、AI 作文批改（异步任务 + 逐句修改建议）
- AI 口语对话：WebSocket 实时语音互动

**🔤 浏览器插件**

- 划词翻译与全文翻译，随取随用
- 与站点账号打通，查词同步进单词本

**🤖 AI 与语音能力**

- 多模型接入：火山引擎方舟、阿里云百炼（DashScope）、MiniMax
- 豆包语音合成（TTS）流式播报
- OCR 图片取词
- Mem0 长期记忆

**⚙️ 平台能力**

- 阿里云 OSS 直传（STS 临时凭证 + 分片上传任务）
- Redis 会话与登录令牌
- SSE / WebSocket 流式响应

## 界面预览

<!-- 想放截图的话，把图片放进 docs/screenshots/ 后取消下面注释即可：
<p align="center">
  <img src="./docs/screenshots/home.png" width="720" alt="首页" />
</p>
 -->

目前没有内置截图资源，可以先访问 [www.momentlingo.cn](https://www.momentlingo.cn) 查看实际效果。

## 技术栈

| 层 | 技术 |
| --- | --- |
| 前端 | Vue 3、TypeScript、Vite、Pinia、Vue Router、Tailwind CSS、TDesign Mobile、Arco Design |
| 业务后端 | Go 1.26、Gin、GORM、Viper、go-redis、snowflake |
| AI 服务 | Python 3.13、FastAPI、LangChain、SQLModel、SSE / WebSocket |
| 存储 | MySQL、Redis、Meilisearch、阿里云 OSS |
| 模型与语音 | 火山引擎（方舟 / 豆包 TTS）、阿里云百炼、MiniMax、Mem0 |
| 浏览器插件 | Chrome Manifest V3 |

## 架构

```
 浏览器插件 ─┐                        ┌─→ MySQL
 Web / H5  ─┼─→ 业务 API (Go · :8080)─┼─→ Redis
   App     ─┘        │                └─→ Meilisearch
                     │  /ai /tts /essay /sms
                     ▼
             AI 服务 (Python · :8000) ──→ 大模型 / TTS / OSS
```

- **Go 业务 API** 负责账号、词汇、搜索、作文、单词书、OSS，并统一做鉴权；对外前缀为 `/moment-lingo`。
- **Python AI 服务** 负责需要编排大模型的场景，用 SSE / WebSocket 做流式输出，由 Go 侧转发或前端直连。
- 需要登录的接口通过 `Authorization: Bearer <token>` 校验，令牌由 Redis 维护。

## 快速开始

### 环境要求

| 依赖 | 版本 |
| --- | --- |
| Go | 1.26+ |
| Python | 3.13+（推荐 [uv](https://docs.astral.sh/uv/)） |
| Node.js | 20+ |
| MySQL | 8+ |
| Redis | 6+ |
| Meilisearch | 最新版（搜索功能需要） |

### 1. 准备基础设施

启动 MySQL，并导入建表语句：

```bash
mysql -u root -p < moment-lingo-go/sql.txt
```

再启动 Redis 与 Meilisearch（本地默认端口分别为 `6379`、`7700`）。

### 2. 启动 AI 服务（Python）

```bash
cd moment-lingo-py
cp .env.example .env      # Windows: copy .env.example .env
uv sync
uv run python main.py     # 监听 :8000
```

### 3. 启动业务 API（Go）

```bash
cd moment-lingo-go
# 先编辑 config/application.yml，填入数据库 / Redis / 邮箱 / OSS 等配置
go run .
```

服务监听 `:8080`。Windows 上也可以直接运行 `./build.ps1` 交叉编译 Linux 可执行文件到 `release/`。

### 4. 启动前端（Web / H5）

```bash
cd moment-lingo-vue
npm install
npm run dev               # http://localhost:5173
```

本地联调时，请把 `src/config/index.ts` 中的 `isDev` 改成 `true`，此时前端会指向
`http://localhost:8080/moment-lingo` 与 `ws://localhost:8000`。

### 5. 加载浏览器插件

1. 打开 `chrome://extensions/`
2. 打开右上角「开发者模式」
3. 点击「加载已解压的扩展程序」，选择 `momentlingo-extension` 目录

插件默认连接 `https://www.momentlingo.cn`，本地调试请同步修改 `manifest.json` 与 `src/content/content.js` 中的域名。

<details>
<summary><b>项目结构</b>（点击展开）</summary>

```
moment-lingo/
├── moment-lingo-go/          # Go 业务 API
│   ├── config/               # 配置（application.yml）
│   ├── controller/ service/ repo/   # 接口 / 业务 / 数据访问
│   ├── model/ dto/           # 模型与传输对象
│   ├── router/               # 路由与鉴权中间件
│   ├── utils/ common/        # 工具与中间件客户端初始化
│   ├── sql.txt               # 建表语句
│   └── build.ps1             # 构建脚本
├── moment-lingo-py/          # Python AI 服务
│   ├── src/app.py            # FastAPI 入口与路由
│   ├── src/config.py         # 环境变量配置
│   ├── src/service/ utils/   # AI / 作文 / TTS / 短信及其封装
│   ├── src/sdk/              # 豆包 TTS WebSocket 协议实现
│   ├── .env.example          # 环境变量模板
│   └── main.py               # 本地启动入口
├── moment-lingo-vue/         # Web / H5 / App 前端
│   └── src/{views,api,store,components,config}/
└── momentlingo-extension/    # 浏览器插件
    └── src/{background,content,popup}/
```

</details>

<details>
<summary><b>配置说明</b>（点击展开）</summary>

**Python：`moment-lingo-py/.env`**（参考 `.env.example`）

| 变量 | 说明 |
| --- | --- |
| `ALIYUN_ACCESS_KEY_ID` / `ALIYUN_ACCESS_KEY_SECRET` | 阿里云 AccessKey，用于短信验证码（Dypnsapi） |
| `VOLCENGINE_BASE_URL` / `VOLCENGINE_API_KEY` | 火山引擎方舟大模型 |
| `VOLCENGINE_TTS_APP_ID` / `VOLCENGINE_TTS_ACCESS_KEY` | 豆包语音合成（TTS）鉴权 |
| `MINIMAX_API_KEY` | MiniMax 接口密钥 |
| `BAILIAN_BASE_URL` / `BAILIAN_API_KEY` | 阿里云百炼（DashScope） |
| `REDIS_HOST` / `REDIS_PORT` / `REDIS_USERNAME` / `REDIS_PASSWORD` / `REDIS_DB` | Redis 连接 |
| `DB_NAME` / `DB_HOST` / `DB_PORT` / `DB_USERNAME` / `DB_PASSWORD` | MySQL 连接 |
| `MEM0_API_KEY` / `MEM0_HOST` | Mem0 记忆服务 |
| `MEILI_HOST` / `MEILI_API_KEY` | Meilisearch 连接 |

**Go：`moment-lingo-go/config/application.yml`**

| 配置项 | 说明 |
| --- | --- |
| `server.port` | 预留字段，当前路由固定监听 `8080` |
| `database.*` / `redis.*` | MySQL / Redis 连接 |
| `email.*` | SMTP 发信，用于注册验证码邮件（QQ 邮箱为 `smtp.qq.com:587`，密码填授权码） |
| `meilisearch.url` / `meilisearch.api-key` | Meilisearch 连接 |
| `python.url` | Python AI 服务地址 |
| `aliyun.access-key-id` / `aliyun.access-key-secret` | 阿里云 AccessKey，用于申请 OSS STS 临时凭证 |

</details>

<details>
<summary><b>接口一览</b>（点击展开）</summary>

**业务 API（`:8080`，前缀 `/moment-lingo`）**

| 分组 | 方法与路径 |
| --- | --- |
| 认证 | `POST /auth/captcha/send`、`POST /auth/register`、`POST /auth/login`、`ANY /auth/options` |
| 词汇 | `GET /vocabulary/:vocabulary`、`GET /vocabulary/detail/:vocabularyId`、`GET /vocabulary/brief/:vocabularyId` |
| 搜索 | `POST /search/vocabulary` |
| 语音 | `POST /tts/stream`、`GET /tts/voices/list` |
| 对象存储 | `GET /oss/sts-token`、`GET /oss/presign`、`POST /oss/upload/task`、`GET /oss/upload/task/:taskId` |
| AI | `POST /ai/ocr`、`POST /ai/extension/translate`、`POST /ai/write` |
| 作文 | `POST /essay/correct/task`、`GET /essay/correct/task/list`、`GET /essay/correct/list`、`GET /essay/correct/:essayId`、`GET /essay/correct/task/:taskId` |
| 单词书 | `GET /book/list`、`GET /book/:bookId`、`GET /book/detail/:bookId` |
| 用户 | `GET /user/me`、`PATCH /user/me` |

**AI 服务（`:8000`）**

| 方法与路径 | 说明 |
| --- | --- |
| `POST /tts` | 语音合成（SSE 流式返回） |
| `POST /sms` | 发送短信验证码 |
| `POST /ai/extension/translate` | 插件划词 / 全文翻译（SSE） |
| `POST /ai/ocr` | 图片文字识别（SSE） |
| `POST /ai/write` | AI 写作 |
| `POST /essay/correct/task` | 创建作文批改任务 |
| `WS /ai/call` | AI 口语实时对话 |

</details>

## 数据库

建表语句见 [`moment-lingo-go/sql.txt`](./moment-lingo-go/sql.txt)，共 8 张表：
`user`、`vocabulary`、`word`、`phrase`、`voice`、`essay`、`book`、`book_vocabulary`。

## 常见问题

**为什么有两个后端？**
Go 负责常规业务接口与鉴权，性能好、部署简单；Python 生态在 LLM 编排、语音处理上更顺手，所以把 AI 相关能力单独拆成服务。

**必须准备云服务账号才能跑起来吗？**
基础功能（词汇、搜索、登录）需要 MySQL、Redis、Meilisearch；短信、TTS、AI 写作 / 批改 / 口语、OSS 上传还需要额外的云服务账号，未配置时对应接口不可用，但不影响其余功能。

**前端跑起来但请求失败？**
多半是 `src/config/index.ts` 里的 `isDev` 还是 `false`（指向线上地址）。本地开发改成 `true`。

**配置文件是空的？**
出于安全考虑，仓库里的密钥字段已全部清空，需要你自己填写，详见上面的「配置说明」。

**能直接用 Docker 部署吗？**
目前仓库还没有提供 Dockerfile / compose 编排，属于待补充项，见「路线图」。

## 路线图

- [ ] 提供 Dockerfile 与 docker-compose，降低本地启动成本
- [ ] 补充单元测试与 CI
- [ ] 拆出更清晰的 API 文档（OpenAPI）
- [ ] 微信小程序端
- [ ] 完善 README 截图与演示视频

> 欢迎在 Issue 里补充你希望看到的方向。

## 参与贡献

欢迎任何形式的贡献：提交 Issue、修正文档、补充测试、提交 PR。

1. Fork 本仓库，从 `master` 新建分支（建议 `feature/xxx` 或 `fix/xxx`）
2. 本地跑通后再提交，尽量保持一次 PR 只做一件事
3. **提交前务必确认没有把密钥、令牌、账号或个人信息带进代码**（`.env` 已被忽略，配置文件请只填占位符）
4. 发起 Pull Request，说明改动动机与验证方式

## 开源协议

本项目基于 [MIT License](./LICENSE) 开源，可自由使用、修改与分发。

## 免责声明

项目会调用火山引擎、阿里云、MiniMax 等第三方服务，相关调用可能产生费用，请自行评估并遵守各平台的使用条款。
