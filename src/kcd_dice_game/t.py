from kcd_dice_game.utils.config import Config


def main():
    print("ok")
    cfg = Config()
    print(cfg.get("camera.camera_index"))


if __name__ == "__main__":
    main()
