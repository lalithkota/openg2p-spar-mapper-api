#!/usr/bin/env python3

# ruff: noqa: I001

from openg2p_spar_mapper_api.app import Initializer

from openg2p_fastapi_common.ping import PingInitializer

main_init = Initializer()

PingInitializer()
main_init.main()
