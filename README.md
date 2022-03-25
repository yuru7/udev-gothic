# udev-gothic
UDEV Gothic は、ユニバーサルデザインフォントの [BIZ UDゴシック](https://github.com/googlefonts/morisawa-biz-ud-gothic) と、 開発者向けフォントの [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono) を合成した、プログラミング向けフォントです。

[👉 ダウンロード](https://github.com/yuru7/udev-gothic/releases)

以下の特徴を備えています。

- モリサワ社の考えるユニバーサルデザインが盛り込まれたBIZ UDゴシック由来の日本語文字
- IntelliJ などの開発環境を提供することで知られる JetBrains 社が手掛けた JetBrains Mono 由来のラテン文字
- BIZ UDゴシック相当の IVS (異体字シーケンス) に対応 (対応している異体字リストは [こちら](https://raw.githubusercontent.com/yuru7/udev-gothic/main/doc/ivs.txt))
- 全角スペースの可視化
- JetBrains Mono に含まれるリガチャに対応したバージョンを同梱
  - `UDEVGothicLG-<Weight>.ttf` のように、ファイル名に `LG` が含まれているものが対象
- 日本語文書で頻出する記号類 ( `← ↓ ↑ → □ ■ …` など) でBIZ UDゴシックの全角記号が優先して表示されるバージョンを同梱
  - `UDEVGothicJPDOC-<Weight>.ttf` のように、ファイル名に `JPDOC` が含まれているものが対象
  - 標準の UDEV Gothic は、JetBrains Mono のグリフが優先されるため、該当する記号は半角表示となる。

![image](https://user-images.githubusercontent.com/13458509/159846115-826e87f5-90e6-4f10-90f5-652e4790f0ff.png)

|リガチャ ON|リガチャ OFF|
|:---:|:---:|
|![image](https://user-images.githubusercontent.com/13458509/159891788-b97865ee-9b94-4691-b44e-f39f55a8bdef.png)|![image](https://user-images.githubusercontent.com/13458509/159892000-99b356e5-42d0-4007-85eb-424abc386a05.png)|
