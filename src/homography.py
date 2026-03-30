import numpy as np
import cv2


def homo(points):
    points = np.asarray(points, dtype=np.float64)
    ones = np.ones((len(points), 1), dtype=np.float64)
    return np.hstack([points, ones])


def cart(hpoints):
    hpoints = np.asarray(hpoints, dtype=np.float64)
    z = hpoints[:, 2:3]
    z = np.where(np.abs(z) < 1e-8, 1e-8, z)
    return hpoints[:, :2] / z


def apply_homography(points, H):
    points_h = homo(points)
    transformed = (H @ points_h.T).T
    return cart(transformed)


def normalize_points(points):
    points = np.asarray(points, dtype=np.float64)
    centroid = points.mean(axis=0)
    shifted = points - centroid
    mean_dist = np.mean(np.linalg.norm(shifted, axis=1)) + 1e-8
    scale = np.sqrt(2.0) / mean_dist

    T = np.array(
        [
            [scale, 0.0, -scale * centroid[0]],
            [0.0, scale, -scale * centroid[1]],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )

    normalized = apply_homography(points, T)
    return normalized, T


def dlt_homography(src_points, dst_points):
    src_points = np.asarray(src_points, dtype=np.float64)
    dst_points = np.asarray(dst_points, dtype=np.float64)

    if len(src_points) < 4:
        raise ValueError("DLT necesita al menos 4 pares de puntos")

    src_norm, T_src = normalize_points(src_points)
    dst_norm, T_dst = normalize_points(dst_points)

    A = []
    for (x, y), (xp, yp) in zip(src_norm, dst_norm):
        A.append([-x, -y, -1, 0, 0, 0, x * xp, y * xp, xp])
        A.append([0, 0, 0, -x, -y, -1, x * yp, y * yp, yp])
    A = np.asarray(A, dtype=np.float64)

    _, _, vt = np.linalg.svd(A)
    H = vt[-1].reshape(3, 3)
    H = np.linalg.inv(T_dst) @ H @ T_src
    H /= H[2, 2]
    return H


def compute_reprojection_distances(H, src_points, dst_points):
    projected = apply_homography(src_points, H)
    return np.linalg.norm(projected - dst_points, axis=1)


def compute_inliers(H, src_points, dst_points, thresh=5.0):
    dist = compute_reprojection_distances(H, src_points, dst_points)
    return dist < thresh


def ransac_homography(src_points, dst_points, num_iters=3000, thresh=5.0, random_seed=0):
    src_points = np.asarray(src_points, dtype=np.float64)
    dst_points = np.asarray(dst_points, dtype=np.float64)

    if len(src_points) < 4:
        raise ValueError("RANSAC necesita al menos 4 pares de puntos")

    rng = np.random.default_rng(random_seed)
    best_H = None
    best_mask = np.zeros(len(src_points), dtype=bool)

    for _ in range(num_iters):
        idx = rng.choice(len(src_points), size=4, replace=False)
        try:
            H = dlt_homography(src_points[idx], dst_points[idx])
        except np.linalg.LinAlgError:
            continue

        mask = compute_inliers(H, src_points, dst_points, thresh=thresh)
        if mask.sum() > best_mask.sum():
            best_H = H
            best_mask = mask

    if best_H is None or best_mask.sum() < 4:
        raise RuntimeError("RANSAC no encontro una homografia valida")

    H_refined, _ = cv2.findHomography(
        src_points[best_mask].astype(np.float32),
        dst_points[best_mask].astype(np.float32),
        method=0,
    )
    H_refined /= H_refined[2, 2]
    return H_refined, best_mask

