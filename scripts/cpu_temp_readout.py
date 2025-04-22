#!/usr/bin/env python3

def read_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_str = f.readline()
            temp_c = int(temp_str) / 1000.0
            return temp_c
    except FileNotFoundError:
        return "Temperature file not found."

if __name__ == "__main__":
    temperature = read_cpu_temp()
    print(f"CPU Temperature: {temperature}°C")

