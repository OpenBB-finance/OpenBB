# OpenBB Platform (平台)

[![下载量](https://static.pepy.tech/badge/openbb)](https://pepy.tech/project/openbb)
[![最新版本](https://badge.fury.io/py/openbb.svg)](https://github.com/OpenBB-finance/OpenBB)

| OpenBB 致力于通过构建面向所有人、随处可用的开源基础设施来打造投资研究的未来。 |
| :---------------------------------------------------------------------------------------------------------------------------------------------: |
|              ![OpenBB Logo](https://user-images.githubusercontent.com/25267873/218899768-1f0964b8-326c-4f35-af6f-ea0946ac970b.png)               |
|                                                 访问我们的网站：[openbb.co](https://www.openbb.co)                                         |

## 概览 (Overview)

OpenBB Platform 提供了一种从多个数据提供商获取金融原始数据的便捷方式。该软件包自带开箱即用的 REST API，允许任何编程语言的开发者在 OpenBB Platform 之上轻松构建应用程序。

请在 [docs.openbb.co](https://docs.openbb.co/platform) 查看完整文档。

## 安装 (Installation)

### PyPI

以下命令可安装 OpenBB Platform 的核心功能及部分选定的数据源。

```bash
pip install openbb
```

这将安装核心模块、路由模块以及以下数据提供商的连接器：

| 扩展名称 | 描述 | 安装命令 | 所需最低订阅类型 |
|----------------|-------------|----------------------|------------------------------------|
| openbb-benzinga | [Benzinga](https://www.benzinga.com/apis/en-ca/) 数据连接器 | pip install openbb-benzinga | 付费 |
| openbb-bls | [美国劳工统计局 (BLS)](https://www.bls.gov/developers/home.htm) 数据连接器 | pip install openbb-bls | 免费 |
| openbb-congress-gov | [美国国会 API](https://api.congress.gov/sign-up/) 数据连接器 | pip install openbb-congress-gov | 免费 |
| openbb-cftc | [商品期货交易委员会 (CFTC)](https://publicreporting.cftc.gov/stories/s/r4w3-av2u) 数据连接器 | pip install openbb-cftc | 免费 |
| openbb-econdb | [EconDB](https://econdb.com) 数据连接器 | pip install openbb-econdb | 无 |
| openbb-imf | [国际货币基金组织 (IMF)](https://data.imf.org) 数据连接器 | pip install openbb-imf | 无 |
| openbb-fmp | [FMP](https://site.financialmodelingprep.com/developer/) 数据连接器 | pip install openbb-fmp | 免费 |
| openbb-fred | [圣路易斯联储 (FRED)](https://fred.stlouisfed.org/) 数据连接器 | pip install openbb-fred | 免费 |
| openbb-intrinio | [Intrinio](https://intrinio.com/pricing) 数据连接器 | pip install openbb-intrinio | 付费 |
| openbb-oecd | [经合组织 (OECD)](https://data.oecd.org/) 数据连接器 | pip install openbb-oecd | 免费 |
| openbb-polygon | [Polygon](https://polygon.io/) 数据连接器 | pip install openbb-polygon | 免费 |
| openbb-sec | [美国证券交易委员会 (SEC)](https://www.sec.gov/edgar/sec-api-documentation) 数据连接器 | pip install openbb-sec | 无 |
| openbb-tiingo | [Tiingo](https://www.tiingo.com/about/pricing) 数据连接器 | pip install openbb-tiingo | 免费 |
| openbb-tradingeconomics | [TradingEconomics](https://tradingeconomics.com/api) 数据连接器 | pip install openbb-tradingeconomics | 付费 |
| openbb-yfinance | [雅虎财经 (Yahoo Finance)](https://finance.yahoo.com/) 数据连接器 | pip install openbb-yfinance | 无 |

### 额外扩展 (Extras)

运行 `pip install openbb` 时不会安装这些包。它们可以单独安装，或通过运行 `pip install openbb[all]` 统一安装。

| 扩展名称 | 描述 | 安装命令 | 所需最低订阅类型 |
|----------------|-------------|----------------------|------------------------------------|
| openbb-mcp-server | 将 OpenBB Platform 作为 [MCP 服务器](https://pypi.org/project/openbb-mcp-server/) 运行 | pip install openbb-mcp-server | 无 |
| openbb-charting | 集成 [Plotly 图表库](https://pypi.org/project/openbb-charting/) 和专用窗口渲染。 | pip install openbb-charting | 无 |
| openbb-alpha-vantage | [Alpha Vantage](https://www.alphavantage.co/) 数据连接器 | pip install openbb-alpha-vantage | 免费 |
| openbb-biztoc | [Biztoc](https://api.biztoc.com/#biztoc-default) 新闻数据连接器 | pip install openbb-biztoc | 免费 |
| openbb-cboe | [Cboe](https://www.cboe.com/delayed_quotes/) 数据连接器 | pip install openbb-cboe | 无 |
| openbb-deribit | [Deribit](https://docs.deribit.com/) 数据连接器 | pip install openbb-deribit | 无 |
| openbb-ecb | [欧洲央行 (ECB)](https://data.ecb.europa.eu/) 数据连接器 | pip install openbb-ecb | 无 |
| openbb-famafrench | [Ken French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) 连接器 | pip install openbb-famafrench | 无 |
| openbb-federal-reserve | [美联储 (Federal Reserve)](https://www.federalreserve.gov/) 数据连接器 | pip install openbb-federal-reserve | 无 |
| openbb-finra | [美国金融业监管局 (FINRA)](https://www.finra.org/finra-data) 数据连接器 | pip install openbb-finra | 无/免费 |
| openbb-finviz | [Finviz](https://finviz.com) 数据连接器 | pip install openbb-finviz | 无 |
| openbb-government-us | [美国政府](https://data.gov) 数据连接器 | pip install openbb-us-government | 无 |
| openbb-nasdaq | [纳斯达克数据链接 (Nasdaq Data Link)](https://data.nasdaq.com/) 连接器 | pip install openbb-nasdaq | 无/免费 |
| openbb-seeking-alpha | [Seeking Alpha](https://seekingalpha.com/) 数据连接器 | pip install openbb-seeking-alpha | 无 |
| openbb-stockgrid | [Stockgrid](https://stockgrid.io) 数据连接器 | pip install openbb-stockgrid | 无 |
| openbb-tmx | [TMX](https://money.tmx.com) 数据连接器 | pip install openbb-tmx | 无 |
| openbb-tradier | [Tradier](https://tradier.com) 数据连接器 | pip install openbb-tradier | 无 |
| openbb-wsj | [华尔街日报 (Wall Street Journal)](https://www.wsj.com/) 数据连接器 | pip install openbb-wsj | 无 |


```bash
pip install openbb-equity openbb-yfinance
```

## Python 使用

```python
>>> from openbb import obb
>>> output = obb.equity.price.historical("AAPL")
>>> df = output.to_dataframe()
>>> df.tail()
```

| date       |    open |   high |    low |   close |
|:-----------|--------:|-------:|-------:|--------:|
| 2025-09-30 | 254.86  | 255.92 | 253.11 |  254.63 |
| 2025-10-01 | 255.04  | 258.79 | 254.93 |  255.45 |
| 2025-10-02 | 256.58  | 258.18 | 254.15 |  257.13 |
| 2025-10-03 | 254.67  | 259.24 | 253.95 |  258.02 |
| 2025-10-06 | 257.945 | 259.07 | 255.05 |  256.69 |


## API 密钥 (API Keys)

为了充分利用 OpenBB Platform，您需要获取一些 API 密钥来连接数据提供商（见上表）。

以下是设置方法：

### 本地文件

直接在 `~/.openbb_platform/user_settings.json` 文件中指定密钥。

根据以下模板填写该文件，并将相关值替换为您的密钥：

```json
{
  "credentials": {
    "fmp_api_key": "在此替换",
    "polygon_api_key": "在此替换",
    "benzinga_api_key": "在此替换",
    "fred_api_key": "在此替换"
  }
}
```

### 运行时 (Runtime)

也可以使用 Python 接口仅为当前会话设置凭据。

```python
>>> from openbb import obb
>>> obb.user.credentials.fred_api_key = "在此替换"
>>> obb.user.credentials.polygon_api_key = "在此替换"
```

详情请参阅 [文档](https://docs.openbb.co/platform/settings/user_settings/api_keys)。

## REST API

OpenBB Platform 自带一个使用 FastAPI 构建的开箱即用的 REST API。使用以下命令启动应用程序：

```bash
uvicorn openbb_core.api.rest_api:app --host 0.0.0.0 --port 8000 --reload
```

API 文档位于服务器根地址下的 "/docs" 路径，可以在任何支持访问本地主机的浏览器（如 Chrome）中查看。

有关运行时设置和配置，请参阅 [文档](https://docs.openbb.co/platform/settings/system_settings#api-settings)。

## 本地开发 (Local Development)

若要基于源代码进行开发，您需要具备以下条件：

- Git
- Python 3.10 - 3.13.
- 安装了 `poetry` 的虚拟环境。
  - 激活虚拟环境并运行 `pip install poetry`。
- [GitHub 仓库](https://github.com/OpenBB-finance/OpenBB.git) 的本地副本。

使用安装脚本安装仓库以进行本地开发：

  1. 激活您的虚拟环境。
  2. 进入 `openbb_platform` 目录。
  3. 运行 `python dev_install.py -e` 以“可编辑模式”安装所有包。

请参阅 [文档](https://docs.openbb.co/platform/developer_guide/architecture_overview) 以了解架构概览以及如何开始构建您自己的扩展。
