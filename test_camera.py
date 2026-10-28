import cv2, time

def test(backend, name):
    cap = cv2.VideoCapture(0, backend)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    t0 = time.perf_counter()
    cap.read()
    first = time.perf_counter() - t0
    t0 = time.perf_counter()
    n = 60
    for _ in range(n):
        cap.read()
    fps = n / (time.perf_counter() - t0)
    print(f"{name}: frame đầu {first:.2f}s | {fps:.1f} fps")
    cap.release()

test(cv2.CAP_DSHOW, "DSHOW")
test(cv2.CAP_MSMF, "MSMF")