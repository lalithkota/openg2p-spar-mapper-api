#!/usr/bin/env python3

# ruff: noqa: I001

from openg2p_spar_mapper_api.app import Initializer

from openg2p_fastapi_common.ping import PingInitializer

main_init = Initializer()
PingInitializer()

app = main_init.return_app()

if __name__ == "__main__":
    main_init.main()
