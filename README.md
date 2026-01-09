<div align="center">

[English](https://github.com/byPancra/MEGA-Account-Generator-GUI) | [Português (Brasil)](https://github.com/byPancra/MEGA-Account-Generator-GUI/tree/lang-pt-BR) | [Español](https://github.com/byPancra/MEGA-Account-Generator-GUI/tree/lang-es) | [日本語](https://github.com/byPancra/MEGA-Account-Generator-GUI/tree/lang-ja) | **繁體中文** | [简体中文](https://github.com/byPancra/MEGA-Account-Generator-GUI/tree/lang-zh-CN)

</div>
<br>

<div align="center">

</div>

<div align="center">

  ![Mega Account Generator GUI](./img/readme-icon.png)

  <h1 align="center">Mega Account Generator GUI</h1>
  
  **自動化 MEGA.nz 帳戶建立與管理的終極工具。**
  
  *使用專業級介面產生、管理、標記和匯出您的帳戶。*

  [![Python Version](https://img.shields.io/badge/python-3.8%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
  [![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](./LICENSE)
  [![Status](https://img.shields.io/badge/status-active-success?style=for-the-badge)]()
  [![Releases](https://img.shields.io/github/downloads/byPancra/Mega-Account-Generator-GUI/total?style=for-the-badge&color=orange)](https://github.com/byPancra/Mega-Account-Generator-GUI/releases)

  [功能](#-功能) • [安裝](#-安裝) • [使用方法](#-使用方法) • [進階管理](#-進階管理) • [常見問題](#-常見問題)

</div>

---

## 📋 概覽

**Mega Account Generator GUI** 是一款強大的桌面級應用程式，專為需要大量產生和管理 [MEGA.nz](https://mega.nz) 帳戶的進階使用者而設計。與簡單的腳本不同，此工具提供了一個完整的帳戶生命週期管理生態系統，包括標記、過濾、狀態追蹤和資料匯出。

使用 **Modern Python** (CustomTkinter) 和 **執行緒安全架構** 建置，即使處理數百個帳戶也能確保可靠性。

![Demo](./img/intro2.gif)

---

## :zap: 功能

### 🚀 核心產生
*   **高速多執行緒**：同時產生多達 8 個帳戶。
*   **智慧速率限制**：智慧延遲和重試邏輯（最多 12 次嘗試）以繞過 Mail.tm 限制。
*   **內建相依性**：執行檔版本預先封裝了 `megatools`，無需額外設定。

### 🛠️ 進階管理
*   **標記系統**：使用自訂標籤（例如 `個人`、`備份`、`客戶-A`）組織帳戶，以便於檢索。
*   **搜尋與過濾**：依電子郵件、狀態（`有效`、`停用`、`失敗`）或標籤即時尋找帳戶。
*   **批次操作**：
    *   **保持活躍**：自動登入以防止帳戶因不活動而被刪除。
    *   **儲存檢查**：自動更新所有帳戶的使用/可用儲存配額。
    *   **帳戶控制**：停用特定帳戶以將其排除在批次操作（例如保持活躍檢查）之外，而在不刪除它們的情況下。

### 💾 資料自由
*   **專業匯出**：將您的資料庫匯出為 **Excel (.xlsx)** 以獲得格式化樣式，或匯出為 **JSON** 以供程式化使用。
*   **無縫匯入**：透過 JSON/Excel 匯入從其他工具或備份轉移資料。
*   **剪貼簿整合**：一鍵複製電子郵件和密碼。

### 🔒 安全與可靠性
*   **執行緒安全 CSV**：防止同時寫入期間的資料損毀。
*   **崩潰復原**：「停止」按鈕可優雅地停止操作，保留資料完整性。

---

## :rocket: 安裝

### 選項 A：獨立執行檔（推薦）
下載最新版本。無需 Python 或外部工具。
1.  從 [Releases](https://github.com/byPancra/Mega-Account-Generator-GUI/releases) 下載 `MegaGenerator.exe`。
2.  執行該執行檔。

### 選項 B：從原始碼執行

**先決條件：**
*   Python 3.8+
*   [Megatools](https://megatools.megous.com/) (已新增至 PATH)

**步驟：**
1.  **複製儲存庫：**
    ```bash
    git clone https://github.com/byPancra/Mega-Account-Generator-GUI.git
    cd Mega-Account-Generator-GUI
    ```

2.  **安裝相依性：**
    ```bash
    pip install -r requirements.txt
    ```

3.  **執行應用程式：**
    ```bash
    python gui.py
    ```

---

## :computer: 使用方法

### 產生帳戶
1.  導覽至 **Generator**（產生器）分頁。
2.  設定 **Threads**（執行緒）和 **Accounts**（帳戶）的數量以進行產生。
3.  點擊 **"Generate Accounts"**（產生帳戶）。
4.  憑證將儲存在 `accounts.csv` 中，並顯示在 **Stored Accounts**（已儲存帳戶）分頁中。

### 管理帳戶
導覽至 **Stored Accounts**（已儲存帳戶）分頁：
*   **搜尋**：輸入電子郵件以即時過濾。
*   **過濾**：使用下拉式選單僅查看 `Active`（有效）、`Disabled`（停用）或 `Failed`（失敗）的帳戶。
*   **編輯**：點擊 "Edit"（編輯）按鈕以更改已儲存的密碼或管理標籤。
*   **複製**：快速按鈕將憑證複製到剪貼簿。

### 💻 CLI 使用方法（命令列）
適合偏好終端機或希望將其整合到腳本中的進階使用者。

```bash
# 基本使用（產生 3 個帳戶）
python generate_accounts.py

# 使用 5 個執行緒產生 50 個帳戶
python generate_accounts.py -n 50 -t 5

# 為所有帳戶設定特定密碼
python generate_accounts.py -n 10 -p "MySecretPass123!"
```

**引數：**
*   `-n`, `--number`：要建立的帳戶數量（預設：3）
*   `-t`, `--threads`：同時執行緒數量 (1-8)
*   `-p`, `--password`：所有帳戶的通用密碼（選用）

#### 保持活躍檢查（登入與儲存）
驗證 `accounts.csv` 中的所有帳戶，檢查其儲存配額，並保持其活躍：

```bash
python signin_accounts.py
```

*   **無需引數。**
*   迭代 `accounts.csv` 中的所有帳戶。
*   **跳過標記為 "Disabled"（停用）的帳戶。**
*   更新狀態為 `Active`（有效）或 `Login Failed`（登入失敗）。
*   更新已使用/可用儲存值。


---

## :briefcase: 進階管理

### 匯出資料
您可以匯出整個帳戶資料庫以進行備份或外部使用。
1.  點擊右上角的 **Export**（匯出）。
2.  選擇 **Excel** 以獲得格式化試算表，或 **JSON** 以獲得原始資料。
3.  選擇儲存位置。

*Excel 匯出包含顏色編碼的狀態欄位和格式化標題，便於閱讀。*

### 匯入資料
從以前的版本或其他工具轉移。
1.  點擊 **Import**（匯入）。
2.  選擇有效的 `.json` 或 `.xlsx` 檔案。
3.  工具會將資料合併到您的 `accounts.csv` 中。

---

## :grey_question: 常見問題

<details>
<summary><strong>為什麼我被限制為 8 個執行緒？</strong></summary>
臨時電子郵件提供者 (Mail.tm) 有嚴格的速率限制。超過 8 個同時執行緒會顯著增加 IP 被封鎖或產生失敗的機會。
</details>

<details>
<summary><strong>"Sign In"（登入）按鈕有什麼作用？</strong></summary>
它執行「保持活躍」檢查。它嘗試使用 `megatools` 登入您的帳戶。這會更新儲存配額資訊並向 MEGA 發出訊號表示帳戶處於活躍狀態，防止被刪除。
</details>

<details>
<summary><strong>我的帳戶儲存在哪裡？</strong></summary>
所有資料都儲存在應用程式目錄中的本機 `accounts.csv` 中。您也可以使用匯出功能匯出此資料。
</details>

<details>
<summary><strong>我看到 "Megatools not found" 錯誤。</strong></summary>
如果是從原始碼執行，請確保已安裝 `megatools` 並將其新增至您的系統 PATH。如果使用執行檔，這會自動處理。
</details>

---

## :warning: 免責聲明

此工具僅供 **教育和測試目的** 使用。嚴禁使用此軟體濫用第三方服務、繞過限制或違反 MEGA.nz 或 Mail.tm 的服務條款 (ToS)。開發者對濫用不承擔任何責任。

---

## :sparkling_heart: 致謝

*   基於 [f-o/MEGA-Account-Generator](https://github.com/f-o/MEGA-Account-Generator) 的原創作品。
*   GUI 元件由 [TomSchimansky/CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) 提供。
*   由 [byPancra](https://github.com/byPancra) 增強和維護。

---

## :copyright: 授權

根據 **MIT 授權** 分發。有關詳細資訊，請參閱 [LICENSE](LICENSE)。

<div align="center">
  <sub>Developed with ❤️ by <a href="https://github.com/byPancra">byPancra</a></sub>
</div>
