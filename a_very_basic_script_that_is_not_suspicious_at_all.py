from PIL import Image, ImageSequence
import numpy as np

import threading
import queue
import random


def worker() -> None:
    while True:
        temp_tuple = q.get()
        if temp_tuple is None:
            break
        frame_id, frame = temp_tuple

        slice_arr(frame_id, frame)
        print(str(frame_id) + " is done.")
        q.task_done()


def slice_arr(frame_id: int, frame: Image) -> None:
    """Slices the frame array and calls paint() with the randomly selected slice."""
    frame_arr = np.array(frame)

    line_start = random.randrange(0, 320)
    line_arr = frame_arr[line_start : line_start + 30]

    frame_arr[line_start : line_start + 30] = paint(line_arr)

    frame = Image.fromarray(frame_arr)

    modified_frames[frame_id] = frame


def paint(line_arr: np.ndarray) -> np.ndarray:
    """Creates a mask from the color channels for the color green (0, 254, 0) in the original gif.
    Then paints the green area a randomly selected color from the color list."""

    if len(np.shape(line_arr)) != 3:
        return line_arr

    red_channel = line_arr[:, :, 0]
    green_channel = line_arr[:, :, 1]
    blue_channel = line_arr[:, :, 2]
    alpha_channel = line_arr[:, :, 3]

    mask = (
        (red_channel == 0)
        & (green_channel == 254)
        & (blue_channel == 0)
        & (alpha_channel == 255)
    )
    random_color = random.choice(colors)
    line_arr[mask] = random_color

    return line_arr


# a chosen set of colors in RGBA form
colors = [
    (252, 3, 3, 255),
    (252, 94, 3, 255),
    (252, 127, 3, 255),
    (227, 252, 3, 255),
    (144, 252, 3, 255),
    (3, 252, 194, 255),
    (3, 177, 252, 255),
    (3, 15, 252, 255),
    (119, 3, 252, 255),
    (210, 3, 252, 255),
    (252, 3, 181, 255),
    (252, 3, 90, 255),
    (252, 3, 57, 255),
]

gif = Image.open("./very_trustworthy.gif")

q = queue.Queue()

# filling the queue with the frames of the original gif
frame_id = 0
for frame in ImageSequence.Iterator(gif):
    frame.info["duration"] //= 4

    q.put((frame_id, frame.copy()))
    frame_id += 1

# initializing the list for the modified frames, they will be inserted using their frame ids as indices
modified_frames = [frame[1] for frame in list(q.queue.copy())]

threads = []
thread_count = 30

for _ in range(thread_count):
    t = threading.Thread(target=worker)
    threads.append(t)
    t.start()
    print("Started: %s" % t)


# block until all tasks are done
q.join()

# stop workers
for _ in threads:
    q.put(None)

# kill all threads
for t in threads:
    t.join()

# saving the new gif
modified_frames[0].save(
    "new_trustworthy.gif",
    save_all=True,
    append_images=modified_frames[1:],
    optimize=False,
    duration=40,
    loop=0,
)
