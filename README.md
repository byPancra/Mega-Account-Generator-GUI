<div align="center">

[English](https://github.com/byPancra/MEGA-Account-Generator-GUI) | [Português (Brasil)](https://github.com/byPancra/MEGA-Account-Generator-GUI/tree/lang-pt-BR) | [Español](https://github.com/byPancra/MEGA-Account-Generator-GUI/tree/lang-es) | [日本語](https://github.com/byPancra/MEGA-Account-Generator-GUI/tree/lang-ja) | [繁體中文](https://github.com/byPancra/MEGA-Account-Generator-GUI/tree/lang-zh-TW) | **简体中文**

</div>
<br>

<div align="center">

</div>

<div align="center">

  ![Mega Account Generator GUI](./img/readme-icon.png)

  <h1 align="center">Mega Account Generator GUI</h1>
  
  **自动化 MEGA.nz 账户创建与管理的终极工具。**
  
  *使用专业级界面生成、管理、标记和导出您的账户。*

  [![Python Version](https://img.shields.io/badge/python-3.8%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
  [![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](./LICENSE)
  [![Status](https://img.shields.io/badge/status-active-success?style=for-the-badge)]()
  [![Releases](https://img.shields.io/github/downloads/byPancra/Mega-Account-Generator-GUI/total?style=for-the-badge&color=orange)](https://github.com/byPancra/Mega-Account-Generator-GUI/releases)

  [功能](#-功能) • [安装](#-安装) • [使用方法](#-使用方法) • [高级管理](#-高级管理) • [常见问题](#-常见问题)

</div>

---

## 📋 概览

**Mega Account Generator GUI** 是一款强大的桌面级应用程序，专为需要批量生成和管理 [MEGA.nz](https://mega.nz) 账户的高级用户而设计。与简单的脚本不同，此工具提供了一个完整的账户生命周期管理生态系统，包括标记、过滤、状态跟踪和数据导出。

使用 **Modern Python** (CustomTkinter) 和 **线程安全架构** 构建，即使处理数百个账户也能确保可靠性。

![Demo](./img/intro2.gif)

---

## :zap: 功能

### 🚀 核心生成
*   **高速多线程**：同时生成多达 8 个账户。
*   **智能速率限制**：智能延迟和重试逻辑（最多 12 次尝试）以绕过 Mail.tm 限制。
*   **内置依赖**：可执行文件版本预先封装了 `megatools`，无需额外设置。

### 🛠️ 高级管理
*   **标记系统**：使用自定义标签（例如 `个人`、`备份`、`客户-A`）组织账户，以便于检索。
*   **搜索与过滤**：按电子邮件、状态（`有效`、`停用`、`失败`）或标签即时查找账户。
*   **批量操作**：
    *   **保持活跃**：自动登录以防止账户因不活动而被删除。
    *   **存储检查**：自动更新所有账户的已用/可用存储配额。
    *   **账户控制**：停用特定账户以将其排除在批量操作（例如保持活跃检查）之外，而在不删除它们的情况下。

### 💾 数据自由
*   **专业导出**：将您的数据库导出为 **Excel (.xlsx)** 以获得格式化样式，或导出为 **JSON** 以供编程使用。
*   **无缝导入**：通过 JSON/Excel 导入从其他工具或备份转移数据。
*   **剪贴板集成**：一键复制电子邮件和密码。

### 🔒 安全与可靠性
*   **线程安全 CSV**：防止同时写入期间的数据损坏。
*   **崩溃恢复**：“停止”按钮可优雅地停止操作，保留数据完整性。

---

## :rocket: 安装

### 选项 A：独立可执行文件（推荐）
下载最新版本。无需 Python 或外部工具。
1.  从 [Releases](https://github.com/byPancra/Mega-Account-Generator-GUI/releases) 下载 `MegaGenerator.exe`。
2.  运行该可执行文件。

### 选项 B：从源代码运行

**先决条件：**
*   Python 3.8+
*   [Megatools](https://megatools.megous.com/) (已添加到 PATH)

**步骤：**
1.  **克隆仓库：**
    ```bash
    git clone https://github.com/byPancra/Mega-Account-Generator-GUI.git
    cd Mega-Account-Generator-GUI
    ```

2.  **安装依赖：**
    ```bash
    pip install -r requirements.txt
    ```

3.  **运行应用程序：**
    ```bash
    python gui.py
    ```

---

## :computer: 使用方法

### 生成账户
1.  导航至 **Generator**（生成器）选项卡。
2.  设置 **Threads**（线程）和 **Accounts**（账户）的数量以进行生成。
3.  点击 **"Generate Accounts"**（生成账户）。
4.  凭据将保存在 `accounts.csv` 中，并显示在 **Stored Accounts**（已存储账户）选项卡中。

### 管理账户
导航至 **Stored Accounts**（已存储账户）选项卡：
*   **搜索**：输入电子邮件以即时过滤。
*   **过滤**：使用下拉菜单仅查看 `Active`（有效）、`Disabled`（停用）或 `Failed`（失败）的账户。
*   **编辑**：点击 "Edit"（编辑）按钮以更改已保存的密码或管理标签。
*   **复制**：快速按钮将凭据复制到剪贴板。

### 💻 CLI 使用方法（命令行）
适合偏好终端或希望将其集成到脚本中的高级用户。

```bash
# 基本使用（生成 3 个账户）
python generate_accounts.py

# 使用 5 个线程生成 50 个账户
python generate_accounts.py -n 50 -t 5

# 为所有账户设置特定密码
python generate_accounts.py -n 10 -p "MySecretPass123!"
```

**参数：**
*   `-n`, `--number`：要创建的账户数量（默认：3）
*   `-t`, `--threads`：并发线程数量 (1-8)
*   `-p`, `--password`：所有账户的通用密码（可选）

#### 保持活跃检查（登录与存储）
验证 `accounts.csv` 中的所有账户，检查其存储配额，并保持其活跃：

```bash
python signin_accounts.py
```

*   **无需参数。**
*   迭代 `accounts.csv` 中的所有账户。
*   **跳过标记为 "Disabled"（停用）的账户。**
*   更新状态为 `Active`（有效）或 `Login Failed`（登录失败）。
*   更新已用/可用存储值。


---

## :briefcase: 高级管理

### 导出数据
您可以导出整个账户数据库以进行备份或外部使用。
1.  点击右上角的 **Export**（导出）。
2.  选择 **Excel** 以获得格式化电子表格，或 **JSON** 以获得原始数据。
3.  选择存储位置。

*Excel 导出包含颜色编码的状态列和格式化标题，便于阅读。*

### 导入数据
从以前的版本或其他工具转移。
1.  点击 **Import**（导入）。
2.  选择有效的 `.json` 或 `.xlsx` 文件。
3.  工具将数据合并到您的 `accounts.csv` 中。

---

## :grey_question: 常见问题

<details>
<summary><strong>为什么我被限制为 8 个线程？</strong></summary>
临时电子邮件提供商 (Mail.tm) 有严格的速率限制。超过 8 个并发线程会显著增加 IP 被封锁或生成失败的机会。
</details>

<details>
<summary><strong>"Sign In"（登录）按钮有什么作用？</strong></summary>
它执行“保持活跃”检查。它尝试使用 `megatools` 登录您的账户。这会更新存储配额信息并向 MEGA 发出信号表示账户处于活跃状态，防止被删除。
</details>

<details>
<summary><strong>我的账户存储在哪里？</strong></summary>
所有数据都存储在应用程序目录中的本地 `accounts.csv` 中。您也可以使用导出功能导出此数据。
</details>

<details>
<summary><strong>我看到 "Megatools not found" 错误。</strong></summary>
如果是从源代码运行，请确保已安装 `megatools` 并将其添加到您的系统 PATH。如果使用可执行文件，这会自动处理。
</details>

---

## :warning: 免责声明

此工具仅供 **教育和测试目的** 使用。严禁使用此软件滥用第三方服务、绕过限制或违反 MEGA.nz 或 Mail.tm 的服务条款 (ToS)。开发者对滥用不承担任何责任。

---

## :sparkling_heart: 致谢

*   基于 [f-o/MEGA-Account-Generator](https://github.com/f-o/MEGA-Account-Generator) 的原创作品。
*   GUI 组件由 [TomSchimansky/CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) 提供。
*   由 [byPancra](https://github.com/byPancra) 增强和维护。

---

## :copyright: 许可

根据 **MIT 许可** 分发。有关详细信息，请参阅 [LICENSE](LICENSE)。

<div align="center">
  <sub>Developed with ❤️ by <a href="https://github.com/byPancra">byPancra</a></sub>
</div>
