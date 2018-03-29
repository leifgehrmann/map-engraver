import sys
import time

from tqdm import tqdm

from map import MapConfig
from map import Map

log_delay_default = 0.1
log_delay = 0.1
progress_bar = None


def log(*args):
    time.sleep(log_delay)
    print(*args)
    time.sleep(log_delay)


def set_log_delay(delay: float):
    global log_delay
    log_delay = delay


def reset_log_delay():
    global log_delay
    log_delay = log_delay_default


def progress_flush(progress_bar_instance):
    if progress_bar_instance is not None:
        progress_bar_instance.refresh()
        progress_bar_instance.close()


def progress_function(name, update, total):
    global progress_bar
    if progress_bar is None or progress_bar.desc is not name:
        progress_flush(progress_bar)
        progress_bar = tqdm(total=total, desc=name, file=sys.stdout)
    progress_bar.update(update)
    if progress_bar.n == total:
        progress_flush(progress_bar)
        progress_bar = None


if len(sys.argv) < 2:
    print('usage: python3 ' + sys.argv[0] + ' [mapYaml]')
    exit()

map_file = sys.argv[1]
Map(MapConfig.create_from_yaml(map_file))\
    .set_logging_function(log)\
    .set_progress_function(progress_function)\
    .prepare_map_data()\
    .draw()