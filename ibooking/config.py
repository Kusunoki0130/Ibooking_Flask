# 默认自习室开始开放时间
start_time_default = 7

# 默认自习室开放持续时间
persist_time_default = 15

# 默认用户最长占用作为时间
book_persist_time_max = 4

# 签到距离限制
sign_distance = 100

# 预约开始前 inform_before_start 分钟邮件提醒
inform_before_start = 15

# 预约开始后 inform_after_start 分钟邮件提醒
inform_after_start = 10

# 预约开始后 sign_allowed_after_start 分钟内允许签到
sign_allowed_after_start = 15


# 延迟 10 分钟未签到提醒消息
msg_minute_10 = """
您在 Ibooking 上有未签到的预约，请尽快进行签到，或者取消预约，否则 5 分钟后将记录违纪
"""

# 延迟 15 分钟未签到提醒消息
msg_minute_15 = """
您在 Ibooking 上有未签到的预约，并已记录一次违约
"""

# 预约开始前 15 分钟签到提醒
msg_minute_45 = """
您在 Ibooking 上有未签到的预约，自习将在 15 分钟后开始，请您尽快进行签到
"""
