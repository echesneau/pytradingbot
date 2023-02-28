#!/usr/bin/env bash

coverage run --source=pytradingbot -m pytest .\pytradingbot\pytradingbot\tests\
coverage html