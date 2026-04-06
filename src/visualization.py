import os

import cv2
import numpy as np


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def _write_image(output_path, image):
    image = np.asarray(image)
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)
    ok = cv2.imwrite(output_path, image)
    if not ok:
        raise IOError(f"No se pudo escribir la imagen: {output_path}")


def _palette(n):
    rng = np.random.default_rng(0)
    colors = rng.integers(40, 255, size=(max(n, 1), 3))
    return [tuple(int(c) for c in color.tolist()) for color in colors]


def _stack_side_by_side(image1, image2):
    h1, w1 = image1.shape[:2]
    h2, w2 = image2.shape[:2]
    canvas_h = max(h1, h2)
    canvas = np.zeros((canvas_h, w1 + w2, 3), dtype=np.uint8)
    canvas[:h1, :w1] = image1
    canvas[:h2, w1:w1 + w2] = image2
    return canvas, w1


def _draw_points(image, points, colors, labels=True):
    draw = image.copy()
    for idx, (point, color) in enumerate(zip(points, colors), start=1):
        x, y = np.round(point).astype(int)
        cv2.circle(draw, (x, y), 8, color, 2, lineType=cv2.LINE_AA)
        cv2.circle(draw, (x, y), 2, color, -1, lineType=cv2.LINE_AA)
        if labels:
            cv2.putText(
                draw,
                str(idx),
                (x + 10, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2,
                lineType=cv2.LINE_AA,
            )
    return draw


def compose_correspondence_image(image1, points1, image2, points2):
    points1 = np.asarray(points1, dtype=np.float64)
    points2 = np.asarray(points2, dtype=np.float64)
    colors = _palette(len(points1))
    draw1 = _draw_points(image1, points1, colors)
    draw2 = _draw_points(image2, points2, colors)
    canvas, x_offset = _stack_side_by_side(draw1, draw2)

    for p1, p2, color in zip(points1, points2, colors):
        pt1 = tuple(np.round(p1).astype(int))
        pt2 = tuple((np.round(p2).astype(int) + np.array([x_offset, 0])).tolist())
        cv2.line(canvas, pt1, pt2, color, 1, lineType=cv2.LINE_AA)

    return canvas


def compose_polygon_projection_image(image_src, image_dst, H):
    h, w = image_src.shape[:2]
    corners = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], dtype=np.float32)
    projected = cv2.perspectiveTransform(corners[None, :, :], H.astype(np.float32))[0]

    src_draw = image_src.copy()
    dst_draw = image_dst.copy()
    cv2.polylines(src_draw, [np.round(corners).astype(np.int32)], True, (0, 255, 255), 3, lineType=cv2.LINE_AA)
    cv2.polylines(dst_draw, [np.round(projected).astype(np.int32)], True, (0, 255, 255), 3, lineType=cv2.LINE_AA)

    return np.hstack([src_draw, dst_draw])


def compose_canvas_outline(canvas_size, warped_corners):
    width, height = canvas_size
    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    colors = _palette(len(warped_corners))
    for idx, (corners, color) in enumerate(zip(warped_corners, colors)):
        poly = np.round(corners).astype(np.int32)
        cv2.polylines(canvas, [poly], True, color, 3, lineType=cv2.LINE_AA)
        center = np.round(corners.mean(axis=0)).astype(int)
        cv2.putText(
            canvas,
            str(idx),
            tuple(center.tolist()),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            color,
            2,
            lineType=cv2.LINE_AA,
        )
    return canvas


def save_keypoints(image, keypoints, output_path, title):
    del title
    ensure_dir(os.path.dirname(output_path))
    draw = cv2.drawKeypoints(image, keypoints, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    _write_image(output_path, draw)


def compose_matches_image(image1, keypoints1, image2, keypoints2, matches, matches_mask=None):
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
    return draw


def save_matches(image1, keypoints1, image2, keypoints2, matches, output_path, title, matches_mask=None):
    del title
    ensure_dir(os.path.dirname(output_path))
    draw = compose_matches_image(image1, keypoints1, image2, keypoints2, matches, matches_mask=matches_mask)
    _write_image(output_path, draw)


def save_correspondences(image1, points1, image2, points2, output_path, title):
    del title
    ensure_dir(os.path.dirname(output_path))
    draw = compose_correspondence_image(image1, points1, image2, points2)
    _write_image(output_path, draw)


def save_projected_polygon(image_src, image_dst, H, output_path, title):
    del title
    ensure_dir(os.path.dirname(output_path))
    draw = compose_polygon_projection_image(image_src, image_dst, H)
    _write_image(output_path, draw)


def save_image(image, output_path, title):
    del title
    ensure_dir(os.path.dirname(output_path))
    _write_image(output_path, image)
