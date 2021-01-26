LOGGER_STR = """
1. Start time: %(start_time)s
2. End Time: %(end_time)s
3. Total exe time(hrs:min:sec): <NOT IMPLEMENTED>
4. Total contacts in input sheet (before start of job): %(total_input_user)s

<Successful>
5. Total successful sent connections: %(total_sent)s
6. Total 1st Degree (successful sent only - count): %(1st_sent)s
7. Total 2nd Degree (successful sent only - count): %(2nd_sent)s
8. Total 3rd Degree (successful sent only - count): %(3rd_sent)s

<Unsuccessful>
9. all unsuccessful/already sent/others url list: %(failure_cnt)s
"""
import traceback

def dump_log(info):
    """ Dump log data into log file
    """
    try:
        log_str = LOGGER_STR%dict(info)
        with open("connection_request_report.txt", 'w') as fp:
            fp.write(str(log_str))
    except Exception as e:
        print("Failed to dump log data into file...")
        print(" E = ", e)
