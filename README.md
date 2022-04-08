# UDEV Gothic

UDEV Gothic は、ユニバーサルデザインフォントの [BIZ UDゴシック](https://github.com/googlefonts/morisawa-biz-ud-gothic) と、 開発者向けフォントの [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono) を合成した、プログラミング向けフォントです。

BIZ UDゴシックの優れた機能美はそのままに、調和的で判読性の高い英数字を提供することを目指しています。

[👉 ダウンロード](https://github.com/yuru7/udev-gothic/releases)  
※「Assets」内の zip ファイルをダウンロードしてご利用ください。

## 特徴

以下の特徴を備えています。

- モリサワ社の考えるユニバーサルデザインが盛り込まれたBIZ UDゴシック由来の読み易い日本語文字
- IntelliJ などの開発環境を提供することで知られる JetBrains 社が手掛けた JetBrains Mono 由来のラテン文字
  - `0` を従来のドットゼロからスラッシュゼロにするなど、BIZ UDゴシックとさらに調和することを目指した。
- BIZ UDゴシック相当の IVS (異体字シーケンス) に対応 (対応している異体字リストは [こちら](https://raw.githubusercontent.com/yuru7/udev-gothic/main/doc/ivs.txt))
- 全角スペースの可視化
- 収録される文字の違い等によって分かれた複数のバリエーションを用意 (下記参照)

### バリエーションについて

| バリエーション|説明|命名パターン |
| --- | --- | --- |
| 文字幅比率 半角3:全角5 | JetBrains Mono を縮小せずに合成し、半角3:全角5の文字幅比率としたバリエーション。通常版と比べ、半角文字がゆとりを持った幅で表示される。| `UDEVGothic35*-*.ttf`<br>※ファイル名に `35` が含まれたもの |
| 日本語文書向け | 日本語文書で頻出する記号類 ( `← ↓ ↑ → □ ■ …` など) がBIZ UDゴシックの全角記号で表示される。 ※通常版の UDEV Gothic では、JetBrains Mono のグリフが優先されるため半角で表示される。 (全角表示されるようになる記号一覧は [こちら](doc/JPDOC.txt)) | `UDEVGothic*JPDOC*-*.ttf`<br>※ファイル名に `JPDOC` が含まれたもの |
| リガチャ対応版 | JetBrains Mono に含まれるリガチャに対応したバリエーション。 | `UDEVGothic*LG*-*.ttf`<br>※ファイル名に `LG` が含まれたもの |
| Nerd Fonts 対応版 | [Nerd Fonts](https://www.nerdfonts.com/) を追加合成したバリエーション。拡張Powerline記号など、お洒落なターミナルで利用される記号を収録。<br>⚠ 制限事項あり (*1) | `UDEVGothic*NF*-*.ttf`<br>※ファイル名に `NF` が含まれたもの |

> ⚠ *1: Nerd Fonts の仕様により一部の漢字グリフが Nerd Fonts グリフに上書きされるため、`﨑` のような旧字体など一部のコードポイントで、漢字ではなく Nerd Fonts のアイコンが表示されます。また、この影響で IVS (異体字シーケンス) にも当該バリエーションでは非対応となります。Nerd Fonts を必要とする用途以外は、NF版以外のバリエーションを利用することを推奨します。

## 表示サンプル

![image](https://user-images.githubusercontent.com/13458509/160800245-9d9fce55-f980-46ce-b630-63e439fc3f27.png)

| リガチャ ON | リガチャ OFF |
| :---: | :---: |
| ![image](https://user-images.githubusercontent.com/13458509/159891788-b97865ee-9b94-4691-b44e-f39f55a8bdef.png) | ![image](https://user-images.githubusercontent.com/13458509/159892000-99b356e5-42d0-4007-85eb-424abc386a05.png) |
