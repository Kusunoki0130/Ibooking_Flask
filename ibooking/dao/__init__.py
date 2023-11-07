from .models import BookingModel


class Process:
    # PROCESS STATUS:
    # 0：未开始；
    WAIT = BookingModel.PROCESS_WAIT
    # 1: 已签到，未开始；
    SIGN = BookingModel.PROCESS_SIGN
    # 2：进行中；
    RUN = BookingModel.PROCESS_RUN
    # 3：违约（未签到）；
    MARK = BookingModel.PROCESS_MARK
    # 4：提前结束；
    STOP = BookingModel.PROCESS_STOP
    # 5：取消；
    CANCEL = BookingModel.PROCESS_CANCEL
    # 6：完成
    COMPLETE = BookingModel.PROCESS_COMPLETE