import pywhatkit as pwk
import pyautogui
import datetime
import logging
import time

logging.basicConfig(level=logging.INFO)

# ── Configuration ──────────────────────────────────────────
PHONE_NUMBERS = [
    "+919987311312",
    "+919876543210",
    "+911234567890",
]
MESSAGE     = "Kemcho"
SEND_HOUR   = 14
SEND_MINUTE = 42
WAIT_TIME   = 20    # seconds to wait for WhatsApp Web to load
CLOSE_TIME  = 3     # seconds before tab closes after sending
MIN_BUFFER  = 2     # minimum minutes lead time required
GAP_BETWEEN = 30    # seconds to wait between each message
# ───────────────────────────────────────────────────────────


def is_time_valid(hour: int, minute: int) -> bool:
    """Check if the scheduled time is at least MIN_BUFFER minutes away."""
    now = datetime.datetime.now()
    scheduled = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    delta_minutes = (scheduled - now).total_seconds() / 60
    return delta_minutes >= MIN_BUFFER


def send_to_one(phone: str, hour: int, minute: int):
    """Send message to a single number at the given time."""
    try:
        logging.info(f"Sending to {phone} at {hour:02d}:{minute:02d}...")

        pwk.sendwhatmsg(
            phone,
            MESSAGE,
            hour,
            minute,
            wait_time=WAIT_TIME,
            tab_close=True,
            close_time=CLOSE_TIME
        )

        # Safety net: force Enter in case pywhatkit doesn't send
        time.sleep(2)
        pyautogui.press("enter")
        logging.info(f"✅ Message sent to {phone}")

    except Exception as e:
        logging.error(f"❌ Failed to send to {phone}: {e}", exc_info=True)


def send_to_all():
    now = datetime.datetime.now()
    logging.info(f"Current time     : {now.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Scheduled time   : {SEND_HOUR:02d}:{SEND_MINUTE:02d}")
    logging.info(f"Total recipients : {len(PHONE_NUMBERS)}")

    # ── Validate base time ─────────────────────────────────
    if not is_time_valid(SEND_HOUR, SEND_MINUTE):
        logging.error(
            "Scheduled time is too soon or already passed. "
            f"Please allow at least {MIN_BUFFER} minutes buffer."
        )
        return

    # ── Send to each number, spaced GAP_BETWEEN seconds apart ──
    for index, phone in enumerate(PHONE_NUMBERS):

        # Calculate staggered time for each recipient
        base_dt  = now.replace(hour=SEND_HOUR, minute=SEND_MINUTE, second=0, microsecond=0)
        offset   = datetime.timedelta(seconds=index * GAP_BETWEEN)
        send_dt  = base_dt + offset
        cur_hour = send_dt.hour
        cur_min  = send_dt.minute

        logging.info(f"\n[{index + 1}/{len(PHONE_NUMBERS)}] Queuing {phone} → {cur_hour:02d}:{cur_min:02d}")
        send_to_one(phone, cur_hour, cur_min)

        # Wait before sending to the next person (skip wait after last one)
        if index < len(PHONE_NUMBERS) - 1:
            logging.info(f"Waiting {GAP_BETWEEN}s before next message...")
            time.sleep(GAP_BETWEEN)

    logging.info("\n✅ All messages processed!")


if __name__ == "__main__":
    send_to_all()