import cv2
import base64
import json
import requests
import time
from hx711 import HX711
import RPi.GPIO as GPIO

# Global weight state
previous_weight = 0
#hx = None

def setup_hx711():
    global hx
    GPIO.setmode(GPIO.BCM)
    hx = HX711(dout_pin=21, pd_sck_pin=20)
    print("this is hx" + str(hx))
    err = hx.zero()
    if err:
        raise ValueError('Tare is unsuccessful.')

    reading = hx.get_raw_data_mean()
    if reading:
        print('Data subtracted by offset but still not converted to units:',
              reading)
    else:
        print('invalid data', reading)


    input('Put known weight on the scale and then press Enter')
    reading = hx.get_data_mean()
    if reading:
        print('Mean value from HX711 subtracted by offset:', reading)
        known_weight_grams = input(
            'Write how many grams it was and press Enter: ')
        try:
            value = float(known_weight_grams)
            print(value, 'grams')
        except ValueError:
            print('Expected integer or float and I have got:',
                  known_weight_grams)

        # set scale ratio for particular channel and gain which is
        # used to calculate the conversion to units. Required argument is only
        # scale ratio. Without arguments 'channel' and 'gain_A' it sets
        # the ratio for current channel and gain.
        ratio = reading / value  # calculate the ratio for channel A and gain 128
        hx.set_scale_ratio(ratio)  # set ratio for current channel
        print('Ratio is set.')
        current_weight = hx.get_weight_mean(20)
        print("now the current value is: ", current_weight)
        
    else:
        raise ValueError('Cannot calculate mean value. Try debug mode. Variable reading:', reading)


def get_weight_difference():
    global previous_weight #, hx
    print("this is hx" + str(hx))
    current_weight1 = hx.get_weight_mean(20)
    while current_weight1 < 3.5:
        print(current_weight1)
        current_weight1 = hx.get_weight_mean(20)
        
    diff = current_weight1 - previous_weight
    previous_weight = current_weight1
    return round(diff, 2)  # rounded difference for stability

def detect_motion():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    ret, frame1 = cap.read()
    ret, frame2 = cap.read()
    min_area = 600

    while cap.isOpened():
        diff = cv2.absdiff(frame1, frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 40, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) < min_area:
                continue

            time.sleep(1)
            ret, captured_frame = cap.read()
            cap.release()
            cv2.destroyAllWindows()
            if ret:
                _, buffer = cv2.imencode('.jpg', captured_frame)
                encoded = base64.b64encode(buffer).decode('utf-8')
                return f"data:image/jpeg;base64,{encoded}"
            else:
                return "Error: Failed to capture image"

        frame1 = frame2
        ret, frame2 = cap.read()

    cap.release()
    cv2.destroyAllWindows()

def barcode_reader():
    hid = {
        4: 'a', 5: 'b', 6: 'c', 7: 'd', 8: 'e', 9: 'f', 10: 'g', 11: 'h',
        12: 'i', 13: 'j', 14: 'k', 15: 'l', 16: 'm', 17: 'n', 18: 'o', 19: 'p',
        20: 'q', 21: 'r', 22: 's', 23: 't', 24: 'u', 25: 'v', 26: 'w', 27: 'x',
        28: 'y', 29: 'z', 30: '1', 31: '2', 32: '3', 33: '4', 34: '5', 35: '6',
        36: '7', 37: '8', 38: '9', 39: '0'
    }

    hid2 = {k: v.upper() for k, v in hid.items()}

    try:
        with open('/dev/hidraw0', 'rb') as fp:
            result = ""
            shift = False
            while True:
                buffer = fp.read(8)
                for c in buffer:
                    c = int(c)
                    if c == 0:
                        continue
                    elif c == 2:
                        shift = True
                    elif c == 40:
                        return result
                    else:
                        result += hid2[c] if shift else hid.get(c, '')
                        shift = False
    except Exception as e:
        print("Barcode read error:", e)
        return ""

def test_verify_product():
    global previous_weight
    GPIO.setmode(GPIO.BCM)
    hx = HX711(dout_pin=21, pd_sck_pin=20)
    print("this is hx" + str(hx))
    err = hx.zero()
    if err:
        raise ValueError('Tare is unsuccessful.')

    reading = hx.get_raw_data_mean()
    if reading:
        print('Data subtracted by offset but still not converted to units:',
              reading)
    else:
        print('invalid data', reading)


    input('Put known weight on the scale and then press Enter')
    reading = hx.get_data_mean()
    if reading:
        print('Mean value from HX711 subtracted by offset:', reading)
        known_weight_grams = input(
            'Write how many grams it was and press Enter: ')
        try:
            value = float(known_weight_grams)
            print(value, 'grams')
        except ValueError:
            print('Expected integer or float and I have got:',
                  known_weight_grams)

        # set scale ratio for particular channel and gain which is
        # used to calculate the conversion to units. Required argument is only
        # scale ratio. Without arguments 'channel' and 'gain_A' it sets
        # the ratio for current channel and gain.
        ratio = reading / value  # calculate the ratio for channel A and gain 128
        hx.set_scale_ratio(ratio)  # set ratio for current channel
        print('Ratio is set.')
        current_weight = hx.get_weight_mean(20)
        print("now the current value is: ", current_weight)
        
    else:
        raise ValueError('Cannot calculate mean value. Try debug mode. Variable reading:', reading)

    try:
        barcode = barcode_reader()
        photo_base64 = detect_motion()
        current_weight = hx.get_weight_mean(20)
        #print(current_weight)
        #current_weight = hx.get_weight_mean(20)
        #print(current_weight)
        
        while current_weight < 3.5:
            print(current_weight)
            current_weight = hx.get_weight_mean(20)
        
        diff = current_weight - previous_weight
        previous_weight = current_weight
        weight_to_server = round(diff, 2)  # rounded difference for stability

        
        data = {
            "photo": photo_base64,
            "barcode": barcode,
            "weight": weight_to_server,
            "battery_percentage": 85
        }

        response = requests.post(
            'https://e-bag-test.replit.app/verify-product',
            headers={'Content-Type': 'application/json'},
            json=data
        )

        print("Status Code:", response.status_code)
        print("Response:", json.dumps(response.json(), indent=2))

    except Exception as e:
        print("Error in test_verify_product:", e)

if _name_ == "_main_":
    try:
        #setup_hx711()
        #global previous_weight
        GPIO.setmode(GPIO.BCM)
        hx = HX711(dout_pin=21, pd_sck_pin=20)
        print("this is hx" + str(hx))
        err = hx.zero()
        if err:
            raise ValueError('Tare is unsuccessful.')

        reading = hx.get_raw_data_mean()
        if reading:
            print('Data subtracted by offset but still not converted to units:',
                  reading)
        else:
            print('invalid data', reading)


        input('Put known weight on the scale and then press Enter')
        reading = hx.get_data_mean()
        if reading:
            print('Mean value from HX711 subtracted by offset:', reading)
            known_weight_grams = input(
                'Write how many grams it was and press Enter: ')
            try:
                value = float(known_weight_grams)
                print(value, 'grams')
            except ValueError:
                print('Expected integer or float and I have got:',
                      known_weight_grams)

            # set scale ratio for particular channel and gain which is
            # used to calculate the conversion to units. Required argument is only
            # scale ratio. Without arguments 'channel' and 'gain_A' it sets
            # the ratio for current channel and gain.
            ratio = reading / value  # calculate the ratio for channel A and gain 128
            hx.set_scale_ratio(ratio)  # set ratio for current channel
            print('Ratio is set.')
            import time
            time.sleep(0.5)
            current_weight1 = hx.get_weight_mean(20)
            print("now the current value is: ", current_weight1)
            
        else:
            raise ValueError('Cannot calculate mean value. Try debug mode. Variable reading:', reading)

        try:
            barcode = barcode_reader()
            photo_base64 = detect_motion()
            current_weight = hx.get_weight_mean(20)
            #print(current_weight)
            #current_weight = hx.get_weight_mean(20)
            #print(current_weight)
            
            while current_weight < 3.5:
                print(current_weight)
                current_weight = hx.get_weight_mean(20)
            
            diff = current_weight - previous_weight
            previous_weight = current_weight
            weight_to_server = round(diff, 2)  # rounded difference for stability

            
            data = {
                "photo": photo_base64,
                "barcode": barcode,
                "weight": weight_to_server,
                "battery_percentage": 85
            }

            response = requests.post(
                'https://e-bag-test.replit.app/verify-product',
                headers={'Content-Type': 'application/json'},
                json=data
            )

            print("Status Code:", response.status_code)
            print("Response:", json.dumps(response.json(), indent=2))

        except Exception as e:
            print("Error in test_verify_product:", e)

    except KeyboardInterrupt:
        print("Interrupted.")
    finally:
        GPIO.cleanup()
