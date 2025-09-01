# import json
# import os
# import shutil
# import sys
# import time

# from deprecated.modules.http_client import request
# import pandas as pd


# sys.path.append(os.path.join(".", "src", "lib"))

# recorder = None
# starting_thread = None
# ending_thread = None
# frames = []


# def startExamination(user_name, content, level, video_option):
#     global recorder
#     global starting_thread
#     global frames

#     try:
#         response = request.get("/start_test")
#         # HTTP 상태코드 4xx, 5xx → HTTPStatusError 발생
#         response.raise_for_status()
#         return response.json()
#     except request.HTTPStatusError as err:
#         # raise_for_status()에 의해 발생 (4xx, 5xx)
#         print(f"[HTTPStatusError] {err.response.status_code} - {err.request.url}")
#         return None
#     except request.RequestError as e:
#         # DNS 실패, 연결 문제, 타임아웃 등
#         print(f"[RequestError] {e.__class__.__name__} - {e}")
#         return None
#     except Exception as ex:
#         # 알 수 없는 오류
#         print(f"[Exception] {ex}")
#         return None

#     # print(f"{user_name}의 테스트를 시작합니다")
#     # print(f"콘텐츠: {content}")
#     # print(f"난이도: level{level}")

#     # # file remove
#     # if len(os.listdir(os.path.join(".", "data", "dummy"))):
#     #     shutil.rmtree(os.path.join(".", "data", "dummy"))
#     #     os.mkdir(os.path.join(".", "data", "dummy"))
#     #     print("ACTION: Remove dummy file ")

#     # unity_content = f"{content}_Level{level}.exe" # unity content file name
#     # dummy_path = os.path.join(".", "data", "dummy", "tmp")
#     # unity_path = os.path.join(".", "data", "unity", content, f"{content}_Level{level}")

#     # # unity file copy
#     # shutil.copytree(unity_path, dummy_path)

#     # # unity file execute
#     # try:
#     #     subprocess.Popen([os.path.join(dummy_path, unity_content)])
#     # except:
#     #     error_text = "ERROR: 콘텐츠를 재생할 수 없습니다"
#     #     print(error_text)
#     #     return error_text

#     # # start screen recording
#     # # recorder = ScreenRecorder(size='480p')
#     # frames = []
#     # if video_option:
#     #     try:
#     #         pass
#     #         # starting_thread = recorder.start_recording(frames, target_name="Level")
#     #     except:
#     #         error_text_scrren = "ERROR: 영상을 녹화할 수 없습니다."
#     #         return error_text_scrren

#     #     if starting_thread is None:
#     #         return "ERROR: 재생되는 과업 프로그램을 찾을 수 없습니다"

#     return False


# def stopExamination(user_name, content, level, timestr, video_option):
#     global recorder
#     global starting_thread
#     global ending_thread
#     global frames

#     file_name = f"{user_name}_{content}_{level}_{timestr}"
#     input_path = os.path.join(".", "data", "input")
#     dummy_path = os.path.join(".", "data", "dummy", "tmp")

#     # stop screen capture
#     if video_option:
#         try:
#             recorder.stop_recording()
#             starting_thread.join()
#             ending_thread = recorder.save_video(frames, file_name, fps=20)
#         except Exception as e:
#             error_text_scrren = f"ERROR: 영상을 저장할 수 없습니다. {e}"
#             return error_text_scrren
#     frames = []

#     # program kill
#     try:
#         unity_content = f"{content}_Level{level}.exe"
#         os.system(f"taskkill /im {unity_content}")
#     except Exception as e:
#         error_text = f"ERROR: 프로그램을 종료할 수 없습니다. {e}"
#         print(error_text)
#         return error_text

#     # file save
#     try:
#         df = json2csv(os.path.join(dummy_path, f"{content}_Level{level}_Data", "data.json"))
#         df.to_csv(os.path.join(input_path, f"{file_name}.csv"), index=False)
#     except Exception as e:
#         error_text = f"ERROR: 데이터가 생성되지 않았습니다. {e}"
#         print(error_text)
#         return error_text

#     # file remove
#     try:
#         time.sleep(10)
#         shutil.rmtree(os.path.join(".", "data", "dummy"))
#         os.mkdir(os.path.join(".", "data", "dummy"))
#     except Exception as e:
#         error_text = f"ERROR: 파일을 찾을 수 없습니다. {e}"
#         print(error_text)
#         return error_text

#     return False


# def json2csv(file_name):
#     with open(file_name, "r") as json_file:
#         data = json.load(json_file)
#     df = pd.DataFrame(data)
#     return df


# def lastest_file():
#     input_path = os.path.join(".", "data", "input")

#     dir = sorted(os.listdir(input_path))
#     if len(dir) == 0:
#         print("ERROR: NO files exist in input dir")
#         return False

#     lastest_timestr = sorted([file.split("_")[-1].split(".")[0] for file in dir])[-1]
#     for file_name in dir:
#         if lastest_timestr in file_name:
#             return file_name


# if __name__ == "__main__":
#     user_name = "홍길동"
#     content = "BalanceBall"
#     level = 1
#     timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

#     startExamination(user_name, content, level, timestr)
#     time.sleep(20)
#     stopExamination(user_name, content, level, timestr)
