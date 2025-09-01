# import cv2
# import numpy as np
# import pyautogui

# import time

# import pygetwindow as gw
# import threading
# import os
# from tqdm import tqdm


# class ScreenRecorder:
#     def __init__(self, size="720p") -> None:
#         self.width = 1280
#         self.height = 720
#         if size == "1080p":
#             self.width = 1920
#             self.height = 1080
#         if size == "480p":
#             self.width = 640
#             self.height = 480

#         self.__running = False
#         self.__rendering = False

#         self.video_folder = os.path.join("data", "video")
#         if not os.path.exists(self.video_folder):
#             os.mkdir(self.video_folder)

#     def _start_recording(self, frames, window) -> None:
#         self.__running = True
#         left, top, width, height = window.left, window.top, window.width, window.height

#         while self.__running:
#             # img = pyautogui.screenshot(region=(left, top, width, height))
#             # frame = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
#             # time.sleep(1/60)
#             frame = cv2.resize(frame, (self.width, self.height))
#             frames.append(frame)
#             # cv2.imshow('frame', frame)
#             if cv2.waitKey(1) == 27:
#                 break
#         # cv2.destroyAllWindows()

#     def start_recording(self, frames, target_name="Level"):
#         print("영상 녹화 중")
#         time.sleep(10)  # 컨텐츠 재생 전까지 기다리기
#         all_title = gw.getAllTitles()
#         title = [file for file in all_title if (target_name in file)]
#         if not title:
#             return None

#         window = gw.getWindowsWithTitle(title[0])[0]
#         thread = threading.Thread(target=self._start_recording, args=[frames, window])
#         thread.start()
#         return thread

#     def _save_video(self, frames, video_name, fps):
#         fourcc = cv2.VideoWriter_fourcc(*"VP80")
#         out = cv2.VideoWriter(os.path.join(self.video_folder, f"{video_name}.webm"), fourcc, fps, (self.width, self.height))
#         # for img in tqdm(frames):
#         for img in frames:
#             img = cv2.resize(img, (self.width, self.height))
#             out.write(img)

#         out.release()
#         print("영상 저장이 완료되었습니다.")

#     def save_video(self, frames, video_name="demo", fps=20):
#         print("영상 저장 중")
#         thread = threading.Thread(target=self._save_video, args=[frames, video_name, fps])
#         thread.start()
#         return thread

#     def stop_recording(self) -> None:
#         self.__running = False


# if __name__ == "__main__":
#     # recorder = ScreenRecorder()
#     frames = []
#     strat_thread = None
#     if strat_thread is None:
#         print("프로그램 확인 불가")
#         exit()

#     time.sleep(10)
#     # recorder.stop_recording()
#     # strat_thread.join()
#     # stop_thread = recorder.save_video(frames, "v1", 60)
#     # stop_thread.join()
