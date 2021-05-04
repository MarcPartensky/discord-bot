#!/bin/sh

lock() {
	pipenv lock --pre --clear
}

run () {
	pipenv run python .
}

