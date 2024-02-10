.PHONY: install check-docker check-pre-commit env env_file

CDK_ENV := lib/.env.yaml
DOCKER_ENV := api/docker/.env

install: check-docker check-pre-commit env_file

	@# 依存関係のインストール
	npm ci

	@# vscode の設定をコピー
	cp .vscode/settings.sample.json .vscode/settings.json

	@# pre-commitの適応
	pre-commit install

	@# sam local invoke 時の DB 接続用ネットワークの作成
	docker network create stamp_rally_backend

	@# docker実行用のapp.envの作成
	npm run env

	# # python のライブラリインポートのための docker-compose の起動
	docker-compose -f api/docker/docker-compose.yaml up -d
	docker-compose -f api/docker/docker-compose.yaml run app poetry install

	# # db のマイグレーション
	./run.sh migrate

	@# runシェル用の環境変数を用意
	cp .env.sample .env

check-docker:
	@which docker > /dev/null 2>&1 || (echo "Docker not installed. Please install Docker."; exit 1)

check-pre-commit:
	@which pre-commit > /dev/null 2>&1 || (echo "pre-commit not installed. Please install pre-commit."; exit 1)

create_env:
	@# 環境変数のコピー
	@cp lib/.env.sample.yaml $(CDK_ENV)

	@# docker compose用のプロジェクト名、ポートの指定ファイルの準備
	@cp api/docker/.env.sample $(DOCKER_ENV)

	@which code > /dev/null 2>&1 && (code $(CDK_ENV) $(DOCKER_ENV);)

	@echo docker関連のenvファイル : "api/docker/.env"
	@echo 環境変数系             : "lib/.env.yaml"
	@echo それぞれ適切に書き換えてから
	@echo \`make install\`

env_file:
	@test -e $(CDK_ENV) || { echo "$(CDK_ENV) not found. Aborting."; exit 1; }
	@test -e $(DOCKER_ENV) || { echo "$(DOCKER_ENV) not found. Aborting."; exit 1; }
