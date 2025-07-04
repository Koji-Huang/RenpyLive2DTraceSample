

image mao = Live2D("mao_pro", update_function=osf_update_function)


label start:

    show mao
    "显示人物"

    return


screen always:
    # define at debug_ren
    add log_frame xysize (1920, 600)

init python:
    config.always_shown_screens.append("always")