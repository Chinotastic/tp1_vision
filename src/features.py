import cv2
import numpy as np


def load_image(path, max_size=None):
    image = cv2.imread(path, cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(path)

    scale = 1.0
    if max_size is not None:
        h, w = image.shape[:2]
        scale = min(1.0, float(max_size) / max(h, w))
        if scale < 1.0:
            image = cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    return image, scale


def bgr_to_rgb(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def detect_sift_features(image, nfeatures=4000, contrast_threshold=0.02, edge_threshold=10, sigma=1.6):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sift = cv2.SIFT_create(
        nfeatures=nfeatures,
        contrastThreshold=contrast_threshold,
        edgeThreshold=edge_threshold,
        sigma=sigma,
    )
    keypoints, descriptors = sift.detectAndCompute(gray, None)
    return keypoints, descriptors


def anms_filter(keypoints, descriptors, num_keep=600, robust_factor=0.9):
    if len(keypoints) <= num_keep:
        return keypoints, descriptors

    responses = np.array([kp.response for kp in keypoints], dtype=np.float64)
    points = np.array([kp.pt for kp in keypoints], dtype=np.float64)
    order = np.argsort(responses)[::-1]

    points = points[order]
    responses = responses[order]
    ordered_keypoints = [keypoints[i] for i in order]
    ordered_descriptors = descriptors[order]

    radii = np.full(len(points), np.inf, dtype=np.float64)
    for i in range(1, len(points)):
        stronger = responses[:i] > robust_factor * responses[i]
        if not np.any(stronger):
            continue
        dist2 = np.sum((points[:i][stronger] - points[i]) ** 2, axis=1)
        radii[i] = np.sqrt(dist2.min())

    keep_idx = np.argsort(radii)[::-1][:num_keep]
    keep_idx = np.sort(keep_idx)
    filtered_keypoints = [ordered_keypoints[i] for i in keep_idx]
    filtered_descriptors = ordered_descriptors[keep_idx]
    return filtered_keypoints, filtered_descriptors


def match_descriptors(des1, des2, ratio=0.75, cross_check=True):
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
    knn12 = bf.knnMatch(des1, des2, k=2)

    reverse_best = {}
    if cross_check:
        knn21 = bf.knnMatch(des2, des1, k=1)
        reverse_best = {i: matches[0].trainIdx for i, matches in enumerate(knn21) if matches}

    good_matches = []
    for candidates in knn12:
        if len(candidates) < 2:
            continue
        m, n = candidates
        if m.distance >= ratio * n.distance:
            continue
        if cross_check and reverse_best.get(m.trainIdx) != m.queryIdx:
            continue
        good_matches.append(m)

    good_matches = sorted(good_matches, key=lambda x: x.distance)
    return good_matches


def points_from_matches(keypoints1, keypoints2, matches):
    pts1 = np.float32([keypoints1[m.queryIdx].pt for m in matches])
    pts2 = np.float32([keypoints2[m.trainIdx].pt for m in matches])
    return pts1, pts2

