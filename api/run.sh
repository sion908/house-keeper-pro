#!/bin/bash


if [ $# = 0 ]; then

  echo "ins(tall)             -> ライブラリのインポートなど"
  echo "is(ort)               -> importのsort"
  echo "pf(lake8)             -> flake8の実行"
  echo "al(embic)             -> alembicの実行"
  echo "  c(reate)m(igration) -> migrationファイルの生成(第二引数必須)"
  echo "  mi(grate)           -> 最新版のmigrationまで適応する"
  echo "fa(stapi)             -> fastApiの実行"
  exit 1

elif [[ $1 =~ ins(tall)? ]]; then
  if [ pwd = '/app' ]; then
    echo 動作ディレクトリはapiです
    exit 1
  fi
  if [ ! -e python_modules ]; then
    mkdir python_modules
  fi

  cd /api/python_modules/

  echo poetry export -o requirements.txt --without-hashes
  poetry export -o requirements.txt --without-hashes

  echo pwd
  pwd

  rm -rf /api/python_modules/python
  echo python -m pip install -r requirements.txt -t /api/python_modules/python/lib/python3.10/site-packages/
  python -m pip install -r requirements.txt -t /api/python_modules/python/lib/python3.10/site-packages/ --upgrade
  echo installed lib
  if [ ! -e python ]; then
    mkdir python
  fi

  zip -r dependencies.zip python

elif [[ $1 =~ is(ort)? ]]; then
  echo poetry run isort /api/src/
  poetry run isort /api/src/

elif [[ $1 =~ pf(lake8)? ]]; then
  if [ $# -eq 1 ]; then
    echo poetry run pflake8 src/
    # poetry run pflake8 src/
    exit 1
  fi

  # 引数を処理して最後の要素を取得し、スペースで結合
  result=""
  # shift
  for arg in "${@:2}"; do
    arg_without_api="${arg#api/}"
    result="$result $arg_without_api"
  done

  # 結果を表示
  # echo poetry run pflake8 $result
  poetry run pflake8 $result

elif [[ $1 =~ al(embic)? ]]; then
  if [[ $2 =~ c(reate)?m(igration)? ]]; then
    if [ $# -lt 3 ]; then
      echo 説明を記入してください
      exit 1
    fi
    cd src/
    echo poetry run alembic -c database/alembic.ini revision --autogenerate -m \"$3\"
    poetry run alembic -c database/alembic.ini revision --autogenerate -m \"$3\"
    exit 1
  elif [[ $2 =~ mi(grate)? ]]; then
    cd src/
    echo poetry run alembic -c database/alembic.ini upgrade head
    poetry run alembic -c database/alembic.ini upgrade head
    exit 1
  fi

  shift

  cd src/
  echo poetry run alembic -c database/alembic.ini $@
  poetry run alembic -c database/alembic.ini $@

elif [[ $1 =~ fa(stapi)? ]]; then
  cd src/
  echo poetry run uvicorn main:app
  poetry install
  poetry run uvicorn main:app --reload --host 0.0.0.0 --port 80

elif [[ $1 =~ (py)?te(st)? ]]; then
  shift;
  poetry run pytest $@
  exit 1
fi
