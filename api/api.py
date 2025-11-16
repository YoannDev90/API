from api.utils.app_config import create_app
from api.endpoints import image_gen, main, text_gen, info, misc, image_edit

app = create_app()

app.include_router(main.router)
app.include_router(info.router)
app.include_router(image_gen.router)
app.include_router(image_edit.router)
app.include_router(misc.router)
app.include_router(text_gen.router)