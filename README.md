# novelist-agent

自成长的网文写作 agent。研究技法 → 学习素材 → 写作章节 → 自我改进。

## 快速开始

```bash
git clone https://github.com/你的用户名/novelist-agent.git
cd novelist-agent
```

然后在这个目录下启动 Claude Code：

```bash
claude
```

Claude Code 会自动加载 CLAUDE.md，进入 agent 模式。

## 初始化

1. 复制 `config.example.yml` 为 `config.yml`，设置 `data_root` 指向你的数据仓库
2. 复制 `templates/` 下的文件到 `craft/` 和 `projects/<你的项目>/`

```bash
cp config.example.yml config.yml
cp templates/init_strengths.yml craft/strengths.yml
cp templates/init_library_index.yml craft/library_index.yml
mkdir -p projects/my-novel/output
cp templates/init_state.json projects/my-novel/state.json
```

3. 编辑 `projects/my-novel/state.json` 设置初始状态

## 工作流

```
用户给 IDEA → 细化大纲 → 分析缺口 → 定向学习 → 写章节 → 自审 → 循环
```

## 目录

```
novelist-agent/
├── CLAUDE.md              ← agent 协议（Claude Code 自动加载）
├── core/                  ← Python 辅助模块
├── pipelines/             ← Python 管道
├── prompts/               ← System prompts
├── protocols/             ← 大文件处理 + 下载协议
├── profiles/              ← Profile 格式规范 + 模板
├── docs/                  ← 工作流参考
├── templates/             ← 初始化模板
├── craft/                 ← 你的能力状态 (gitignored)
└── projects/              ← 你的写作项目 (gitignored)
```

## 依赖

纯 Python 标准库 + PyYAML + Anthropic SDK（仅 Python 批量模式需要）。

Claude Code 模式下不需要任何依赖。

## License

MIT
