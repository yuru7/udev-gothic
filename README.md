# UDEV Gothic

UDEV Gothic は、ユニバーサルデザインフォントの [BIZ UDゴシック](https://github.com/googlefonts/morisawa-biz-ud-gothic) と、 開発者向けフォントの [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono) を合成した、プログラミング向けフォントです。

BIZ UDゴシックの優れた機能美はそのままに、調和的で判読性の高い英数字を提供することを目指しています。

[👉 ダウンロード](https://github.com/yuru7/udev-gothic/releases)

## 特徴

以下の特徴を備えています。

- モリサワ社の考えるユニバーサルデザインが盛り込まれたBIZ UDゴシック由来の読み易い日本語文字
- IntelliJ などの開発環境を提供することで知られる JetBrains 社が手掛けた JetBrains Mono 由来のラテン文字
  - `0` を従来のドットゼロからスラッシュゼロにするなど、BIZ UDゴシックとさらに調和すること目指した
- BIZ UDゴシック相当の IVS (異体字シーケンス) に対応 (対応している異体字リストは [こちら](https://raw.githubusercontent.com/yuru7/udev-gothic/main/doc/ivs.txt))
- 全角スペースの可視化
- JetBrains Mono に含まれるリガチャに対応したバリエーションを同梱
  - `UDEVGothicLG-<Weight>.ttf` のように、ファイル名に `LG` が含まれているものが対象
- 日本語文書で頻出する記号類 ( `← ↓ ↑ → □ ■ …` など) でBIZ UDゴシックの全角記号が優先して表示されるバリエーションを同梱
  - `UDEVGothicJPDOC-<Weight>.ttf` のように、ファイル名に `JPDOC` が含まれているものが対象
  - 標準の UDEV Gothic では、JetBrains Mono のグリフが優先されるため、該当の記号は通常版では半角で表示される

![image](https://user-images.githubusercontent.com/13458509/159846115-826e87f5-90e6-4f10-90f5-652e4790f0ff.png)

|リガチャ ON|リガチャ OFF|
|:---:|:---:|
|![image](https://user-images.githubusercontent.com/13458509/159891788-b97865ee-9b94-4691-b44e-f39f55a8bdef.png)|![image](https://user-images.githubusercontent.com/13458509/159892000-99b356e5-42d0-4007-85eb-424abc386a05.png)|
