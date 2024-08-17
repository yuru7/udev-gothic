# UDEV Gothic

UDEV Gothic は、ユニバーサルデザインフォントの [BIZ UDゴシック](https://github.com/googlefonts/morisawa-biz-ud-gothic) と、 開発者向けフォントの [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono) を合成した、プログラミング向けフォントです。

BIZ UDゴシックの優れた機能美はそのままに、調和的で判読性の高い英数字を提供することを目指しています。

[👉 ダウンロード](https://github.com/yuru7/udev-gothic/releases/latest)  
※「Assets」内の zip ファイルをダウンロードしてご利用ください。

> 💡 その他、公開中のプログラミングフォント
> - 日本語文字に源柔ゴシック、英数字部分に Hack を使った [**白源 (はくげん／HackGen)**](https://github.com/yuru7/HackGen)
> - 日本語文字に IBM Plex Sans JP、英数字部分に IBM Plex Mono を使った [**PlemolJP (プレモル ジェイピー)**](https://github.com/yuru7/PlemolJP)
> - 日本語文字に源真ゴシック、英数字部分に Fira Mono を使った [**Firge (ファージ)**](https://github.com/yuru7/Firge)

## 特徴

以下の特徴を備えています。

- モリサワ社の考えるユニバーサルデザインが盛り込まれたBIZ UDゴシック由来の読み易い日本語文字
- IntelliJ などの開発環境を提供することで知られる JetBrains 社が手掛けた JetBrains Mono 由来のラテン文字
  - `0` を従来のドットゼロからスラッシュゼロにするなど、BIZ UDゴシックとさらに調和することを目指した。
- BIZ UDゴシック相当の IVS (異体字シーケンス) に対応 (対応している異体字リストは [こちら](https://raw.githubusercontent.com/yuru7/udev-gothic/main/doc/ivs.txt))
- 全角スペースの可視化
- 収録される文字の違い等によって分かれた複数のバリエーションを用意 (下記参照)

### バリエーション

| 種類 | 説明 | 命名パターン |
| --- | --- | --- |
| 文字幅比率 半角1:全角2 | JetBrains Mono を縮小することで、半角1:全角2の文字幅比率となるように合成したバリエーション。 | `UDEVGothic*-*.ttf`<br>※ファイル名に `35` が含まれて **いない** もの |
| 文字幅比率 半角3:全角5 | JetBrains Mono を縮小せずに合成し、半角3:全角5の文字幅比率としたバリエーション。半角1:全角2と比べ、英数字などの半角文字がゆとりのある幅で表示される。| `UDEVGothic35*-*.ttf`<br>※ファイル名に `35` が含まれて **いる** もの |
| 日本語文書向け | 日本語文書で頻出する記号類 ( `← ↓ ↑ → □ ■ …` など) がBIZ UDゴシックの全角記号で表示される。 ※通常版の UDEV Gothic では、JetBrains Mono のグリフが優先されるため半角で表示される。 (全角表示されるようになる記号一覧は [こちら](doc/JPDOC.txt)) | `UDEVGothic*JPDOC*-*.ttf`<br>※ファイル名に `JPDOC` が含まれたもの |
| リガチャ対応版 | JetBrains Mono に含まれるリガチャに対応したバリエーション。 | `UDEVGothic*LG*-*.ttf`<br>※ファイル名に `LG` が含まれたもの |
| Nerd Fonts 対応版 | [Nerd Fonts](https://www.nerdfonts.com/) を追加合成したバリエーション。拡張Powerline記号など、お洒落なターミナルで利用される記号を収録。 | `UDEVGothic*NF*-*.ttf`<br>※ファイル名に `NF` が含まれたもの |

## 表示サンプル

| 通常版 (幅比率 半角1:全角2) | 35版 (幅比率 半角3:全角5) |
| :---: | :---: |
| ![image](https://user-images.githubusercontent.com/13458509/163554505-af07d1b1-574a-42a0-a7c4-01cccef75537.png) | ![image](https://user-images.githubusercontent.com/13458509/163554472-de0ebb09-9f82-4d61-8c68-51dbc938858a.png) |

| リガチャ ON | リガチャ OFF |
| :---: | :---: |
| ![image](https://user-images.githubusercontent.com/13458509/159891788-b97865ee-9b94-4691-b44e-f39f55a8bdef.png) | ![image](https://user-images.githubusercontent.com/13458509/159892000-99b356e5-42d0-4007-85eb-424abc386a05.png) |

## ビルド

環境:

- fontforge: `20230101` \[[Windows](https://fontforge.org/en-US/downloads/windows/)\] \[[Linux](https://fontforge.org/en-US/downloads/gnulinux/)\]
- Python: `>=3.12`

### Windows (PowerShell Core)

```sh
# 必要パッケージのインストール
pip install -r requirements.txt
# ビルド
& "C:\Program Files (x86)\FontForgeBuilds\bin\ffpython.exe" .\fontforge_script.py && python3 .\fonttools_script.py
```

### ビルドオプション

`fontforge_script.py` 実行時、以下のオプションを指定できます。

- `--35`: 半角3:全角5 の幅にする
- `--jpdoc`: 日本語文書頻出記号を全角にする
- `--nerd-font`: Nerd Fonts を追加合成する
- `--liga`: リガチャを加える
- `--hidden-zenkaku-space`: 全角スペース可視化を無効化
- `--dot-zero`: `0` をドットゼロにする

## ライセンス

SIL OPEN FONT LICENSE Version 1.1 が適用され、商用・非商用問わず利用可能です。
詳細は [LICENSE](https://raw.githubusercontent.com/yuru7/udev-gothic/main/LICENSE) を参照
