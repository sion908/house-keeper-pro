#!/bin/bash

# AWSプロファイルの読み込み
source .env

if [ $# = 0 ]; then

  echo "doc(ker)     -> docker系の実行"
  echo "                .ex: ./run.sh doc ps"
  echo "se(rver)     -> server系の内部実行"
  echo "  fl(ake8)     flake8の実行"
  echo "  b(ash)       bashの実行"
  echo "  in(stall)    依存関係のzipファイル作成"
  echo "  fa(stapi)    fastApiの実行"
  echo "  op(enapi)    openAPIの再生成"
  echo "  (py)te(st)   pytestの実行"
  echo "in(voke)     -> ローカルでの実行"
  echo "  i(nstall)     依存関係のzip作成もセット"
  echo "mi(grate)    -> マイグレーションの実行, (引数ありでその環境に対して)"
  echo "de?p(loy)    -> デプロイ"
  exit 1

elif [[ $1 =~ pre(-commit)? ]]; then
    docker-compose -f api/docker/docker-compose.yaml exec app poetry run pflake8
elif [[ $1 =~ doc(ker)? ]]; then
    shift;
    echo docker-compose -f api/docker/docker-compose.yaml $@
    docker-compose -f api/docker/docker-compose.yaml $@

elif [[ $1 =~ se(rver)? ]]; then

    if [[ $2 =~ fl(ake8)? ]]; then
        echo docker-compose exec app poetry run pflake8 src/
        docker-compose -f api/docker/docker-compose.yaml exec app poetry run pflake8 src/
        exit 1
    elif [[ $2 =~ b(ash)? ]]; then
        echo docker-compose exec app bash
        docker-compose -f api/docker/docker-compose.yaml exec app bash
        exit 1
    elif [[ $2 =~ in(stall)? ]]; then
        echo docker-compose run app ./run.sh install
        docker-compose -f api/docker/docker-compose.yaml exec app ./run.sh install
        exit 1
    elif [[ $2 =~ fa(stapi)? ]]; then
        echo docker-compose exec app ./run.sh fastapi
        docker-compose -f api/docker/docker-compose.yaml exec app ./run.sh fastapi
        exit 1
    elif [[ $2 =~ op(enapi)? ]]; then
        echo docker-compose exec app poetry run fastapi_to_openapi -i src/main
        docker-compose -f api/docker/docker-compose.yaml exec app poetry run fastapi_to_openapi -i src/main
        mv api/openapi.yaml rest_client/openapi.yaml
        exit 1
    elif [[ $2 =~ (py)?te(st)? ]]; then
        pytest_cmd="pytest"
        if [[ $2 =~ lf ]]; then
            pytest_cmd="${pytest_cmd} --lf"
        fi
        # やったもののみ --lf
        shift;shift;
        echo docker-compose exec app poetry run $pytest_cmd $@
        docker-compose -f api/docker/docker-compose.yaml exec app poetry run $pytest_cmd $@
        exit 1
    fi

    shift

    echo docker-compose -f api/docker/docker-compose.yaml exec app $@
    docker-compose -f api/docker/docker-compose.yaml exec app $@

elif [ $1 = "db" ]; then
    echo -e "- local      : local_db\n- local_test : local_test_db\n"
    if command -v mysql &> /dev/null; then
        echo 'mysql -u root -h 127.0.0.1 --port 33306 -t local_db -p'
        mysql -u root -h 127.0.0.1 --port 53306 -t local_db -p
    else
        echo "docker-compose exec db bash"
        echo " -> mysql -u root -p"
        docker-compose -f api/docker/docker-compose.yaml exec db mysql -u root -t local_db -p
    fi

elif [[ $1 =~ in(voke)? ]]; then

    if [[ $2 =~ i(nstall)? ]]; then

    echo docker-compose -f api/docker/docker-compose.yaml run app ./run.sh install
    docker-compose -f api/docker/docker-compose.yaml run app ./run.sh install
    fi


    echo npm run cdk -c environment=local synth
    npm run cdk:local synth

    echo sam local start-api
    sam local start-api -t ./cdk.out/StampRallyStack-dev.template.json --docker-network stamp_rally_backend
elif [[ $1 =~ mi(grate)? ]]; then
    if [ $# -eq 2 ]; then
        echo npm run env -- -e $2
        npm run env -- -e $2
    fi
    echo docker-compose doc exec app ./run.sh alembic migrate
    docker-compose -f api/docker/docker-compose.yaml run --rm app ./run.sh al mi
    npm run env
    exit 1

elif [[ $1 =~ de?p(loy)? ]]; then
    if [ "$2" = "prod" ]; then
        echo npm run cdk:prod deploy -- --profile $PROFILE
        npm run cdk:prod deploy -- --profile $PROFILE
        exit 1
    fi

    echo npm run cdk:dev deploy -- --profile $PROFILE
    npm run cdk:dev deploy -- --profile $PROFILE
    exit 1

fi
