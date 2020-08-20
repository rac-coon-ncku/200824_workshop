import copy

if brick is not None:
    if transform is not None:
        brick = copy.deepcopy(brick)
        brick.transform(transform)
    brick_frame = brick.frame
    brick_brep = brick.shape
