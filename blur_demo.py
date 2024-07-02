import cv2
import numpy as np

# 画像を読み込む
image_path = "backend/images/komei01.jpg"
mask_path = "backend/images/mask.jpg"
image = cv2.imread(image_path)
mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

# マスクを2値化する
_, binary_mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

# ぼかし処理を適用
blurred_image = cv2.GaussianBlur(image, (23, 23), 30)

# ぼかし領域をマスクで選択
blurred_area = cv2.bitwise_and(blurred_image, blurred_image, mask=binary_mask)

# マスクの反転を作成
inverse_mask = cv2.bitwise_not(binary_mask)

# 元の画像のマスク外領域を選択
original_area = cv2.bitwise_and(image, image, mask=inverse_mask)

# ぼかし領域と元の領域を合成
final_image = cv2.add(blurred_area, original_area)

# 画像を表示する
# cv2.imshow("Blurred Image", final_image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# ぼかした画像を保存する場合
cv2.imwrite("blurred_image.jpg", final_image)
