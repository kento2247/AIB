import cv2


def blur_image(
    image_path, mask_path, blur_radius=30, save_path="images/blurred_image.jpg"
):
    image = cv2.imread(image_path)
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    _, binary_mask = cv2.threshold(
        mask, 127, 255, cv2.THRESH_BINARY
    )  # マスクを2値化する
    blurred_image = cv2.GaussianBlur(image, (23, 23), blur_radius)  # ぼかし処理を適用
    blurred_area = cv2.bitwise_and(
        blurred_image, blurred_image, mask=binary_mask
    )  # ぼかし領域をマスクで選択
    inverse_mask = cv2.bitwise_not(binary_mask)  # マスクの反転を作成
    original_area = cv2.bitwise_and(
        image, image, mask=inverse_mask
    )  # 元の画像のマスク外領域を選択
    final_image = cv2.add(blurred_area, original_area)  # ぼかし領域と元の領域を合成
    cv2.imwrite(save_path, final_image)  # ぼかした画像を保存する場合


def mosaic_image(
    image_path, mask_path, scale=0.04, save_path="images/mosaic_image.jpg"
):
    """
    画像にモザイク処理を適用する
    :param image_path: 入力画像のパス
    :param mask_path: マスク画像のパス
    :param scale: 縮小・拡大のスケール（0.1は10%に縮小し、その後10倍に拡大）
    :param save_path: 結果画像の保存パス
    """
    # 画像とマスクの読み込み
    image = cv2.imread(image_path)
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

    # 画像またはマスクの読み込みに失敗した場合の処理
    if image is None:
        raise FileNotFoundError(f"Error: Could not read image file '{image_path}'")
    if mask is None:
        raise FileNotFoundError(f"Error: Could not read mask file '{mask_path}'")

    # 画像のサイズを取得
    h, w = image.shape[:2]

    # マスクされた領域を抽出
    masked_image = cv2.bitwise_and(image, image, mask=mask)

    small_image = cv2.resize(
        masked_image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_LINEAR
    )
    # 縮小した画像を再拡大してモザイク効果を適用
    mosaic_image = cv2.resize(small_image, (w, h), interpolation=cv2.INTER_NEAREST)

    # モザイク領域をマスクとして作成
    mosaic_mask = cv2.inRange(mosaic_image, 0, 255)

    # 元の画像からモザイクを適用する部分を取り除く
    clear_image_part = cv2.bitwise_and(image, image, mask=mosaic_mask)
    # # モザイク領域と元の画像の統合
    result = cv2.add(clear_image_part, mosaic_image)

    cv2.imwrite(save_path, result)
    return save_path


# # 画像を読み込む
image_path = "images/komei01.jpg"
mask_path = "images/mask.jpg"
save_path = "images/blurred_image2.jpg"
# blur_image(image_path, mask_path, blur_radius=90, save_path=save_path)
mosaic_image(image_path, mask_path, scale=0.04, save_path=save_path)
