from aiogram import Router


def setup_routers() -> Router:
    from . import start
    from . import register
    from . import profile
    from . import join_request
    from . import menu_hand

    router = Router()

    router.include_router(start.router)
    router.include_router(register.router)
    router.include_router(profile.router)
    router.include_router(join_request.router)
    router.include_router(menu_hand.router)

    return router
