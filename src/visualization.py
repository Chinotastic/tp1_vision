import os

import cv2


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def save_keypoints(image, keypoints, output_path, title):
    del title
    ensure_dir(os.path.dirname(output_path))
    draw = cv2.drawKeypoints(image, keypoints, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    cv2.imwrite(output_path, draw)


def save_matches(image1, keypoints1, image2, keypoints2, matches, output_path, title, matches_mask=None):
    del title
    ensure_dir(os.path.dirname(output_path))
    draw_params = dict(flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    if matches_mask is not None:
        draw_params["matchesMask"] = [int(x) for x in matches_mask]
    draw = cv2.drawMatches(
        image1,
        keypoints1,
        image2,
        keypoints2,
        matches,
        None,
        **draw_params,
    )
    cv2.imwrite(output_path, draw)


def save_image(image, output_path, title):
    del title
    ensure_dir(os.path.dirname(output_path))
    cv2.imwrite(output_path, image)
