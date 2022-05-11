from openbb_terminal.core.log.collection import log_sender


def test_queue_str(tmp_path):
    log_sender.QueueItem(tmp_path).__str__()


def test_sender_settings(settings):
    value = log_sender.LogSender(settings).settings
    assert value is not None


def test_sender_fails(settings):
    value = log_sender.LogSender(settings).fails
    assert value is not None


def test_sender_queue(settings):
    value = log_sender.LogSender(settings).queue
    assert value is not None
