# -*- coding: utf-8 -*-

import io
from PIL import Image


def  mergePic(bg,small_images):
    # 加载大图和小?
    big_image = Image.open(io.BytesIO(bg))  # 确保大图? RGBA 模式

    # 获取大图尺寸
    big_width, big_height = big_image.size  # 预计大图宽度? 345

    # 设置???的小图区域宽度和目标????
    final_width = 130  # 目标宽度
    small_width, small_height = small_images[0].size

    # 将三张小图水平拼接在??
    combined_width = 3 * small_width# 拼接后的总宽?
    combined_height = small_height # 拼接后的总高?

    # 创建???新的图像用于拼接三张小?
    combined_image = Image.new("RGBA", (combined_width, combined_height))
    x_offset = 0
    for small_image in small_images:
        # 创建???白色背景图?
        white_background = Image.new("RGBA", small_image.size, (255, 255, 255, 255))  # 白色背景
        # 将小图粘贴到白色背景?
        white_background.paste(small_image, (0, 0), small_image)  # 使用小图? alpha 通道
        combined_image.paste(white_background, (x_offset, 0))  # 将处理后的小图粘贴到拼接图像?
        x_offset += small_width

    # 缩放拼接好的小图到目标宽? 130 像素，保持高度比?
    new_height = int(combined_height * (final_width / combined_width))
    resized_combined_image = combined_image.resize((final_width, new_height), Image.LANCZOS)  # 使用 LANCZOS 代替 ANTIALIAS

    # 创建???黑色背景的新图像，宽度与大图相同，高度为小图区域高?
    black_background = Image.new("RGBA", (big_width, new_height), (0, 0, 0, 255))  # 黑底

    # 将缩放后的拼接图像粘贴到黑底背景上，并水平居?
    x_offset =0 # 计算居中位置
    black_background.paste(resized_combined_image, (x_offset, 0), resized_combined_image)

    # 创建???新的图像用于拼接大图和黑底小图区域
    final_image_height = big_height + new_height
    final_image = Image.new("RGBA", (big_width, final_image_height), (255, 255, 255, 0))  # 透明背景，RGBA 模式以支持????

    # 将大图粘贴到???图像的上方
    final_image.paste(big_image, (0, 0))

    # 将黑底小图区域粘贴到大图下方
    final_image.paste(black_background, (0, big_height))

    return final_image

def  wordprocess(file):
    # 加载原始图片
    original_image = Image.open(io.BytesIO(file))
    # 获取原始图片的尺寸
    width, height = original_image.size

    # 创建一个新的白色背景图片，尺寸为 35x80
    new_width = width+12
    # new_image = Image.new("RGBA", (new_width, height), color=(255, 255, 255))
    new_image = Image.new("RGBA", (new_width, height), color=(255, 255, 255,0))
    # 将原图粘贴到新图片的顶部
    new_image.paste(original_image, (10, 0))
    # 保存新的图片
    return new_image
