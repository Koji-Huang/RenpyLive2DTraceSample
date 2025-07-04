
"""renpy    

init python:
"""
last_obj = None

def show_model_info(obj):
    global last_obj
    print("######################################")
    print("obj: ", obj)

    last_obj_dir = last_obj.__dir__() if last_obj is not None else tuple()

    for i in obj.__dir__():
        if last_obj is None or i not in last_obj_dir:
            exec(f"print('    {i}: ', obj.{i})", {}, {"obj": obj})
        else:
            if eval(f"a.{i} != b.{i}", {}, {"a": obj, "b": last_obj}):
                exec(f"print('    {i}: ', a.{i}, ' -> ', b.{i})", {}, {"a": obj, "b": last_obj})
    
    last_obj = obj


ModelInfo = list()
# define at cdd_ren
log_frame = LogFrame(ModelInfo)


def show_osf_track_data():
    # define at osf_ren
    data = FaceTraceData
    
    if bool(data) is False:
        return

    ModelInfo.clear()
    ModelInfo.append(f"time: {data['time']} | id: {data['id']} | cameraResolution: {data['cameraResolution']}")
    ModelInfo.append(f"EyeOpen: {data['leftEyeOpen']} {data['rightEyeOpen']}")
    ModelInfo.append(f"Quaternion: {data['Quaternion']}")
    ModelInfo.append(f"Rotation: {data['rotation']}")
    ModelInfo.append(f"Translation: {data['translation']}")
    ModelInfo.append(f"Eye: {data['features']['EyeLeft']} {data['features']['EyeRight']}")
    ModelInfo.append(f"EyebrowSteepness: {data['features']['EyebrowSteepnessLeft']} {data['features']['EyebrowSteepnessRight']}")

    renpy.redraw(log_frame, 0.0)


def show_mouth_track_data():
    # define at pymouth_ren
    data = GetMouthData

    ModelInfo.clear()
    ModelInfo.append("S: %.5f" % data[0])
    ModelInfo.append("A: %.5f" % data[1])
    ModelInfo.append("I: %.5f" % data[2])
    ModelInfo.append("U: %.5f" % data[3])
    ModelInfo.append("E: %.5f" % data[4])
    ModelInfo.append("O: %.5f" % data[5])

    renpy.redraw(log_frame, 0.0)

