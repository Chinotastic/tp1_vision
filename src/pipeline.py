import os

import cv2
import numpy as np

from .features import (
    anms_filter,
    detect_sift_features,
    load_image,
    match_descriptors,
    points_from_matches,
)
from .homography import apply_homography, compute_reprojection_distances, ransac_homography
from .visualization import (
    compose_canvas_outline,
    ensure_dir,
    save_image,
    save_keypoints,
    save_matches,
    save_projected_polygon,
)


DEFAULT_CONFIG = {
    "max_size": 1200,
    "nfeatures": 4000,
    "contrast_threshold": 0.02,
    "edge_threshold": 10,
    "sigma": 1.6,
    "anms_keep": 700,
    "anms_robust": 0.9,
    "ratio": 0.75,
    "cross_check": True,
    "ransac_iters": 3000,
    "ransac_thresh": 5.0,
    "blend_power": 1.0,
}


def detect_features_with_anms(image, config):
    keypoints, descriptors = detect_sift_features(
        image,
        nfeatures=config["nfeatures"],
        contrast_threshold=config["contrast_threshold"],
        edge_threshold=config["edge_threshold"],
        sigma=config["sigma"],
    )
    raw_keypoints = keypoints
    raw_descriptors = descriptors
    keypoints, descriptors = anms_filter(
        keypoints,
        descriptors,
        num_keep=config["anms_keep"],
        robust_factor=config["anms_robust"],
    )
    return {
        "raw_keypoints": raw_keypoints,
        "raw_descriptors": raw_descriptors,
        "keypoints": keypoints,
        "descriptors": descriptors,
    }


def estimate_pair(image1, image2, config):
    feat1 = detect_features_with_anms(image1, config)
    feat2 = detect_features_with_anms(image2, config)

    matches = match_descriptors(
        feat1["descriptors"],
        feat2["descriptors"],
        ratio=config["ratio"],
        cross_check=config["cross_check"],
    )

    pts1, pts2 = points_from_matches(feat1["keypoints"], feat2["keypoints"], matches)
    H, inlier_mask = ransac_homography(
        pts1,
        pts2,
        num_iters=config["ransac_iters"],
        thresh=config["ransac_thresh"],
    )
    distances = compute_reprojection_distances(H, pts1, pts2)

    return {
        "feat1": feat1,
        "feat2": feat2,
        "matches": matches,
        "pts1": pts1,
        "pts2": pts2,
        "H": H,
        "inlier_mask": inlier_mask,
        "distances": distances,
    }


def compute_output_limits(images, homographies):
    corners_all = []
    for image, H in zip(images, homographies):
        h, w = image.shape[:2]
        corners = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32)
        warped = apply_homography(corners, H)
        corners_all.append(warped)

    stacked_corners = np.vstack(corners_all)
    min_xy = np.floor(stacked_corners.min(axis=0)).astype(int)
    max_xy = np.ceil(stacked_corners.max(axis=0)).astype(int)

    tx = -min_xy[0]
    ty = -min_xy[1]
    T = np.array([[1, 0, tx], [0, 1, ty], [0, 0, 1]], dtype=np.float64)
    width = int(max_xy[0] - min_xy[0])
    height = int(max_xy[1] - min_xy[1])
    return T, (width, height), corners_all


def blend_images(warped_images, warped_masks, blend_power=1.0):
    weights = []
    for mask in warped_masks:
        dist = cv2.distanceTransform(mask.astype(np.uint8), cv2.DIST_L2, 5)
        dist = dist ** blend_power
        dist[dist < 1e-6] = 0.0
        weights.append(dist)

    weights = np.stack(weights, axis=0)
    weights_sum = weights.sum(axis=0, keepdims=True)
    weights_sum[weights_sum == 0] = 1.0
    weights = weights / weights_sum

    panorama = np.zeros_like(warped_images[0], dtype=np.float32)
    for weight, image in zip(weights, warped_images):
        panorama += image.astype(np.float32) * weight[..., None]

    panorama = np.clip(panorama, 0, 255).astype(np.uint8)
    return panorama


def crop_valid_region(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ys, xs = np.where(gray > 0)
    if len(xs) == 0:
        return image
    x0, x1 = xs.min(), xs.max()
    y0, y1 = ys.min(), ys.max()
    return image[y0:y1 + 1, x0:x1 + 1]


def build_panorama(images, homographies, config):
    T, dsize, warped_corners = compute_output_limits(images, homographies)
    shifted_corners = [apply_homography(corners, T) for corners in warped_corners]

    warped_images = []
    warped_masks = []
    for image, H in zip(images, homographies):
        H_total = T @ H
        warped = cv2.warpPerspective(image, H_total, dsize)
        mask = np.ones(image.shape[:2], dtype=np.uint8) * 255
        warped_mask = cv2.warpPerspective(mask, H_total, dsize) > 0
        warped_images.append(warped)
        warped_masks.append(warped_mask.astype(np.uint8))

    panorama = blend_images(warped_images, warped_masks, blend_power=config["blend_power"])
    panorama = crop_valid_region(panorama)
    return panorama, warped_images, warped_masks, {
        "translation": T,
        "canvas_size": dsize,
        "warped_corners": shifted_corners,
    }


def run_triplet(image_paths, anchor_index=1, output_dir=None, config=None):
    if config is None:
        config = DEFAULT_CONFIG.copy()

    images = [load_image(path, max_size=config["max_size"])[0] for path in image_paths]
    ensure_dir(output_dir or "img/outputs")

    if output_dir is not None:
        anchor_feat = detect_features_with_anms(images[anchor_index], config)
        save_keypoints(
            images[anchor_index],
            anchor_feat["raw_keypoints"],
            os.path.join(output_dir, f"features_raw_{anchor_index}.png"),
            f"Features crudas {anchor_index}",
        )
        save_keypoints(
            images[anchor_index],
            anchor_feat["keypoints"],
            os.path.join(output_dir, f"features_anms_{anchor_index}.png"),
            f"Features ANMS {anchor_index}",
        )

    homographies = [None] * len(images)
    homographies[anchor_index] = np.eye(3)
    pair_results = {}

    for idx in range(len(images)):
        if idx == anchor_index:
            continue
        result = estimate_pair(images[idx], images[anchor_index], config)
        homographies[idx] = result["H"]
        pair_results[idx] = result

        if output_dir is not None:
            save_keypoints(
                images[idx],
                result["feat1"]["raw_keypoints"],
                os.path.join(output_dir, f"features_raw_{idx}.png"),
                f"Features crudas {idx}",
            )
            save_keypoints(
                images[idx],
                result["feat1"]["keypoints"],
                os.path.join(output_dir, f"features_anms_{idx}.png"),
                f"Features ANMS {idx}",
            )
            save_matches(
                images[idx],
                result["feat1"]["keypoints"],
                images[anchor_index],
                result["feat2"]["keypoints"],
                result["matches"],
                os.path.join(output_dir, f"matches_all_{idx}_{anchor_index}.png"),
                f"Matches {idx}->{anchor_index}",
            )
            save_matches(
                images[idx],
                result["feat1"]["keypoints"],
                images[anchor_index],
                result["feat2"]["keypoints"],
                result["matches"],
                os.path.join(output_dir, f"matches_inliers_{idx}_{anchor_index}.png"),
                f"Inliers {idx}->{anchor_index}",
                matches_mask=result["inlier_mask"],
            )
            outlier_mask = (~result["inlier_mask"]).astype(np.uint8)
            save_matches(
                images[idx],
                result["feat1"]["keypoints"],
                images[anchor_index],
                result["feat2"]["keypoints"],
                result["matches"],
                os.path.join(output_dir, f"matches_outliers_{idx}_{anchor_index}.png"),
                f"Outliers {idx}->{anchor_index}",
                matches_mask=outlier_mask,
            )
            save_projected_polygon(
                images[idx],
                images[anchor_index],
                result["H"],
                os.path.join(output_dir, f"projection_{idx}_{anchor_index}.png"),
                f"Proyeccion {idx}->{anchor_index}",
            )

    panorama, warped_images, warped_masks, canvas_debug = build_panorama(images, homographies, config)

    if output_dir is not None:
        for idx, warped in enumerate(warped_images):
            save_image(warped, os.path.join(output_dir, f"warped_{idx}.png"), f"Warped {idx}")
            save_image(
                warped_masks[idx] * 255,
                os.path.join(output_dir, f"mask_{idx}.png"),
                f"Mask {idx}",
            )
        save_image(
            compose_canvas_outline(canvas_debug["canvas_size"], canvas_debug["warped_corners"]),
            os.path.join(output_dir, "canvas_outline.png"),
            "Canvas outline",
        )
        save_image(panorama, os.path.join(output_dir, "panorama.png"), "Panorama final")

    return {
        "images": images,
        "homographies": homographies,
        "pair_results": pair_results,
        "panorama": panorama,
        "warped_images": warped_images,
        "warped_masks": warped_masks,
        "canvas_debug": canvas_debug,
        "config": config,
    }
