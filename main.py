#!/usr/bin/env python3

# ruff: noqa: I001

from src.openg2p_spar_mapper_api.app import Initializer
# from openg2p_fastapi_common.ping import PingInitializer

main_init = Initializer()

main_init.main()