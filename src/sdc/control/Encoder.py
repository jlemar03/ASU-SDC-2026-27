from gpiozero import DigitalInputDevice 
import time



PIN_A = 17  # GPIO pin for encoder channel A
PIN_B = 18  # GPIO pin for encoder channel B

REVOLUTION_TIMER = 11 * 18.8 # encoder counts revolutions using 11 pulses per rev (based on gearbox ratio), so 11*18.8

TARGET_REV = 10.0 # 10 is just an arbitrary number for testing can be wtv

encoder_a = DigitalInputDevice(PIN_A, pull_up=None, active_state=True) #encoder a object
encoder_b = DigitalInputDevice(PIN_B, pull_up=None, active_state=True) #encodeer b object

def a_encoder_tick():
    global encoder_count
    if encoder_b.value == 0:  #if it's low then the motors are going forwards, so +1 count, else it's going reverse so -1 count
        encoder_count += 1
    else:
        encoder_count -= 1

encoder_a.when_activated = a_encoder_tick  # automatically calls the function when the encoder pulses

start_time = time.perf_counter()
done = False
try: 
    while True:
        revs = encoder_count / REVOLUTION_TIMER # calculate the number of revolutions based on the encoder count and the timer
        elapsed_time = time.perf_counter() - start_time
        print(f"Revolutions: {revs:7.3f} Time: {elapsed_time:7.3f} s") 
        
        if not done and revs >= TARGET_REV:  # check if the target revolutions have been reached
         print(f">>> Reached {TARGET_REV} revolutions in {elapsed_time:7.3f} s")
         done = True
        time.sleep(0.1)  # sleep for a short time to avoid flooding the pi

except KeyboardInterrupt:
            print("\n Stopped") # if we interupt it we know
                  