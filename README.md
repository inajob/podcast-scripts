# これは何？

話題ごとに分割されたオーディオファイルを読み込み、ポッドキャスト番組としての体裁を整えた音声ファイルにするためのAudacityのためのPythonスクリプトです

# 使い方

`in_folder`に入っているm4aのオーディオファイルをうまいことつなげてポッドキャスト番組を作成します。

始めのオーディオファイルと最後のオーディオファイルの部分で`bgm_sound`がいい感じに鳴ります。

最後以外のオーディオファイルの継ぎ目で`change_sound`が鳴ります。


Audacityを起動した状態で、以下のように実行します。
（Windowsの場合は管理者でコマンドプロンプトを開く必要があります）

```
$ python make-tameroku.py <in_folder> <change_sound> <bgm_sound>
```

# 変換例

- [#inajob の試しに録音してみた](https://open.spotify.com/show/6nDe9T61ZUBvLWfavKS98y) はこのスクリプトで生成しています

# 参考

- [Audacity Script - DTMプログラミング言語探訪](https://qiita.com/aike@github/items/413d614d358450026d98)

