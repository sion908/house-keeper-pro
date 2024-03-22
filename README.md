# house_keeper_pro_backend

fastapiをdockerで開発し，AWSのlambdaにデプロイするためのレポジトリ.  
backend用というわけではないですが，backend用に開発したのでそのまま名前についてます．  
なにかわからないことがあればお聞きください．  
わかるかはわからないですが...  
できるだけlinterに頼るようにしています．

## 開発手順

1. migrationの作成
2. `./run.sh doc fastapi`で実行しながらアプリの開発
3. testファイルの更新
4. `./run.sh invoke`でlocalで目指す挙動がされるかの確認
5. `dev`にデプロイして実際の環境で動くかの確認

## デプロイ

```shell
npm run cdk deploy -c environment={env} --profile {PROFILE}
```

または
```shell
cp .env.sample .env
```
したのちに、プロファイルを設定してから
```shell
./run.sh deploy
```

## fastAPIについて

このプロジェクトは基本的にfastAPIで実行しています  
関連の説明は,[apiフォルダ下のREADME](api/README.md)で確認する

### python プログラムの整形

flake8 を用いている  
純粋なflake8ではpoetryの設定ファイルが使えないので、.venvに入っているpflake8を利用している  
`api/src/`のみで、`api/tests`に対しては実行しない
docker における`app/`直下において`pflake8 src/`を実行する  
これの省略が

```shell
./run.sh doc(ker) f(lake8)   # 括弧内は省略可
```

原因は下記 URL で大体わかる  
https://www.flake8rules.com/rules/{E125}.html

## ローカルでのlambdaの実行

```shell
npm run invoke
```

または（下をまとめたのが上のコマンド）

1. テンプレートファイルの作成
   ```shell
   cdk synth-c environment=local
   ```
2. sam の実行
   ```shell
   sam local start-api -t ./cdk.out/HouseKeeperProStack-local.template.json --docker-network house_keeper_pro_backend
   ```

## localでの実行を行う場合

```shell
npm run invoke:ins  # 依存関係解決用のzipファイル作成とsynth,invokeのセット
```

1. python のライブラリインポートのための docker-compose の起動
   ```shell
   ./run.sh doc ins
   (docker-compose -f api/docker/docker-compose.yaml run app ./run.sh install)
   ```
   `python_module/dependences.zip`が作成される
2. local での実行 (synth と local invoke)
   ```shell
   npm run invoke
   ```

## REST Client

REAT の client ツールとして、vscodoe の拡張機能を利用  
詳しくは[README.md](rest_client/README.md)で確認する  
https://github.com/TheDesignium/house_keeper_pro_rest_client  
このレポジトリに実態は存在

## docs

APIのドキュメントは, `rest_client/openapi.yaml`で確認できます。

VScode の拡張機能[swaggerViewer](https://marketplace.visualstudio.com/items?itemName=Arjun.swagger-viewer)
または、
fastAPIを起動（`./run.sh doc fastapi`）して、http://0.0.0.0/docs より確認してください.
pre-commitで最新かを確認するようになっています

### APIドキュメントの更新
コンテナで作成する都合上、一度`src/`に生成してから移動するようにしています
```shell
./run.sh doc openapi
```

### git の関係

これ単体で用いることを考え、subTree として別のレポジトリとしている

```shell
git subtree push --prefix=rest_client rc main
```

で`rest_client`のブランチも更新されることになる

## 初期設定

1. 環境変数の作成と編集
   ```shell
   make create_env
   ```
   vscodeの場合は、
   `lib/.env.yaml`と
   `api/docker/.env`が開くのでそのまま編集して保存する。特にmysqlのポートに重複がないようにする。
2. 環境の作成
   ```shell
   make install
   ```

or

1. このリポジトリをクローンする
   ```shell
   git clone --recursive git@github.com:TheDesignium/0_rd_house_keeper_pro_backend.git
   ```
2. 依存関係をダウンロードする
   ```shell
   npm ci
   ```
3. docker がなければダウンロード
   (sam の実行と python のライブラリのダウンロードに必要)
4. vscode の設定をコピー

   1. メインの設定をコピー
      ライブラリなどの実行を docker でやっている関係で仮想環境上にライブラリがあるため
      ```shell
        cp .vscode/settings.sample.json .vscode/settings.json
      ```
   2. [REST client](rest_client/.vscode/settings.sample.json)の設定を追記
      `rest_client/.vscode/settings.sample.json`

5. pre-commit(python の整形ツール)
   1. インストール
      ```shell
      brew install pre-commit
      ```
   2. pre-commit の適応
      ```shell
      pre-commit install
      ```
6. docker compose用のプロジェクト名、ポートの指定ファイルの準備
   ```shell
   cp api/docker/.env.sample api/docker/.env
   ```
7.  sam local invoke 時の DB 接続用ネットワークの作成
   ```shell
   docker network create house_keeper_pro_backend
   ```
8.  環境変数のコピー
   ```shell
   cp lib/.env.sample.yaml lib/.env.yaml
   npm run env
   ```

9.  python のライブラリインポートのための docker-compose の起動
   ```shell
   docker-compose -f api/docker/docker-compose.yaml run app poetry install
   ```

10. db のマイグレーション

   ```shell
   ./run.sh migrate
   ```


## ディレクトリ構成

```python
.
├─ README.md                # これ
├─ api/                     # lambdaのスクリプト、以下はそこのREADME.mdを参照
├─ bin/                     # app定義ファイルを格納するフォルダ
├─ cdk.out/                 # cdk synthの出力ファイル
│                           # 非追跡（asset.../はログみたいなものなので最新以外消しても良い）
├─ lib/                     # cdkの定義ファイルなどを格納する
├─ test/                    # cdkのテスト アプデの時に使いやすい、cdkの設計思想が弱いため、使えない
├─ node_modules/            # cdk用のライブラリの保存場所、.vscodeにて非表示に設定
├─ rest_client/             # RESTのclient設定を定義したサブモジュール
├─ .pre-commit-config.yaml  # pre-commitの設定ファイル
├─ cdk.json                 # cdk実行のためのの設定ファイル
├─ jest.config.js           # tsのlinter設定ファイル
├─ run.sh                   # 全体的なコマンドを確認するためのシェルスクリプト, ./run.shで内容確認
└─ tsconfig.json            # typescriptの設定ファイル
```

## 参考

本リポジトリは NEC ソリューションイノベータ Advent Calendar 2022 の掲載記事のソースコードを参考にしています。

- [NEC ソリューションイノベータ Advent Calendar 2022](https://qiita.com/advent-calendar/2022/nec_solution_innovators)
- [CDK の APIGateway+Lambdan 構成を OpenAPI の定義から作成する](https://qiita.com/stake15/items/2616a568593d48e5bd16)
- [minio](https://qiita.com/reflet/items/3e0f07bc9d64314515c1)
