#!/bin/sh

lock() {
	pipenv lock --pre --clear
}

run () {
	pipenv run python .
}

freeze () {
	pipenv run pip freeze > requirements.txt
}


