# Open Data Platform (ODP) - OpenBB 桌面应用程序

ODP 桌面应用程序通过降低在多个界面上构建、呈现和共享数据流水线、见解或仪表板的技术门槛，增强了开发者的体验。

此代码库包含了 OpenBB 发布的核心 Open Data Platform (ODP) 桌面端应用程序及系统托盘图标的完整源代码。

分发的二进制文件（目前支持 macOS 和 Windows）是此仓库中构建操作的直接产物，负责生成发行版工件。

请注意，虽然目前没有针对 Linux 发行版的构建流水线，但可以在本地执行构建和安装。

## 用户文档与安装

官方用户文档请参考：[此处](https://docs.openbb.co/desktop)。

下载最新版本：[请点击此处](https://github.com/OpenBB-finance/OpenBB/releases/tag/odp)

本节余下部分旨在帮助您熟悉和上手此代码库。

## 技术栈概览

ODP Desktop 基于 Tauri 和 React 框架构建，其中 Rust 和 TypeScript 的代码占比约为 50/50。

该技术栈利用操作系统原生的窗口创建能力，极大地减小了分发包的体积。安装后大小约为 35 MB，压缩后仅为 12 MB。

该应用程序以“托盘图标 - 后台服务”的形式运行，其功能依赖于通过 ODP 单独安装的开发工具。换句话说，应用程序本身是一个图形界面 (GUI) 和一个与操作系统及命令行交互的包装器。

我们假设操作系统中未安装任何开发工具，且用户不具备该机器的管理员/root 权限。多用户机器必须针对每个用户单独配置。

为了便于环境管理和解决依赖项，当第一次运行 ODP Desktop 时，系统会自动安装 Miniforge。选择 Conda 是由于其高效的隔离模式以及与平台、编程语言无关的特性。

初始安装环境提供了一个生产就绪的 REST API、MCP 服务器、NodeJS 以及 Jupyter Lab IDE。

## 运行代码

按照以下步骤从开发服务器在本地运行代码。

### Rust

您必须安装或更新 Rust 至 1.90.0 版本。

```sh
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

如果您之前已安装 Rust，请更新到最新版本（目前为 rustc 1.90.0）：

```sh
rustup update
```

### NodeJS

$PATH 环境变量中必须包含 NodeJS 和 NPM。

如果尚未安装，请参考 [官方说明](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)。

如果您已经安装了 `npm`，请在安装本项目之前对其进行更新。

### OpenSSL

系统中必须安装 OpenSSL，并配置以下环境变量：

```env
OPENSSL_DIR
OPENSSL_INCLUDE_DIR
OPENSSL_LIB_DIR
```

### 安装项目

完成上述三项安装或更新后，在 `/desktop` 根目录下运行命令安装项目：

```sh
npm install
```

### 开发

构建并启动开发服务器：

```sh
npm run tauri dev
```

这将启动开发服务器并监听代码库的更改。大多数更改会被自动识别，但某些操作可能需要完整重启服务。

如果您使用浏览器而非独立窗口查看开发服务器，某些功能可能无法正常运行，这是预期行为。

目前请忽略所有警告信息，我们稍后会进行统一清理。

### 推荐的 VS Code 扩展

- rust-analyzer
- Tauri
- Tailwind CSS IntelliSense

## 构建 (Building)

生产环境的构建和签名旨在通过 GitHub Actions 完成。如果您是在官方发布结构之外进行构建，可能需要调整 `beforeBundleCommand` 配置。
