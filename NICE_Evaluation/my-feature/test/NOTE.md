# log
1. environment.yml -> 可以 built, 但是會有 dependency conflict 的問題 -> 很麻煩
2. minienv.yml -> 嘗試減少版本控制的問題，讓 conda 去自己決定

## 1. 安裝 anaconda

[利用 conda 建立虛擬環境](https://simplelearn.tw/python-conda-virtual-environment/)

```
# 進入 condaPrompt
# 創建 env (根據自己需求選擇)
conda create -n testenv python=3.12
conda activate testenv
```


## 2. 要先轉換 requirements.txt 成 pip 可以接受的格式 (有點問題 ?)

```
# 使用 pip freeze 輸出 pip 格式的 requirements.txt
pip freeze > requirements.txt
```

## 3. 安裝 requirements

```
pip install -r requirements.txt
```

## 4. 安裝 Pytorch

```
# 在網站上選擇好對應的環境（例如 Linux + Conda + CUDA 11.8）
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
```

## 5. 白癡
```
# 'vgg9' 要去掉 ''
python hw_inference.py --num_steps 5 --arch 'vgg9' --batch_size 128 --b_size 4 --ADC_precision 4 --quant 4 --xbar_size 64
```

```
# 去掉 '', --arch vgg9 才對
python hw_inference.py --num_steps 5 --arch vgg9 --batch_size 128 --b_size 4 --ADC_precision 4 --quant 4 --xbar_size 64
```

## 6. 還是搞不出來 ...

# second try

## 原本檔案出現 error (因為混雜 pip & conda 的指令)
> 分開並且儲存成 .yaml

## 把 pip 跟 conda 分開儲存成 .yaml 格式
> SRC: requirements.yaml
> EXECUTE: conda create -f requirements.yaml

```
[ERR]
ResolvePackageNotFound:
  - nvidia-ml-py3=7.352.0
  - fastai=1.0.61
  - fastprogress=0.2.2
  - torchvision=0.6.1
```

## 把所有的版本號去掉 (2025.6.14)
> SRC: minienv.yml

```
Solving environment: failed

ResolvePackageNotFound:
  - nvidia-ml-py3
```

## 把 nvidia-ml-py3 改到 pip 安裝就可以了
> SRC: minienv.yml
# cuda 問題
您的 Windows 系統已經正確安裝了 NVIDIA 驅動程式 (560.94)，支援 CUDA 12.6。現在需要在 WSL 中設置 CUDA 支援。

## 在 WSL 中啟用 CUDA

1. **確認 WSL 版本**（在 PowerShell 中執行）：
   ```powershell
   wsl --list --verbose
   ```
   確保您使用的是 WSL 2

2. **在 WSL 中安裝 CUDA**：
   ```bash
   # 更新套件
   sudo apt update && sudo apt upgrade -y
   
   # 安裝開發工具
   sudo apt install build-essential -y
   
   # 安裝 CUDA (選擇與 Windows 驅動程式相容的版本)
   wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-wsl-ubuntu.pin
   sudo mv cuda-wsl-ubuntu.pin /etc/apt/preferences.d/cuda-repository-pin-600
   sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/3bf863cc.pub
   sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/ /"
   
   sudo apt update
   sudo apt install cuda -y
   ```

3. **設置環境變數**：
   ```bash
   echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
   echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
   source ~/.bashrc
   ```

4. **安裝 CUDA 版本的 PyTorch**：
   ```bash
   # 使用 CUDA 12.x (與您的驅動相符)
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

5. **重新啟動 WSL**（在 PowerShell 中執行）：
   ```powershell
   wsl --shutdown
   ```
   然後重新開啟 WSL 終端

6. **檢查 CUDA 是否可用**：
   在 WSL 中運行：
   ```bash
   nvidia-smi  # 應顯示與 Windows 相同的 GPU
   python -c "import torch; print(torch.cuda.is_available())"  # 應返回 True
   ```

完成這些步驟後，您的 WSL 環境中的 PyTorch 應該可以使用 CUDA，您便可以繼續執行原始程式碼而無需修改 `.cuda()` 調用。

Similar code found with 2 license types

## 終於可以執行了 (用 gpu training)
# 程式碼分析：硬體感知神經網路推論模擬

從錯誤訊息和參數中，我可以分析出這個程式碼是在模擬神經網路在特定硬體架構上的推論過程。具體來說：

## 主要功能

這個程式碼模擬的是**神經網路在類比運算陣列硬體上的推論**，特別關注於在交叉陣列架構（crossbar arrays）上實現卷積神經網路(CNN)。

## 關鍵元件

1. **硬體模型**：模擬特定硬體架構（可能是基於SRAM或RRAM的交叉陣列）
2. **量化**：使用低位元精度（參數`--quant 4`表示4比特量化）
3. **ADC轉換**：模擬類比數位轉換器（`--ADC_precision 4`）
4. **交叉陣列**：模擬大小為64x64的矩陣乘法陣列（`--xbar_size 64`）

## 工作流程

1. 載入預訓練的VGG9神經網路模型
2. 將模型參數轉換為硬體友好格式（量化、編碼）
3. 模擬硬體上的卷積、池化操作
4. 模擬電流輸出、ADC轉換等物理特性
5. 計算最終推論結果和準確率

## 特殊功能

這段程式碼特別模擬了以下硬體特性：

- 交叉陣列大小的限制和分割
- 量化導致的精度損失
- 類比電流求和和轉換
- 可能的非理想效應（如設備變異）

這種模擬對於理解和優化神經網路在特定類比計算硬體上的性能和能耗非常重要。