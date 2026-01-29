<br />
<img src="https://github.com/OpenBB-finance/OpenBB/blob/develop/images/odp-light.svg?raw=true#gh-light-mode-only" alt="OpenBB 开放数据平台图标" width="600">
<img src="https://github.com/OpenBB-finance/OpenBB/blob/develop/images/odp-dark.svg?raw=true#gh-dark-mode-only" alt="OpenBB 开放数据平台图标" width="600">
<br />
<br />

[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/openbb_finance.svg?style=social&label=关注%20%40openbb_finance)](https://x.com/openbb_finance)
[![Discord Shield](https://img.shields.io/discord/831165782750789672)](https://discord.com/invite/xPHTuHCmuV)
[![在 Dev Containers 中打开](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/OpenBB-finance/OpenBB)
<a href="https://codespaces.new/OpenBB-finance/OpenBB">
  <img src="https://github.com/codespaces/badge.svg" height="20" />
</a>
<a target="_blank" href="https://colab.research.google.com/github/OpenBB-finance/OpenBB/blob/develop/examples/googleColab.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="在 Colab 中打开"/>
</a>
[![PyPI](https://img.shields.io/pypi/v/openbb?color=blue&label=PyPI%20软件包)](https://pypi.org/project/openbb/)

OpenBB 开放数据平台 (ODP) 是一个开源工具集，旨在帮助数据工程师将专有数据、授权数据和公共数据源整合到下游应用中，如 AI 助手、金融研究控制面板等。

ODP 作为“一次连接，随处使用”的基础设施层，将数据整合并同时暴露给多个平台：面向量化人员的 Python 环境、面向量析师的 OpenBB Workspace 和 Excel、面向 AI 代理的 MCP 服务器，以及面向其他应用程序的 REST API。

<a href="https://pro.openbb.co">
  <div align="center">
  <img src="https://openbb-cms.directus.app/assets/70b971ef-7a7e-486e-b5ae-1cc602f2162c.png" alt="Logo" width="1000">
  </div>
</a>

快速开始：`pip install openbb`

```python
from openbb import obb
output = obb.equity.price.historical("AAPL")
df = output.to_dataframe()
```

可用的数据集成可以在此处找到：<https://docs.openbb.co/python/reference>

---

## OpenBB Workspace

虽然开放数据平台提供了开源数据集成的基础，但 **OpenBB Workspace** 为分析师提供了可视化的企业级 UI，并可利用 AI 代理。平台的“一次连接，随处使用”架构实现了两者之间的无缝集成。

您可以访问 <https://pro.openbb.co> 体验 OpenBB Workspace。
<a href="https://pro.openbb.co">
  <div align="center">
  <img src="https://openbb-cms.directus.app/assets/f69b6aaf-0821-4bc8-a43c-715e03a924ef.png" alt="Logo" width="1000">
  </div>
</a>

数据集成：

- 您可以从 [文档](https://docs.openbb.co/workspace) 或 [此开源仓库](https://github.com/OpenBB-finance/backends-for-openbb) 了解更多关于向 OpenBB Workspace 添加数据的信息。

AI 代理集成：

- 您可以从 [此开源仓库](https://github.com/OpenBB-finance/agents-for-openbb) 了解更多关于向 OpenBB Workspace 添加 AI 代理的信息。

### 将开放数据平台集成到 OpenBB Workspace

在 Python (3.9.21 - 3.12) 环境中通过几个简单的步骤将此库连接到 OpenBB Workspace。

#### 运行 ODP 后端

- 安装软件包。

```sh
pip install "openbb[all]"
```

- 在本地启动 API 服务。

```sh
openbb-api
```

这将通过 Uvicorn 在 `127.0.0.1:6900` 启动一个 FastAPI 服务器。

您可以通过访问 <http://127.0.0.1:6900> 检查其是否运行正常。

#### 将 ODP 后端集成到 OpenBB Workspace

登录 [OpenBB Workspace](https://pro.openbb.co/)，并按照以下步骤操作：

![操作指南图示](https://github.com/user-attachments/assets/75cffb4a-5e95-470a-b9d0-6ffd4067e069)

1. 前往 "Apps" 选项卡
2. 点击 "Connect backend" (连接后端)
3. 填写表单：
   名称：Open Data Platform
   URL：<http://127.0.0.1:6900>
4. 点击 "Test" (测试)。您应该会看到 "Test successful" (测试成功) 并显示找到的应用数量。
5. 点击 "Add" (添加)。

完成。

---

<!-- 目录 -->
<details closed="closed">
  <summary><h2 style="display: inline-block">目录</h2></summary>
  <ol>
    <li><a href="#1-安装">安装</a></li>
    <li><a href="#2-贡献">贡献</a></li>
    <li><a href="#3-许可">许可</a></li>
    <li><a href="#4-免责声明">免责声明</a></li>
    <li><a href="#5-联系方式">联系方式</a></li>
    <li><a href="#6-关注度历史">Star History</a></li>
    <li><a href="#7-贡献者">贡献者</a></li>
  </ol>
</details>

## 1. 安装

ODP Python 软件包可以通过 [PyPI](https://pypi.org/project/openbb/) 安装，运行命令：`pip install openbb`

或者直接通过克隆仓库安装：`git clone https://github.com/OpenBB-finance/OpenBB.git`。

有关安装过程的更多详细信息，请参阅 [OpenBB 文档](https://docs.openbb.co/python/installation)。

### ODP CLI 安装

ODP CLI 是一个命令行界面，允许您直接从终端访问 ODP。

可以通过运行 `pip install openbb-cli` 安装，

或者直接通过克隆仓库安装：`git clone https://github.com/OpenBB-finance/OpenBB.git`。

有关安装过程的更多详细信息，请参阅 [OpenBB 文档](https://docs.openbb.co/cli/installation)。

## 2. 贡献

参与此项目主要有三种方式（希望你已经给项目点过星了 ⭐️）：

### 成为贡献者

- 更多信息请访问我们的 [开发者文档](https://docs.openbb.co/python/developer)。

### 创建 GitHub 工单 (Ticket)

在创建工单之前，请确保 [现有的 issue](https://github.com/OpenBB-finance/OpenBB/issues) 中尚不存在相同的问题。

- [报告 Bug](https://github.com/OpenBB-finance/OpenBB/issues/new?assignees=&labels=bug&template=bug_report.md&title=%5BBug%5D)
- [建议改进](https://github.com/OpenBB-finance/OpenBB/issues/new?assignees=&labels=enhancement&template=enhancement.md&title=%5BIMPROVE%5D)
- [功能请求](https://github.com/OpenBB-finance/OpenBB/issues/new?assignees=&labels=new+feature&template=feature_request.md&title=%5BFR%5D)

### 提供反馈

我们在 [Discord](https://openbb.co/discord) 上最为活跃，但也可以随时通过我们的任何 [社交媒体](https://openbb.co/links) 联系我们并提供反馈。

## 3. 许可

基于 AGPLv3 许可证分发。更多信息请参阅 [LICENSE](https://github.com/OpenBB-finance/OpenBB/blob/main/LICENSE)。

## 4. 免责声明

金融工具交易涉及高风险，包括损失部分或全部投资金额的风险，可能并不适合所有投资者。

在决定交易金融工具之前，您应该充分了解与金融市场交易相关的风险和成本，仔细考虑您的投资目标、经验水平和风险偏好，并在需要时寻求专业建议。

开放数据平台中的数据不一定准确。

OpenBB 以及本网站所含数据的任何提供商对于因您的交易或您对所显示信息的依赖而导致的任何损失或损害概不负责。

我们网站、产品或文档中可能引用的所有第三方名称、徽标和品牌均为其各自所有者的商标。除非另有说明，OpenBB 及其产品和服务不受这些第三方的支持、赞助或关联。

我们使用这些名称、徽标和品牌仅用于识别目的，并不暗示任何此类背书、赞助或关联。

## 5. 联系方式

如果您对平台或 OpenBB 有任何疑问，请随时发送电子邮件至 `support@openbb.co`

如果您想打个招呼或有兴趣与我们合作，请随时通过 `hello@openbb.co` 与我们联系。

我们的社交媒体平台：[openbb.co/links](https://openbb.co/links)

## 6. Star History

这是我们成长的一个缩影，我们才刚刚开始。

更多对我们重要的指标请访问 [openbb.co/open](https://openbb.co/open)。

[![Star History Chart](https://api.star-history.com/svg?repos=openbb-finance/OpenBB&type=Date&theme=dark)](https://api.star-history.com/svg?repos=openbb-finance/OpenBB&type=Date&theme=dark)

## 7. 贡献者

如果没有你们，OpenBB 就不可能存在。如果我们要颠覆金融行业，每一次贡献都至关重要。感谢您成为这段旅程的一部分。

<a href="https://github.com/OpenBB-finance/OpenBB/graphs/contributors">
   <img src="https://contributors-img.web.app/image?repo=OpenBB-finance/OpenBB" width="800"/>
</a>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/OpenBB-finance/OpenBB.svg?style=for-the-badge
[contributors-url]: https://github.com/OpenBB-finance/OpenBB/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/OpenBB-finance/OpenBB.svg?style=for-the-badge
[forks-url]: https://github.com/OpenBB-finance/OpenBB/network/members
[stars-shield]: https://img.shields.io/github/stars/OpenBB-finance/OpenBB.svg?style=for-the-badge
[stars-url]: https://github.com/OpenBB-finance/OpenBB/stargazers
[issues-shield]: https://img.shields.io/github/issues/OpenBB-finance/OpenBB.svg?style=for-the-badge&color=blue
[issues-url]: https://github.com/OpenBB-finance/OpenBB/issues
[bugs-open-shield]: https://img.shields.io/github/issues/OpenBB-finance/OpenBB/bug.svg?style=for-the-badge&color=yellow
[bugs-open-url]: https://github.com/OpenBB-finance/OpenBB/issues?q=is%3Aissue+label%3Abug+is%3Aopen
[bugs-closed-shield]: https://img.shields.io/github/issues-closed/OpenBB-finance/OpenBB/bug.svg?style=for-the-badge&color=success
[bugs-closed-url]: https://github.com/OpenBB-finance/OpenBB/issues?q=is%3Aissue+label%3Abug+is%3Aclosed
[license-shield]: https://img.shields.io/github/license/OpenBB-finance/OpenBB.svg?style=for-the-badge
[license-url]: https://github.com/OpenBB-finance/OpenBB/blob/main/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/DidierRLopes
