from os import path

from pygame import image, transform, Color


class Colors:
    """一些颜色常量"""

    WHITE = Color("#FFFFFF")
    BLACK = Color("#6E7783")
    RED = Color("#E53A40")
    BLUE = Color("#30A9DE")
    YELLOW = Color("#FFCB6B")


class Assets:
    """游戏资源"""

    # 资源路径
    assets_path = path.dirname(__file__)
    assets_path = path.join(assets_path, "assets")
    audio_path = path.join(assets_path, "audio")
    image_path = path.join(assets_path, "image")

    # 图像资源
    img_logo = image.load(path.join(image_path, "logo.png"))
    img_start = image.load(path.join(image_path, "start.png"))
    img_game_win = image.load(path.join(image_path, "game-win.png"))

    # 处理过后
    surf_start = transform.smoothscale(img_start, [220, 200])
    surf_game_win = transform.smoothscale(img_game_win, [200, 200])
